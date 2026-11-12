"""Pengayaan Tugas 4: DSL filter -> klausa WHERE SQL dengan parameter (?).

Nilai tidak pernah digabung ke string SQL, selalu lewat params, jadi aman dari
SQL injection. Nama kolom dijamin aman oleh grammar (regex identifier).

Pakai: python ke_sql.py 'status = "open" and priority > 2'
Tanpa argumen: menjalankan self-check ke SQLite in-memory.
"""
import sqlite3
import sys

import tree_sitter_filter
from tree_sitter import Language, Parser

parser = Parser(Language(tree_sitter_filter.language()))
OPERATOR = {"=": "=", "!=": "<>", ">": ">", "<": "<", ">=": ">=", "<=": "<="}


def nilai(node):
    teks = node.text.decode()
    if node.type == "string":
        return teks[1:-1]
    if node.type == "number":
        return float(teks) if "." in teks else int(teks)
    return 1 if teks == "true" else 0  # boolean, SQLite tidak punya tipe boolean


def kolom(node):
    # customer.city -> "customer"."city"
    return ".".join(f'"{bagian}"' for bagian in node.text.decode().split("."))


def ke_sql(node, params):
    f = node.child_by_field_name
    if node.type in ("query", "parenthesized"):
        return ke_sql(node.named_children[0], params)
    if node.type == "comparison":
        params.append(nilai(f("value")))
        return f"{kolom(f('field'))} {OPERATOR[f('operator').text.decode()]} ?"
    if node.type == "in_expression":
        isi = node.children_by_field_name("value")
        params.extend(nilai(v) for v in isi)
        return f"{kolom(f('field'))} IN ({', '.join('?' * len(isi))})"
    if node.type == "contains_expression":
        cari = nilai(f("value")).replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        params.append(f"%{cari}%")
        return f"{kolom(f('field'))} LIKE ? ESCAPE '\\'"
    if node.type in ("and_expression", "or_expression"):
        kata = "AND" if node.type == "and_expression" else "OR"
        return f"({ke_sql(f('left'), params)} {kata} {ke_sql(f('right'), params)})"
    if node.type == "not_expression":
        return f"NOT {ke_sql(f('operand'), params)}"
    raise ValueError(f"node {node.type} belum didukung")


def terjemahkan(teks):
    tree = parser.parse(teks.encode())
    if tree.root_node.has_error:
        raise ValueError(f"filter tidak valid: {teks}")
    params = []
    return ke_sql(tree.root_node, params), params


def cek():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE tiket (id, status, priority, owner, title, archived)")
    db.executemany("INSERT INTO tiket VALUES (?, ?, ?, ?, ?, ?)", [
        (1, "open", 3, "budi", "invoice maret", 0),
        (2, "open", 1, "sari", "login gagal", 0),
        (3, "pending", 5, "budi", "invoice_lama", 1),
        (4, "closed", 4, "andi", "100% selesai", 0),
    ])

    def id_hasil(teks):
        where, params = terjemahkan(teks)
        return [r[0] for r in db.execute(f"SELECT id FROM tiket WHERE {where} ORDER BY id", params)]

    assert id_hasil('status = "open" and (priority > 2 or owner = "budi")') == [1]
    # and lebih kuat: id=2 or (id=1 and priority=5) -> [2]; kalau salah kelompok hasilnya []
    assert id_hasil("id = 2 or id = 1 and priority = 5") == [2]
    assert id_hasil('status in ("open", "pending", "hold")') == [1, 2, 3]
    assert id_hasil('title contains "invoice" and not archived = true') == [1]
    assert id_hasil('title contains "_"') == [3]  # _ bukan wildcard
    assert id_hasil('title contains "100%"') == [4]  # % bukan wildcard
    assert id_hasil('owner = "x\' OR \'1\'=\'1"') == []  # injection jadi nilai biasa
    try:
        terjemahkan("title contains 5")
        raise AssertionError("filter rusak harus ditolak")
    except ValueError:
        pass
    print("self-check ke_sql: semua assert lulus")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        where, params = terjemahkan(sys.argv[1])
        print("WHERE", where)
        print("params", params)
    else:
        cek()
