# Tree-sitter Part 1 (PLP Praktikum)

Ghaisan Khoirul Badruzaman, 251524048, 2B D4 Teknik Informatika Polban.
Tugas awal tree-sitter dari Pak Joe Lian Min (Programming Language Pragmatics).

| Folder / file | Isi |
| --- | --- |
| `setup/` | Uji cepat bagian 4 dan versi tool yang dipakai |
| `tugas1-3/` | Tugas 1-3: skrip Python, file `.scm`, output `.txt` |
| `tree-sitter-filter/` | Tugas 4-5: grammar DSL filter, `test/corpus/`, `queries/highlights.scm` |
| `cek/` | Tugas 6: `cek.py` dan README cara menjalankan |
| `laporan.md` | Laporan singkat, kendala, catatan penggunaan AI |
| `proposal-draft.md` | Draf proposal proyek (bagian 9) |
| `proposal/` | Uji coba query aturan 1 dan 2 untuk proposal |

## Ringkasan hasil

| Tugas | Hasil |
| --- | --- |
| 1 | Pohon ditebak dulu (`t1_perkiraan.txt`), lalu dibandingkan dengan output; `ERROR` dari kode rusak |
| 2 | `jelajah.py` dan versi `TreeCursor` identik pada `fa.py` 207 baris |
| 3 | Query fungsi + parameter, `print`, import, docstring cocok dengan hitungan manual `contoh.py` |
| 4 | `tree-sitter test` 10/10 lulus, `in_expression`, `contains_expression`, pengayaan `ke_sql.py` |
| 5 | 26 token `contoh.filter` punya capture dan warna berbeda per jenis |
| 6 | `cek.py` di psf/requests cocok 63/63 dengan pembanding tokenize + ast, plus dukungan JavaScript |

## Lingkungan

```bash
python3 -m venv .venv
.venv/bin/pip install tree-sitter tree-sitter-python tree-sitter-javascript
npm install -g tree-sitter-cli
```

Versi yang dipakai ada di `setup/versi.txt`. Catatan: materi ditulis untuk API 0.25, yang terpasang py-tree-sitter 0.26.1 dan CLI 0.27.2.
