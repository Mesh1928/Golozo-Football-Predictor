const mysql = require('mysql2');

const db = mysql.createConnection({
    host: process.env.MYSQLHOST || 'localhost',
    user: process.env.MYSQLUSER || 'root',
    password: process.env.MYSQLPASSWORD || '2468goku',
    database: process.env.MYSQLDATABASE || 'GolozoDB',
    port: process.env.MYSQLPORT || 3306
});

db.connect((err) => {
    if (err) {
        console.error('Database connection failed:', err);
    } else {
        console.log('Connected to MySQL!');
    }
});

const getPrediction = (req, res) => {
    const query = "SELECT team, opponent, date, predicted_target FROM matches WHERE venue_code = 1 AND date >= '2026-04-22' ORDER BY date ASC LIMIT 20";
    db.query(query, (err, results) => {
        if (err) {
            console.error('Query error:', err);
            res.status(500).json({ error: 'Database query failed' });
        } else {
            res.json(results);
        }
    });
};

module.exports = { getPrediction };
