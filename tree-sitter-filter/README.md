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

## Highlight (Tugas 5)

`tree-sitter init-config` membuat `~/.config/tree-sitter/config.json`. Isi `parser-directories` dengan folder
induk repo ini (folder yang berisi `tree-sitter-filter/`). Theme bawaan memberi `number` dan `constant.builtin`
warna yang sama persis (94 tebal), dan `operator` sewarna dengan tanda kurung (239), jadi angka dan boolean
tidak bisa dibedakan. Bagian theme diubah menjadi:

```json
"constant.builtin": { "bold": true, "color": 166 },
"punctuation.bracket": 244,
"punctuation.delimiter": 244
```

| Token | Capture | Warna |
| --- | --- | --- |
| `and` `or` `not` `in` `contains` | `@keyword` | 56 ungu |
| `=` `!=` `>` `<` `>=` `<=` | `@operator` | 239 tebal |
| `(` `)` `,` | `@punctuation.*` | 244 abu terang |
| nama field | `@property` | 124 merah |
| string | `@string` | 28 hijau |
| angka | `@number` | 94 tebal coklat |
| `true` `false` | `@constant.builtin` | 166 tebal oranye |

Output berwarna ada di `log/5_theme_baru.txt` (kode ANSI lewat `cat -v`) dan `log/5_highlight.html`.
