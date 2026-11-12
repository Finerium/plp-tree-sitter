// harus terdeteksi
db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);
models.sequelize.query(`SELECT * FROM Users WHERE email = '${req.body.email}'`);
db.query("SELECT * FROM users WHERE name = '" + req.query.name + "'");

// tidak boleh terdeteksi
db.query("SELECT * FROM users WHERE id = $1", [req.params.id]);
db.query(`SELECT * FROM users`);
logger.info(`user ${id} login`);
