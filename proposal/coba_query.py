# Uji rancangan query proposal: python coba_query.py <file.js> <query.scm>
import sys
import tree_sitter_javascript as tsjs
from tree_sitter import Language, Parser, Query, QueryCursor

JS = Language(tsjs.language())
tree = Parser(JS).parse(open(sys.argv[1], "rb").read())
for _, cap in QueryCursor(Query(JS, open(sys.argv[2]).read())).matches(tree.root_node):
    sql = cap["sql"][0]
    print(f"{sys.argv[1]}:{sql.start_point[0] + 1}: {sql.text.decode()}")
