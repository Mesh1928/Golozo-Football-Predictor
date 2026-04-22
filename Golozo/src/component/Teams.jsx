import s from './mainstyles.module.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import p from './predicstyle.module.css';
import l from './loginstyle.module.css';
import { Link } from "react-router-dom";

const Teams = () => {
    const [teams, setTeams] = useState([]);
    const [error, setError] = useState('');


    useEffect(() => {
        const fetchTeams = async () => {
            try {
                const response = await axios.get('http://localhost:8080/matches/teams');
                console.log('API Response:', response.data);
                if (Array.isArray(response.data)) {
                    setTeams(response.data);
                } else {
                    setError("Failed to load teams.");
                }
            } catch (error) {
                setError("Error fetching teams: " + error.message);
                console.error("Error fetching teams:", error);
            }
        };

        fetchTeams();
    }, []);

    return (
        <div className={s.main}>
            <header className={s.header}>
                <h1>
                    T<span className={s.word}>E</span>
                    A<span className={s.word}>M</span>
                    S
                </h1>
            </header>
            <div className={l.backbtn}>
                <Link to="/">Back</Link>
            </div>

            {error && <p className={p.error}>{error}</p>}

            {!error && teams.length > 0 && (
                <div className={p.matchList}>
                    {teams.map((team, index) => (
                        <div key={index} className={p.matchCard}>
                            <h3 className={p.matchTitle}>{team}</h3>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Teams;
