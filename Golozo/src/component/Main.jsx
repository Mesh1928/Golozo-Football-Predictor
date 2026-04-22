import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import s from './mainstyles.module.css';

const GoLoZo = () => {
    const p2Ref = useRef(null);
    const [opacity, setOpacity] = useState(0);
    const [isLoggedIn, setIsLoggedIn] = useState(false); // State to track if user is logged in
    const navigate = useNavigate();

    useEffect(() => {
        const userData = localStorage.getItem('userData');
        if (userData) {
            setIsLoggedIn(true);
        }
    }, []);

    const handleButtonClick = () => {
        navigate('/pred');
    };

    const handleLogout = () => {
        localStorage.removeItem('userData');
        setIsLoggedIn(false);
        navigate('/');
    };

    useEffect(() => {
        const handleScroll = () => {
            if (p2Ref.current) {
                const element = p2Ref.current;
                const rect = element.getBoundingClientRect();
                const windowHeight = window.innerHeight;

                const scrollTop = window.scrollY;
                const documentHeight = document.body.scrollHeight - windowHeight;
                const scrollPercentage = scrollTop / documentHeight;

                if (scrollPercentage >= 0.4) {
                    const newOpacity = (scrollPercentage - 0.4) / 0.6;
                    setOpacity(Math.min(1, newOpacity));
                } else {
                    setOpacity(0);
                }
            }
        };

        window.addEventListener('scroll', handleScroll);

        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);

    return (
        <div className={s.main}>
            <header className={s.header}>
                <h1>
                    G<span className={s.word}>O</span>
                    L<span className={s.word}>O</span>
                    Z<span className={s.word}>O</span>
                </h1>
                <nav className={s.nav}>
                    <ul>
                        <li><Link to='/t'>Teams</Link></li>
                        <li><Link to='/f'>Fixtures</Link></li>
                    </ul>
                </nav>
                <p className={s.tagline}>
                    T
                    <span className={s.word}>h</span>
                    e
                    <span className={s.gap}> </span>
                    <span className={s.word}>B</span>
                    e
                    <span className={s.word}>s</span>
                    t
                    <span className={s.gap}> </span>
                    <span className={s.word}>F</span>
                    o
                    <span className={s.word}>o</span>
                    t
                    <span className={s.word}>b</span>
                    a
                    <span className={s.word}>l</span>
                    l
                    <span className={s.gap}> </span>
                    <span className={s.word2}>PL Predictor</span>
                </p>

                <p className={s.p1}>"The more difficult the victory, the greater the happiness in winning." – Pelé</p>

                <div className={s.p1}>
                    <button className={s.hoverbutton} onClick={handleButtonClick}>
                        Match Predictor Assistant
                    </button>
                </div>

                <p className={s.p2025}>@2025 Copyright</p>

                <br />

                <p className={s.p3}>How Do We Calculate A Prediction Of A Match?</p>

                <p ref={p2Ref} style={{ opacity }} className={s.p2}>
                    We use possession based team and opponent in the last 5 games,
                    club form, total goals conceded in the last 5 games,
                    total goals scored in the last 5 games, which stadium, clean sheets & many more!
                </p>

                <p ref={p2Ref} style={{ opacity }} className={s.p2}>
                    Please be aware we do not guarantee a 100% result, what we give is based statistically.
                    Its all about the entertainment! Enjoy Love & Respect!
                </p>

            </header>
        </div>
    );
};

export default GoLoZo;
