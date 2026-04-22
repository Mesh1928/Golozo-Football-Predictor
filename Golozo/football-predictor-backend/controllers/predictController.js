const fs = require('fs');
const path = require('path');

const getPrediction = (req, res) => {
    try {
        const dataPath = path.join(__dirname, '..', 'data.json');
        const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        res.json(data);
    } catch (err) {
        console.error('Error reading data:', err);
        res.status(500).json({ error: 'Failed to load data' });
    }
};

module.exports = { getPrediction };
