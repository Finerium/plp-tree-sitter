import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

kode = open(sys.argv[1], "rb").read()
pola = open(sys.argv[2]).read()
tree = parser.parse(kode)

hasil = QueryCursor(Query(PY, pola)).captures(tree.root_node)
# di py-tree-sitter 0.26 urutan node per capture tidak urut posisi, jadi diurutkan dulu
for nama, nodes in hasil.items():
    for n in sorted(nodes, key=lambda n: n.start_byte):
        print(f"@{nama}  baris {n.start_point[0] + 1}: {n.text.decode()}")
