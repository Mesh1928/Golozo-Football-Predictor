import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import l from './loginstyle.module.css';
import s from './mainstyles.module.css';
import { Link } from 'react-router-dom';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            // Sending login data to backend via POST request
            const response = await axios.post('http://localhost:8080/api/auth/login', null, {
                params: {
                    email: email,
                    password: password,
                },
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            // If login is successful, handle the response
            console.log('Logged in successfully:', response.data);

            // Optionally, store user data or token in localStorage/sessionStorage
            localStorage.setItem('userData', JSON.stringify(response.data)); // Example

            // Navigate to the home page or another page
            navigate('/');
        } catch (error) {
            // Improved error handling with logging of the full error object
            console.error('Login error:', error);

            if (error.response) {
                if (error.response.status === 401) {
                    setError('Invalid email or password');
                } else if (error.response.status === 404) {
                    setError('Endpoint not found');
                } else if (error.response.data && error.response.data.message) {
                    setError(`An error occurred: ${error.response.data.message}`);
                } else {
                    setError('An error occurred, please try again later.');
                }
            } else {
                setError('Network error, please try again');
            }
        }
    };

    return (
        <div className={l.loginbody}>
            <div className={l.backbtn}>
                <Link to="/">Back</Link>
            </div>
            <div className={l.logincontainer}>
                <h2>
                    Login - G<span className={l.word}>O</span>
                    L<span className={l.word}>O</span>
                    Z<span className={l.word}>O</span>
                </h2>

                {/* Display error message if there is one */}
                {error && <p className={l.error}>{error}</p>}

                {/* Login form */}
                <form className={l.loginform} onSubmit={handleSubmit}>
                    <div className={l.formgroup}>
                        <label htmlFor="email">EMAIL</label>
                        <input
                            type="text"
                            id="email"
                            name="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className={l.formgroup}>
                        <label htmlFor="password">PASSWORD</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className={l.submit}>Login</button>

                    {/* Link to register if user doesn't have an account */}
                    <p className={l.reg}>
                        Don't Have An Account? <Link to="/register">Register Now</Link>
                    </p>
                </form>
            </div>
        </div>
    );
};

export default Login;
