import sys
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

Q_TODO = Query(PY, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FUNGSI = Query(PY, "(function_definition name: (identifier) @nama) @fungsi")
BATAS_BARIS = 30

def error_pertama(node):
    # Turun ke child pertama yang membawa error sampai ke node paling dalam.
    # Jangan berhenti di ERROR pertama: ERROR luar bisa membungkus kode yang sah
    # sejak baris 1 (lihat uji/rusak.py), padahal salahnya ada di dalam.
    for child in node.children:
        if child.has_error or child.is_missing:
            return error_pertama(child)
    return node


def cek_file(path):
    tree = parser.parse(path.read_bytes())

    # Fitur 1: komentar TODO/FIXME (sudah jadi)
    todo = QueryCursor(Q_TODO).captures(tree.root_node).get("c", [])
    for node in sorted(todo, key=lambda n: n.start_byte):
        print(f"{path}:{node.start_point[0] + 1}: {node.text.decode(errors='replace').strip()}")

    # Fitur 2: fungsi lebih dari 30 baris, dihitung dari baris def sampai baris
    # terakhir body. Fungsi di dalam kelas dan fungsi bersarang ikut dihitung.
    for _, cap in QueryCursor(Q_FUNGSI).matches(tree.root_node):
        fungsi = cap["fungsi"][0]
        jumlah = fungsi.end_point[0] - fungsi.start_point[0] + 1
        if jumlah > BATAS_BARIS:
            nama = cap["nama"][0].text.decode(errors="replace")
            print(f"{path}:{fungsi.start_point[0] + 1}: fungsi {nama} {jumlah} baris")

    # Fitur 3: file yang pohonnya mengandung error
    if tree.root_node.has_error:
        rusak = error_pertama(tree.root_node)
        jenis = "MISSING" if rusak.is_missing else "ERROR"
        print(f"{path}:{rusak.start_point[0] + 1}: sintaks rusak ({jenis})")

LEWATI = {".git", ".venv", "venv", "node_modules", "__pycache__"}

for path in sorted(Path(sys.argv[1]).rglob("*.py")):
    if not LEWATI.intersection(path.parts):
        cek_file(path)
