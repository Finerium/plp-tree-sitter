import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

tree = parser.parse(open(sys.argv[1], "rb").read())
pola = open(sys.argv[2]).read()

for _, cap in QueryCursor(Query(PY, pola)).matches(tree.root_node):
    nama = cap["nama"][0].text.decode()
    # tanda * dan / di daftar parameter adalah node bernama (keyword_separator,
    # positional_separator), jadi named_child_count saja kelebihan satu
    jumlah = sum(1 for c in cap["params"][0].named_children
                 if c.type not in ("keyword_separator", "positional_separator"))
    print(nama, jumlah)
