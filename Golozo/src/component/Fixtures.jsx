import s from './mainstyles.module.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import p from './predicstyle.module.css';
import l from './loginstyle.module.css'
import { Link, useNavigate } from "react-router-dom";

const Fixtures = () => {
    const [matches, setMatches] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchMatches = async () => {
            try {
                const response = await axios.get('http://localhost:8080/matches/allFixtures');
                console.log('API Response:', response.data);
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




    return (

        <div className={s.main}>
            <header className={s.header}>
                <h1>
                    F<span className={s.word}>I</span>
                    X<span className={s.word}>T</span>
                    U<span className={s.word}>R</span>
                    E<span className={s.word}>S</span>
                </h1>
            </header>
            <div className={l.backbtn}>
                <Link to="/">Back</Link>
            </div>

            {error && <p className={p.error}>{error}</p>}

            {!error && matches.length > 0 && (
                <div className={p.matchList}>
                    {matches.map((match, index) => {
                        return (
                            <div key={index} className={p.matchCard}>
                                <h3 className={p.matchTitle}>{match.team} vs {match.opponent}</h3>
                                <p className={p.matchDate}>{match.date}</p>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>

    );
};

export default Fixtures;
