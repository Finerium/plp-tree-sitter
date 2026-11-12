# Laporan Tugas Awal Tree-sitter

Ghaisan Khoirul Badruzaman, 251524048, 2B D4 TI. Repo: https://github.com/Finerium/plp-tree-sitter

Lingkungan: macOS, Python 3.14.6, py-tree-sitter 0.26.1, tree-sitter-python 0.25.0, tree-sitter-javascript 0.25.0,
CLI tree-sitter 0.27.2 (`setup/versi.txt`). Semua output di bawah disalin dari terminal, versi lengkapnya ada di
file `.txt` yang disebut. Proses tiap langkah bisa dilihat di riwayat commit.

## Tugas 1. Membaca pohon

Tiga potongan (fungsi, if/else, kelas) ditebak dulu pohonnya di `t1_perkiraan.txt` dan di-commit sebelum
dijalankan (commit `64aa9f5`), baru dijalankan dengan `t1.py`. Ketiganya cocok, termasuk `string` yang punya child
`string_start`, `string_content`, `string_end` (`t1_perbandingan.txt`). `children` berisi semua token, misalnya
anak `function_definition` adalah `def`, `identifier`, `parameters`, `:`, `block`, sedangkan `named_children` hanya
`identifier`, `parameters`, `block`. Node anonim lain: `=`, `+`, `return`, `(`, `)`. Kode yang dirusak:

```
$ python t1.py potongan/p2_rusak_titikdua.py      # ":" setelah if dihapus
(module (if_statement condition: (comparison_operator (identifier) (ERROR (integer) (identifier)) (string (string_start) (string_content) (string_end))) (ERROR) consequence: (block (expression_statement (assignment left: (identifier) right: (string (string_start) (string_content) (string_end)))))))
```

Pohonnya tetap punya `if_statement`, tapi kata `else` ditelan `(ERROR)` sehingga `consequence` justru berisi body
else. Tool harus cek `has_error` dulu sebelum percaya isi pohon. Di semua percobaan Python hanya muncul `ERROR`,
`MISSING` baru muncul di JavaScript (Tugas 6).

## Tugas 2. Penjelajah node

`jelajah.py` (rekursif, `field_name_for_child(i)` dengan indeks dari `children`) dan `jelajah_cursor.py`
(pengayaan, `TreeCursor`). Diuji ke `sampel/fa.py`, skrip NFA/DFA tugas teori PLP saya sendiri (207 baris):

```
$ python jelajah.py kecil.py
module [1:0]
  expression_statement [1:0]
    assignment [1:0]
      left: identifier [1:0]
      right: integer [1:4]
$ diff <(python jelajah.py sampel/fa.py) <(python jelajah_cursor.py sampel/fa.py)
(tidak ada beda, 2321 baris)
```

Temuan: kolom di `start_point` dihitung per byte. Di baris 60 `fa.py` ada huruf `ε` (2 byte), sehingga `himp`
tercetak di kolom 70 padahal indeks karakternya 69.

## Tugas 3. Query pertama

`contoh.py` sengaja diisi kasus tepi lalu dihitung manual dulu (`t3_hitung_manual.txt`).

| Yang dicari | Manual | Query | Catatan |
| --- | --- | --- | --- |
| Fungsi dan jumlah parameter | 6 fungsi | 6 fungsi, cocok | versi pertama `cetak` = 3, manual 2 |
| `print(...)` | 4 | 4 | `grep 'print('` = 7 (ikut `log.print`, string, komentar) |
| Modul di-import | 7 | 7 | termasuk `as` dan `from . import` |
| Docstring fungsi (pengayaan) | 2 | 2 | anchor `.` supaya string di baris kedua tidak ikut |

Selisih `cetak` terjadi karena `def cetak(self, *, tebal: bool = False)` punya node bernama `keyword_separator`
untuk `*`, jadi `named_child_count` kelebihan satu. `parameter.py` sekarang melewati `keyword_separator` dan
`positional_separator`. Nama node untuk query import diambil dari output `jelajah.py` (`t3_impor_pohon.txt`).

## Tugas 4. Grammar DSL filter

Dibangun per langkah 4a sampai 4f, satu commit per langkah, output tiap langkah di `tree-sitter-filter/log/`.

```
$ tree-sitter test
  dasar:
      1. ✓ satu perbandingan string
      2. ✓ operator perbandingan dengan angka
      3. ✓ and berantai mengelompok ke kiri
      4. ✓ and lebih kuat dari or
      5. ✓ kurung mengalahkan prioritas
      6. ✓ not lebih kuat dari and, nilai boolean
      7. ✓ in dengan tiga nilai
      8. ✓ contains untuk pencarian teks
      9. ✓ identifier berawalan kata kunci tetap identifier
     10. ✓ contains dengan angka ditolak
Total parses: 10; successful parses: 10; failed parses: 0; success percentage: 100.00%; average speed: 7447 bytes/ms
```

Yang saya pelajari: conflict sudah muncul di 4b (`_expr 'and' _expr • 'and'`, asosiativitas), bukan baru di 4c.
`prec.left` tanpa angka lolos `generate` tetapi `a = 1 or b = 2 and c = 3` jadi `(a or b) and c`
(`log/4c_prec_tanpa_angka.txt`), baru benar setelah `or` diberi 1 dan `and` 2. Setelah `field(...)` ditambahkan,
tes lama yang tidak menulis field tetap lulus, karena test runner mengabaikan field kalau expected tidak menulis
field sama sekali. Expected lalu ditulis ulang dengan field, dan saya buktikan field ikut dicek dengan menukar
`left`/`right` (tes gagal, `log/4f_bukti_field_dicek.txt`). Pengayaan: semua `prec` dihapus sementara (conflict
pertama `not` vs `and`), dan `ke_sql.py` menerjemahkan filter ke `WHERE` berparameter:

```
$ python ke_sql.py 'status = "open" and (priority > 2 or owner = "budi")'
WHERE ("status" = ? AND ("priority" > ? OR "owner" = ?))
params ['open', 2, 'budi']
$ python ke_sql.py
self-check ke_sql: semua assert lulus        # SQLite in-memory, termasuk input x' OR '1'='1
```

## Tugas 5. Highlight

Mulai dari `(string) @string`, lalu capture materi. Setelah itu `status`, `title`, `in`, `contains`, kurung, dan
koma belum punya capture (`log/5_langkah4.txt`), karena pola `@property` di materi hanya untuk `comparison`. Setelah
ditambah, 26 token di `contoh.filter` semuanya punya capture. Theme bawaan `init-config` memberi `number` dan
`constant.builtin` warna yang sama (`^[[1m^[[38;5;94m2` dan `^[[1m^[[38;5;94mtrue`), jadi theme diubah:

```
$ tree-sitter highlight contoh.filter | cat -v      (potongan baris 2, sesudah theme diubah)
... ^[[38;5;124mpriority^[[0m ^[[1m^[[38;5;239m>=^[[0m ^[[1m^[[38;5;94m2^[[0m ^[[38;5;56mor^[[0m ...
... ^[[38;5;56mnot^[[0m ^[[38;5;124marchived^[[0m ^[[1m^[[38;5;239m=^[[0m ^[[1m^[[38;5;166mtrue^[[0m
```

Tabel token, capture, dan warnanya ada di `tree-sitter-filter/README.md`.

## Tugas 6. cek.py

```
$ python cek.py uji/   (sebelum pengayaan JavaScript, cek/hasil_uji.txt)
uji/panjang.py:1: fungsi panjang_35 35 baris
uji/panjang.py:71: fungsi luar 34 baris
uji/panjang.py:72: fungsi dalam 32 baris
uji/rusak.py:5: sintaks rusak (ERROR)
uji/todo.py:4: # TODO: ganti os.listdir dengan pathlib
uji/todo.py:6: # FIXME: belum menangani folder kosong
$ python cek_manual.py repo-uji/requests
== repo-uji/requests/tests/testserver/server.py
  ast.parse: OK, tidak ada error sintaks
  ast baris 139: fungsi __init__ 31 baris
== repo-uji/requests/src/requests/structures.py
  ast.parse: OK, tidak ada error sintaks

seluruh repo: cek.py 63 temuan, tokenize+ast 63 temuan
hanya di cek.py: tidak ada
hanya di pembanding: tidak ada
```

`pas_30` (tepat 30 baris) sengaja tidak dilaporkan.

Di psf/requests (37 file) ada 7 TODO, 56 fungsi panjang, 0 file rusak. Dua file acak (seed 48) dan seluruh repo
cocok dengan pembanding tanpa tree-sitter (`tokenize` untuk komentar, `ast` untuk fungsi). `server.py:139` juga
saya cek langsung, `__init__` memang dari baris 139 sampai 169. Karena requests tidak punya file rusak, fitur 3
diuji di test suite CPython 3.14 (1131 file, `hasil_cpython_test.txt`): hanya 1 dari 4 file yang ditandai
tree-sitter benar-benar rusak. Tiga lainnya sah tapi belum didukung grammar 0.25 (`Union[*args]`, default type
parameter, dedent di dalam kurung). Pengayaan JavaScript diuji di `lib/` npm 11.9.0 (110 file).

## Kendala dan cara mengatasi

| Kendala | Cara mengatasi |
| --- | --- |
| `tree-sitter init` gagal `IO error: not a terminal` | tulis `tree-sitter.json` dulu, `init` membacanya |
| `module.exports` dari materi: `ReferenceError: module is not defined in ES module scope` | CLI 0.27 membuat `package.json` ESM, pakai `export default` |
| `pip install -e .` gagal, pyproject berisi `PARSER_AUTHOR_EMAIL` | hapus placeholder email dari `pyproject.toml` |
| Sesudah itu `import tree_sitter_filter` tetap gagal | file `.pth` editable diberi flag `hidden` oleh macOS dan dilewati Python 3.14, pakai `pip install .` |
| Hasil `captures()` di py-tree-sitter 0.26 tidak urut baris | diurutkan dengan `start_byte` |
| Grammar Python 0.25 tertinggal dari Python 3.14 | dicatat sebagai batasan fitur 3 di `cek/README.md` |

## Catatan penggunaan AI

Semua tugas dikerjakan bersama Claude Code (AI coding agent) yang bekerja langsung di repo ini. Saya meminta AI
mengikuti langkah terpandu materi, menjalankan tiap langkah, dan commit per langkah. Hasil AI saya cek lewat
output, tes, dan pembanding yang tidak memakai tree-sitter.

| Tugas | Kesalahan atau kekurangan hasil AI | Bukti dan perbaikan |
| --- | --- | --- |
| 1 | Fungsi perapi S-expression versi pertama menaruh label field di baris yang salah (`(function_definition name:` lalu `(identifier)` di bawahnya), regex `[^()]*` ikut menelan `name: ` | terlihat saat output pertama dijalankan (belum di-commit), regex diganti `[^()\s]*`. Tebakan pohon dari AI sendiri cocok semua |
| 2 | Tidak ditemukan kesalahan. Kekurangannya, kolom dalam byte tidak disadari sampai dicek | `diff` dua versi kosong, posisi baris 14 dan 60 dicek manual |
| 3 | Menghitung parameter dengan `named_child_count` (mengikuti materi) memberi `cetak` = 3 | hitungan manual 2, pohon `jelajah.py` menunjukkan `keyword_separator` (commit `dc7ebfd`, `d36e47c`) |
| 4 | Menebak pohon error `title contains 5` sebagai `(query (ERROR (identifier)) (comparison ...))`, aslinya `(ERROR (identifier) (number))` | `log/4_in_contains_tes_gagal.txt`, diganti atribut `:error`. Assert di `ke_sql.py` memakai `.replace("a", "id")` sehingga `and` jadi `idnd`, ketahuan dari `ValueError` |
| 5 | Mengikuti query materi saja, `status`, `title`, `in`, `contains`, kurung, dan koma belum punya capture | `log/5_langkah4.txt` dibanding `log/5_langkah5.txt` |
| 6 | `error_pertama` berhenti di `ERROR` pertama, `uji/rusak.py` dilaporkan baris 1 padahal rusak di baris 5. AI juga sempat mengira `server.py` tidak dilaporkan, padahal output yang dibaca terpotong 60 dari 66 baris | `cek/hasil_fitur3_salah_baris.txt` dan pohon `jelajah.py`, diperbaiki turun ke error terdalam. Sejak itu hasil dibandingkan dengan skrip (`cek_manual.py`), bukan dengan mata |
