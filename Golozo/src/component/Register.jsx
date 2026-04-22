import React, { useState } from 'react';
import axios from 'axios';
import l from './loginstyle.module.css';
import { Link, useNavigate } from "react-router-dom";


const Register = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });

    const [errors, setErrors] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });

    const [successMessage, setSuccessMessage] = useState('');

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setErrors({
            ...errors,
            [e.target.name]: ''
        });
    };

    const validateForm = () => {
        const newErrors = {};
        if (!formData.username.trim()) newErrors.username = 'Username is required.';
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!formData.email.trim()) newErrors.email = 'Email is required.';
        else if (!emailRegex.test(formData.email)) newErrors.email = 'Invalid email format.';
        if (!formData.password) newErrors.password = 'Password is required.';
        else if (formData.password.length < 6) newErrors.password = 'Password must be at least 6 characters.';
        if (!formData.confirmPassword) newErrors.confirmPassword = 'Please confirm your password.';
        else if (formData.confirmPassword !== formData.password) newErrors.confirmPassword = 'Passwords do not match.';
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (validateForm()) {
            try {

                const response = await axios.post('http://localhost:8080/api/user', {
                    email: formData.email,
                    password: formData.password
                });
                navigate('/');
                setFormData({ username: '', email: '', password: '', confirmPassword: '' });
            } catch (error) {
                if (error.response && error.response.data) {
                    setErrors({ ...errors, email: error.response.data });
                } else {
                    console.error('Registration error:', error);
                }
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
                    Register - G<span className={l.word}>O</span>
                    L<span className={l.word}>O</span>
                    Z<span className={l.word}>O</span>
                </h2>
                <form className={l.loginform} onSubmit={handleSubmit} noValidate>
                    <div className={l.formgroup}>
                        <label htmlFor="username">USERNAME</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleInputChange}
                        />
                        {errors.username && <p className={l.error}>{errors.username}</p>}
                    </div>
                    <div className={l.formgroup}>
                        <label htmlFor="email">EMAIL</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                        />
                        {errors.email && <p className={l.error}>{errors.email}</p>}
                    </div>
                    <div className={l.formgroup}>
                        <label htmlFor="password">PASSWORD</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleInputChange}
                        />
                        {errors.password && <p className={l.error}>{errors.password}</p>}
                    </div>
                    <div className={l.formgroup}>
                        <label htmlFor="confirmPassword">CONFIRM PASSWORD</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleInputChange}
                        />
                        {errors.confirmPassword && <p className={l.error}>{errors.confirmPassword}</p>}
                    </div>
                    {successMessage && <p className={l.success}>{successMessage}</p>} {/* Display success message */}
                    <button type="submit" className={l.submit}>Register</button>
                    <p className={l.reg}>
                        Already Have An Account? <Link to="/log">Login</Link>
                    </p>
                </form>
            </div>
        </div>
    );
};

export default Register;
