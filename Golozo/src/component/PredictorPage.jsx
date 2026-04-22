import React, { useState, useEffect } from 'react';
import axios from 'axios';
import p from './predicstyle.module.css';
import l from './loginstyle.module.css';
import { Link } from 'react-router-dom';

const PP = () => {
    const [matches, setMatches] = useState([]);
    const [selectedMatch, setSelectedMatch] = useState(null);
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');


    useEffect(() => {
        const fetchMatches = async () => {
            try {
                const response = await axios.get('https://golozo-football-predictor-production.up.railway.app/api/predict');
                if (Array.isArray(response.data)) {
                    setMatches(response.data);
                } else {
                    setError("Failed to load matches.");
                }
            } catch (error) {
                setError("Error fetching matches: " + error.message);
                console.error("Error fetching matches:", error);
            }
        };

        fetchMatches();
    }, []);

    const handleMatchSelect = (match) => {
        setSelectedMatch(match);
        setPrediction(null);
        setError("");
    };

    const handlePrediction = async () => {
        if (!selectedMatch) {
            setError("Please select a match first.");
            return;
        }

        setLoading(true);
        setError('');
        setPrediction(null);

        try {
           const { team, opponent, predicted_target } = selectedMatch;
           const predictedTarget = predicted_target;
            const isTeam1Win = predictedTarget === 1;
            const predictionText = isTeam1Win ? `${team} is predicted to win.` : `${team} is predicted to not win.`;

            setPrediction({
                team,
                opponent,
                predictionText
            });
        } catch (error) {
            setError("Error predicting match: " + error.message);
            console.error("Error predicting match:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={p.main}>
            <header className={p.header}>
                <h1 className={p.tagline}>
                    <span className={p.group1}>C<span className={p.word}>h</span>o<span className={p.word}>o</span>s<span className={p.word}>e</span></span>
                    <span style={{ margin: '0 2px' }}></span>
                    <span className={p.group2}>Y<span className={p.word}>o</span>u<span className={p.word}>r</span></span>
                    <span style={{ margin: '0 2px' }}></span>
                    <span className={p.group3}>M<span className={p.word}>a</span>t<span className={p.word}>c</span>h</span>
                </h1>
            </header>
            <h2 className={p.note}>
                We provide predictions for the next gameweek matches only as we want
                the most accurate predictions!
            </h2>
            <h3 className={p.el}>
                Please Select A Match
            </h3>

            <div className={p.matchContainer}>
                {matches.map((match, index) => {
                    const matchDate = new Date(match.date).toLocaleDateString(); // Format the date
                    const isSelected = selectedMatch && selectedMatch.team === match.team && selectedMatch.opponent === match.opponent;

                    return (
                        <div
                            key={index}
                            className={`${p.matchCardCustom} ${isSelected ? p.selectedMatch : ''}`}
                            onClick={() => handleMatchSelect(match)}
                        >
                            <h3 className={p.matchTitle}>{match.team} vs {match.opponent}</h3>
                            <p className={p.matchDate}>{matchDate}</p>
                        </div>
                    );
                })}
            </div>

            <button onClick={handlePrediction} className={p.predictButton} disabled={loading}>
                {loading ? 'Loading...' : 'Predict Match'}
            </button>

            {error && !loading && <p className={p.error}>{error}</p>}

            {prediction && !loading && (
                <div className={p.prediction}>
                    <h3 className={p.predictionTitle}>Prediction Result:</h3>
                    <p className={p.predictionText}>{prediction.predictionText}</p>
                </div>
            )}

            <div className={l.backbtn}>
                <Link to="/">Back</Link>
            </div>
        </div>
    );
};

export default PP;
