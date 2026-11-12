# tree-sitter-filter

Grammar DSL filter untuk kotak pencarian lanjutan di halaman admin (Tugas 4-5), contoh:
`status in ("open", "pending") and (priority > 2 or owner = "budi") and not archived = true`.

```bash
tree-sitter generate          # grammar.js -> src/parser.c
tree-sitter parse contoh.filter
tree-sitter test              # test/corpus/dasar.txt
tree-sitter highlight contoh.filter
```

Riwayat pembangunan grammar per langkah (4a-4f) ada di git log, output tiap langkah di `log/`.
