# Versi TreeCursor dari jelajah.py (pengayaan). Output harus identik.
import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))


def jelajah(cursor, kedalaman=0):
    node = cursor.node
    if node.is_named:
        baris, kolom = node.start_point
        label = f"{cursor.field_name}: " if cursor.field_name else ""
        print("  " * kedalaman + f"{label}{node.type} [{baris + 1}:{kolom}]")
    if cursor.goto_first_child():
        while True:
            jelajah(cursor, kedalaman + 1)
            if not cursor.goto_next_sibling():
                break
        cursor.goto_parent()


with open(sys.argv[1], "rb") as f:
    tree = parser.parse(f.read())
jelajah(tree.walk())
