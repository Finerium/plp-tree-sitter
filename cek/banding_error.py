"""Fitur 3 di kode nyata: bandingkan has_error tree-sitter dengan ast.parse (parser asli Python).
Pakai: python banding_error.py <folder>"""
import ast
import sys
import warnings
from pathlib import Path

import tree_sitter_python as tspython
from tree_sitter import Language, Parser

warnings.simplefilter("ignore")  # SyntaxWarning escape string di file uji CPython
parser = Parser(Language(tspython.language()))
akar = Path(sys.argv[1])
semua = sorted(akar.rglob("*.py"))
ts, py = set(), set()
for f in semua:
    isi = f.read_bytes()
    if parser.parse(isi).root_node.has_error:
        ts.add(f)
    try:
        ast.parse(isi)
    except (SyntaxError, ValueError):
        py.add(f)
print(f"{len(semua)} file, error menurut tree-sitter {len(ts)}, menurut ast.parse {len(py)}, sama {len(ts & py)}")
for judul, kumpulan in [("keduanya", ts & py), ("tree-sitter saja", ts - py), ("ast.parse saja", py - ts)]:
    for f in sorted(kumpulan):
        print(f"  {judul}: {f.relative_to(akar)}")
