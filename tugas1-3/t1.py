import re
import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))


def rapi(sexp):
    # S-expression satu baris jadi berindentasi, supaya gampang dibandingkan
    # dengan perkiraan. ponytail: teks selain tipe node, field, dan
    # (MISSING "x") dibuang, cukup untuk potongan Tugas 1.
    baris, dalam = [], 0
    for m in re.finditer(r"(\w+: )?\(([^()\s]*(?: \"[^\"]*\")?)|\)", sexp):
        if m.group(0) == ")":
            baris[-1] += ")"
            dalam -= 1
        else:
            baris.append("  " * dalam + (m.group(1) or "") + "(" + m.group(2).strip())
            dalam += 1
    return "\n".join(baris)


kode = open(sys.argv[1], "rb").read() if len(sys.argv) > 1 else b"x = 1\n"
tree = parser.parse(kode)
print(tree.root_node)
print(rapi(str(tree.root_node)))

# langkah 5: anak langsung dari statement pertama, termasuk yang anonim
print("\nanak statement pertama:")
pertama = tree.root_node.children[0]
for c in pertama.children:
    print(" ", c.type, "bernama" if c.is_named else "anonim")
params = pertama.child_by_field_name("parameters")
if params:
    print("anak node parameters:")
    for c in params.children:
        print(" ", c.type, "bernama" if c.is_named else "anonim")
print("has_error:", tree.root_node.has_error)
