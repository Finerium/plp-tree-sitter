"""Regex ke NFA (Thompson, ditulis manual sesuai aturan slide) lalu NFA ke DFA (subset construction).

Script ini menghitung epsilon-closure dan move, menggambar NFA/DFA dengan graphviz, menulis laporan.md,
dan mengecek bahwa NFA dan DFA menerima string yang sama persis dengan regex aslinya (re.fullmatch).

Pemakaian: python3 fa.py
"""

import itertools
import os
import re
import subprocess

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = "ε"

# tiap NFA: (nama, regex di slide, regex python, alfabet, jumlah state, state final, transisi)
# penomoran state mengikuti contoh (a|b)*abb di slide: kiri ke kanan, cabang atas dulu,
# dan concatenation menggabungkan state akhir N(s) dengan state awal N(t)
SOAL = [
    ("P", "x(y)+z", "x(y)+z", "xyz", 6, 5, [
        (0, "x", 1), (1, E, 2), (2, "y", 3), (3, E, 2), (3, E, 4), (4, "z", 5)]),
    ("Q", "m | nr*", "m|nr*", "mnr", 9, 8, [
        (0, E, 1), (0, E, 3), (1, "m", 2), (3, "n", 4), (4, E, 5), (4, E, 7),
        (5, "r", 6), (6, E, 5), (6, E, 7), (2, E, 8), (7, E, 8)]),
    ("R", "(p | q)*r", "(p|q)*r", "pqr", 9, 8, [
        (0, E, 1), (0, E, 7), (1, E, 2), (1, E, 4), (2, "p", 3), (4, "q", 5),
        (3, E, 6), (5, E, 6), (6, E, 1), (6, E, 7), (7, "r", 8)]),
    ("T", "t*(u | v)", "t*(u|v)", "tuv", 9, 8, [
        (0, E, 1), (0, E, 3), (1, "t", 2), (2, E, 1), (2, E, 3), (3, E, 4), (3, E, 6),
        (4, "u", 5), (6, "v", 7), (5, E, 8), (7, E, 8)]),
    ("W", "x(y | z)+", "x(y|z)+", "xyz", 9, 8, [
        (0, "x", 1), (1, E, 2), (2, E, 3), (2, E, 5), (3, "y", 4), (5, "z", 6),
        (4, E, 7), (6, E, 7), (7, E, 2), (7, E, 8)]),
]


def himp(s):
    return "{" + ", ".join(map(str, sorted(s))) + "}" if s else "∅"


def closure(trans, s):
    hasil, tumpuk = set(s), list(s)
    while tumpuk:
        q = tumpuk.pop()
        for a, lbl, b in trans:
            if a == q and lbl == E and b not in hasil:
                hasil.add(b)
                tumpuk.append(b)
    return frozenset(hasil)


def move(trans, s, c):
    return frozenset(b for a, lbl, b in trans if a in s and lbl == c)


def subset(trans, sigma, final):
    """Subset construction dengan catatan langkah bergaya slide."""
    awal = closure(trans, {0})
    nama, urut, langkah = {awal: "A"}, [awal], [f"*ε-closure* (0) = {himp(awal)} → **A**"]
    dfa, sudah = {}, {}  # sudah: hasil move yang sudah pernah di-closure
    i = 0
    while i < len(urut):
        T = urut[i]
        kosong = []
        for c in sigma:
            m = move(trans, T, c)
            if not m:
                kosong.append(c)
                dfa[(nama[T], c)] = None
                continue
            if m in sudah:
                U = sudah[m]
                langkah.append(f"*move* [{nama[T]}, {c}] = {himp(m)} → **{nama[U]}**")
            else:
                U = closure(trans, m)
                sudah[m] = U
                if U not in nama:
                    nama[U] = chr(ord("A") + len(nama))
                    urut.append(U)
                langkah.append(f"*move* [{nama[T]}, {c}] = {himp(m)}")
                langkah.append(f"*ε-closure* ([{nama[T]}, {c}]) = *ε-closure* ({himp(m)}) = {himp(U)} → **{nama[U]}**")
            dfa[(nama[T], c)] = nama[U]
        if kosong:
            lst = " = ".join(f"*move* [{nama[T]}, {c}]" for c in kosong)
            langkah.append(f"{lst} = ∅")
        i += 1
    finals = [nama[S] for S in urut if final in S]
    return urut, nama, dfa, langkah, finals


def terima_nfa(trans, final, w):
    s = closure(trans, {0})
    for c in w:
        s = closure(trans, move(trans, s, c))
    return final in s


def terima_dfa(dfa, finals, w):
    s = "A"
    for c in w:
        s = dfa.get((s, c))
        if s is None:
            return False
    return s in finals


def dot(teks, berkas):
    subprocess.run(["dot", "-Tpng", "-Gdpi=200", "-o", os.path.join(AKAR, "gambar", berkas)],
                   input=teks.encode(), check=True)


GAYA = ('rankdir=LR; bgcolor=white; node [shape=circle fontname="Times New Roman" fontsize=16 width=0.5 fixedsize=true];'
        ' edge [fontname="Times New Roman" fontsize=16 arrowsize=0.8];'
        ' mulai [shape=none label="start" fixedsize=false fontsize=14];')


def gambar_nfa(n, nst, final, trans):
    baris = [f"digraph {n} {{ {GAYA}"]
    baris += [f'{q} [shape={"doublecircle" if q == final else "circle"}];' for q in range(nst)]
    baris.append("mulai -> 0;")
    for a, lbl, b in trans:
        # sisi balik (loop closure) dibuat tidak memengaruhi urutan kiri ke kanan
        extra = ' constraint=false' if b < a else ""
        baris.append(f'{a} -> {b} [label="{lbl}"{extra}];')
    dot("\n".join(baris) + "}", f"nfa-{n.lower()}.png")


def gambar_dfa(n, urut, nama, dfa, sigma, finals):
    baris = [f"digraph {n} {{ {GAYA}"]
    baris += [f'{nama[S]} [shape={"doublecircle" if nama[S] in finals else "circle"}];' for S in urut]
    baris.append("mulai -> A;")
    gabung = {}
    for (a, c), b in dfa.items():
        if b:
            gabung.setdefault((a, b), []).append(c)
    for (a, b), cs in gabung.items():
        baris.append(f'{a} -> {b} [label="{", ".join(cs)}"];')
    dot("\n".join(baris) + "}", f"dfa-{n.lower()}.png")


def tabel_md(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


ROMAWI = ["II", "III", "IV", "V", "VI"]
md = ["# Regex ke NFA dan NFA ke DFA", "",
      "Naskah sumber PDF, dibuat oleh `draf/fa.py`. Jangan diedit manual, ubah fa.py lalu jalankan ulang.", "",
      "## PENDAHULUAN", "", "### 1.1 Soal", "",
      "Lima regular expression dari Latihan 1 pertemuan 3 dicari contoh string-nya, lalu diubah menjadi NFA, "
      "kemudian NFA tersebut diubah menjadi DFA:", ""]
md += [f"- {n} → `{rx}`, alfabet {{{', '.join(sig)}}}" for n, rx, _, sig, *_ in SOAL]

# Latihan 1 asli: beberapa string yang dihasilkan tiap regex (dicek dengan re.fullmatch)
STRING = {"P": ["xyz", "xyyz", "xyyyz"], "Q": ["m", "n", "nr", "nrr"], "R": ["r", "pr", "qr", "pqr"],
          "T": ["u", "v", "tu", "tv"], "W": ["xy", "xz", "xyz", "xzy"]}
for n, rx, py, *_ in SOAL:
    assert all(re.fullmatch(py, w) for w in STRING[n]), n
md += ["", "### 1.2 Latihan 1: String yang Dihasilkan", ""]
md += [f"- {n} = {{{', '.join(STRING[n])}, ...}}" for n, *_ in SOAL]
md += ["", "### 1.3 Cara Pengerjaan", "",
       "- Regex ke NFA memakai aturan di slide *RegEx to NFA*: NFA untuk simbol, concatenation (state akhir N(s) "
       "digabung dengan state awal N(t)), union, Kleene closure, dan positive closure. Penomoran state mengikuti "
       "contoh (a|b)*abb di slide, dari kiri ke kanan dan cabang atas lebih dulu.",
       "- NFA ke DFA memakai *ε-closure* dan *move* seperti di slide *Conversion of an NFA to a DFA*. Kalau hasil "
       "*move* sudah pernah dihitung, *ε-closure*-nya tidak ditulis ulang.",
       "- ∅ berarti tidak ada transisi. Pada DFA, ∅ adalah dead state yang tidak digambar di diagram.",
       "- Semua NFA dan DFA dicek dengan program: untuk setiap string sampai panjang 6 atas alfabetnya, NFA dan DFA "
       "menerima string yang sama persis dengan regex aslinya.", ""]

ringkas = []
for k, (n, rx, py, sig, nst, final, trans) in enumerate(SOAL):
    urut, nama, dfa, langkah, finals = subset(trans, sig, final)
    gambar_nfa(n, nst, final, trans)
    gambar_dfa(n, urut, nama, dfa, sig, finals)
    # cek: NFA, DFA, dan regex python harus sepakat untuk semua string sampai panjang 6
    for L in range(7):
        for w in map("".join, itertools.product(sig, repeat=L)):
            r = re.fullmatch(py, w) is not None
            assert terima_nfa(trans, final, w) == r == terima_dfa(dfa, finals, w), (n, w)
    b = k + 2
    nfa_rows = [[str(q)] + [himp({t for a, l, t in trans if a == q and l == c}) for c in list(sig) + [E]]
                for q in range(nst)]
    dfa_rows = [[himp(S), f"**{nama[S]}**" if nama[S] in finals else nama[S]]
                + [dfa[(nama[S], c)] or "∅" for c in sig] for S in urut]
    md += [f"## {n} → `{rx}`", "",
           f"### {b}.1 Regex ke NFA", "",
           f"![Gambar {b}.1: NFA untuk {n} → {rx}](gambar/nfa-{n.lower()}.png)", "",
           f"Tabel {b}.1: Tabel transisi NFA {n}", "",
           tabel_md(["State"] + list(sig) + [E], nfa_rows), "",
           f"State awal 0, state final {final}.", "",
           f"### {b}.2 NFA ke DFA", ""]
    md += [f"- {x}" for x in langkah]
    md += ["", f"Tabel {b}.2: Tabel transisi DFA {n}", "",
           tabel_md(["State NFA", "State DFA"] + list(sig), dfa_rows), "",
           f"State awal A, state final {', '.join(finals)} (dicetak tebal) karena memuat state final NFA {final}.", "",
           f"![Gambar {b}.2: DFA untuk {n} → {rx}](gambar/dfa-{n.lower()}.png)", ""]
    ringkas.append([n, "`" + rx.replace("|", "\\|") + "`", str(nst), str(len(urut)), ", ".join(finals)])
    print(n, "NFA", nst, "state, DFA", len(urut), "state, final", finals)

md += ["## RINGKASAN", "", "Tabel 7.1: Ringkasan hasil konversi", "",
       tabel_md(["Nama", "Regex", "State NFA", "State DFA", "State final DFA"], ringkas), ""]
with open(os.path.join(AKAR, "laporan.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print("cek NFA = DFA = regex untuk semua string sampai panjang 6: lolos")
