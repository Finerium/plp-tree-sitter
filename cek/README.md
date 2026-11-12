# cek.py: pendeteksi TODO, fungsi panjang, dan file rusak (Tugas 6)

CLI kecil berbasis tree-sitter yang membaca semua file `.py` (dan `.js`) di sebuah folder lalu melaporkan:

1. komentar berisi `TODO` atau `FIXME` (query `comment` + `#match?`, jadi string dan nama method tidak ikut),
2. fungsi lebih dari 30 baris, dihitung dari baris `def` sampai baris terakhir body,
3. file yang pohonnya punya error, beserta baris node `ERROR`/`MISSING` paling dalam yang pertama.

## Pasang

```bash
python3 -m venv .venv
.venv/bin/pip install tree-sitter tree-sitter-python tree-sitter-javascript
```

## Jalankan

```bash
python cek.py <folder>
python cek.py uji/                      # file uji buatan sendiri
git clone --depth 1 https://github.com/psf/requests.git repo-uji/requests
python cek.py repo-uji/requests         # repo nyata
python cek_manual.py repo-uji/requests  # pembanding tanpa tree-sitter (tokenize + ast)
python banding_error.py <folder>        # bandingkan fitur 3 dengan ast.parse
```

Folder `.git`, `.venv`, `venv`, `node_modules`, dan `__pycache__` di dalam folder yang dicek dilewati.

## Contoh output (`uji/`)

```
uji/contoh.js:1: // TODO: ganti var dengan const
uji/contoh.js:5: // FIXME: belum cek NaN
uji/contoh.js:10: fungsi panjangPanah 33 baris
uji/contoh.js:45: fungsi cetak 33 baris
uji/panjang.py:1: fungsi panjang_35 35 baris
uji/panjang.py:71: fungsi luar 34 baris
uji/panjang.py:72: fungsi dalam 32 baris
uji/rusak.js:1: sintaks rusak (MISSING)
uji/rusak.py:5: sintaks rusak (ERROR)
uji/todo.py:4: # TODO: ganti os.listdir dengan pathlib
uji/todo.py:6: # FIXME: belum menangani folder kosong
```

`pas_30` (tepat 30 baris) sengaja tidak dilaporkan, `# todo` huruf kecil dan `"TODO"` di dalam string juga tidak.

## Hasil di repo nyata

| Repo | File | TODO/FIXME | Fungsi > 30 baris | File rusak | Pengecekan |
| --- | --- | --- | --- | --- | --- |
| psf/requests `3c7baaa` | 37 `.py` | 7 | 56 | 0 | 2 file acak (seed 48) dan seluruh repo sama persis dengan tokenize + ast (`hasil_cek_manual.txt`) |
| test suite CPython 3.14 | 1131 `.py` | - | - | 4 | dibandingkan dengan `ast.parse` (`hasil_cpython_test.txt`) |
| npm 11.9.0 `lib/` | 110 `.js` | 33 | 117 | 1 | file rusak dicek dengan `node --check` (`hasil_npm_js.txt`) |

## Catatan dan batasan

- Fungsi di dalam kelas dan fungsi bersarang ikut dihitung, jadi satu fungsi panjang yang berisi fungsi panjang
  muncul dua kali (`luar` dan `dalam`).
- JavaScript: yang dihitung `function`, generator, method kelas, dan arrow/function expression yang disimpan ke
  variabel. Callback anonim (`arr.map(x => ...)`) tidak punya nama, jadi tidak dilaporkan.
- Fitur 3 bergantung pada grammar, bukan pada Python atau Node. Di test suite CPython 3.14, tree-sitter-python
  0.25 menandai 3 file sah sebagai rusak (`Union[*args]`, default type parameter PEP 696, dedent di dalam kurung)
  dan tidak menangkap 3 file yang rusak karena encoding. Di npm, `base-cmd.js` ditandai rusak padahal
  `node --check` lolos: baris diawali `[` setelah `}` milik arrow function, Node menyisipkan titik koma (ASI),
  tree-sitter-javascript tidak.
