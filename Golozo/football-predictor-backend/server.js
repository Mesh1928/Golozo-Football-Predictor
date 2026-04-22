const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const predictController = require('./controllers/predictController');

const app = express();
const PORT = 5001;

app.use(cors());
app.use(bodyParser.json());

app.get('/api/predict', predictController.getPrediction);

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
