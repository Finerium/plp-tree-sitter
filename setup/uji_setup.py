import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

tree = parser.parse(b"def halo(nama):\n    return nama\n")
print(tree.root_node)  # mencetak S-expression pohon
