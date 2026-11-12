"""Pembanding untuk Tugas 6 langkah 5: pilih 2 file acak (seed 48), lalu hitung ulang
tanpa tree-sitter: grep untuk TODO/FIXME dan modul ast bawaan Python untuk panjang fungsi."""
import ast
import random
import re
import sys
from pathlib import Path

semua = sorted(p for p in Path(sys.argv[1]).rglob("*.py") if ".git" not in p.parts)
random.seed(48)
for path in random.sample(semua, 2):
    teks = path.read_text(encoding="utf-8")
    print(f"== {path}")
    for no, baris in enumerate(teks.splitlines(), 1):
        if re.search(r"TODO|FIXME", baris):
            print(f"  grep baris {no}: {baris.strip()}")
    pohon = ast.parse(teks)  # gagal kalau sintaks rusak
    print("  ast.parse: OK, tidak ada error sintaks")
    for n in ast.walk(pohon):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            panjang = n.end_lineno - n.lineno + 1
            if panjang > 30:
                print(f"  ast baris {n.lineno}: fungsi {n.name} {panjang} baris")

# Pembanding seluruh repo, juga tanpa tree-sitter: tokenize untuk komentar, ast untuk fungsi
import io
import subprocess
import tokenize

harapan = set()
for path in semua:
    teks = path.read_text(encoding="utf-8")
    for tok in tokenize.generate_tokens(io.StringIO(teks).readline):
        if tok.type == tokenize.COMMENT and re.search(r"TODO|FIXME", tok.string):
            harapan.add(f"{path}:{tok.start[0]}: {tok.string.strip()}")
    for n in ast.walk(ast.parse(teks)):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.end_lineno - n.lineno + 1 > 30:
            harapan.add(f"{path}:{n.lineno}: fungsi {n.name} {n.end_lineno - n.lineno + 1} baris")
keluaran = subprocess.run([sys.executable, "cek.py", sys.argv[1]], capture_output=True, text=True).stdout
hasil = set(keluaran.splitlines())
print(f"\nseluruh repo: cek.py {len(hasil)} temuan, tokenize+ast {len(harapan)} temuan")
print("hanya di cek.py:", sorted(hasil - harapan) or "tidak ada")
print("hanya di pembanding:", sorted(harapan - hasil) or "tidak ada")
