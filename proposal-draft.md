# Draf Proposal Proyek Tree-sitter

Ghaisan Khoirul Badruzaman (251524048, 2B D4 TI)

**1. Judul.** sqlguard: pendeteksi query SQL yang dirangkai dari string pada backend Node.js (Express).

**2. Masalah.** Di backend web enterprise, query sering dibangun dengan template string atau `+`, misalnya
`` db.query(`... WHERE email = '${req.body.email}'`) ``. Pola ini membuka SQL injection (OWASP A03), lolos dari
code review karena terlihat wajar, dan bisa ikut terbawa di kode hasil AI. Penggunanya reviewer pull request
dan tim keamanan, kegiatannya code review dan quality gate di CI.

**3. Kenapa tidak cukup dengan AI saja.** Review oleh AI hasilnya bisa beda tiap kali dijalankan, mahal kalau
dijalankan ke semua file di setiap commit, dan AI yang menulis kode belum tentu menyadari pola ini. Tool
tree-sitter memberi hasil yang sama untuk input yang sama, ribuan file per detik, dan bisa memblokir merge
lewat exit code di CI. AI tetap dipakai untuk mengusulkan aturan baru, tree-sitter yang menjalankannya. Regex
juga tidak cukup: regex tidak bisa membedakan `${}` di argumen `db.query` dengan `${}` di `logger.info`, dan
tidak paham string yang dirangkai lewat variabel di baris lain.

**4. Target.** JavaScript dan TypeScript (Express dengan `pg`, `mysql2`, `sequelize.query`, `knex.raw`), grammar
`tree-sitter-javascript` dan `tree-sitter-typescript` dari PyPI.

**5. Contoh kode.**

```js
// harus terdeteksi
db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);
db.query("SELECT * FROM users WHERE name = '" + req.query.name + "'");
var q = "SELECT name FROM Users WHERE login='" + req.body.login + "'"; db.sequelize.query(q);  // aturan 3
// tidak boleh terdeteksi
db.query("SELECT * FROM users WHERE id = $1", [req.params.id]);
db.query(`SELECT * FROM users`);
logger.info(`user ${id} login`);
```

**6. Rancangan query** (aturan 1, sudah dicoba pada `proposal/contoh.js`, hasilnya di `proposal/hasil_query.txt`):

```scheme
(call_expression
  function: (member_expression property: (property_identifier) @method)
  arguments: (arguments . (template_string (template_substitution)) @sql)
  (#match? @method "^(query|execute|raw)$"))
```

Aturan 2 sama, tetapi argumennya `(binary_expression operator: "+")`. Aturan 3 (variabel yang diisi string
rangkaian lalu dikirim ke `.query`) butuh penelusuran di Python dalam satu fungsi, tidak cukup dengan query.

**7. Bentuk output.** Laporan terminal `file:baris: aturan, potongan kode`, file JSON, dan anotasi GitHub Actions
(`::error file=...,line=...`) dengan exit code bukan nol kalau ada temuan.

**8. Cara evaluasi.** Recall diuji di dua aplikasi yang sengaja dibuat rentan: OWASP Juice Shop (TypeScript,
template string di `routes/login.ts`) dan DVNA (JavaScript, string dirangkai lewat variabel di
`core/appHandler.js`). False positive diuji di satu atau dua repo Express biasa, lalu 20 temuan dicek manual
dan dihitung berapa yang benar.

**9. Rencana kerja dan risiko.**

| Minggu | Kegiatan |
| --- | --- |
| 1 | Aturan 1 dan 2 untuk JavaScript, kasus uji benar dan salah |
| 2 | Aturan 3 (penelusuran variabel dalam satu fungsi) |
| 3 | Dukungan TypeScript, output JSON dan anotasi CI |
| 4 | Evaluasi di Juice Shop, DVNA, dan repo biasa |
| 5 | Perbaikan dari hasil evaluasi, laporan, demo |

Risiko: aliran data lintas fungsi atau file tidak terjangkau (dibatasi dalam satu fungsi), string konstan yang
dirangkai (`"SELECT " + KOLOM`) bisa jadi false positive, dan nama method tiap library berbeda (dibuat daftar
yang bisa ditambah).
