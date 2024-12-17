import React, { useEffect, useState } from 'react';
import { checkToken, resetPassword } from "../Modules/Web-server_queries";
import Alert from "../Modules/Alert";
import "./Login.css";
import validatePassword from "../Modules/ValidatePass"; // Using the same CSS as Login

const ResetPassword = () => {
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [mess, setMess] = useState('');
    const [Token, setToken] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(true); // Track loading state

    useEffect(() => {
        const path = window.location.pathname;
        const confirmIndex = path.indexOf('/reset/');

        if (confirmIndex !== -1) {
            const tokenIndex = confirmIndex + '/reset/'.length;
            const extractedToken = path.substring(tokenIndex);
            setToken(extractedToken);
        }

        if (Token) {
            checkToken(Token)
                .then(responseData => {
                    setMess(responseData.message);
                    setLoading(false); // Stop loading when token check is complete
                })
                .catch(error => {
                    let message;
                    if (error.response) {
                        switch (error.response.status) {
                            case 500:
                                message = 'Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.';
                                break;
                            case 429:
                                message = 'Слишком много запросов. Попробуйте позже.';
                                break;
                            case 400:
                                message = 'Заполните все поля!';
                                break;
                            case 403:
                                message = 'Вы пытались зайти по недействительному токену. Попробуйте еще раз!';
                                break;
                            default:
                                message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                                break;
                        }
                    } else {
                        message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                    }
                    setErrorMessage(message);
                    setOpen(true);
                    setLoading(false); // Stop loading when there's an error
                    setTimeout(() => {
                        window.location.href = '/forgot';
                    }, 5000);
                });
        }
    }, [Token]);


    const handleSubmit = (e) => {
        e.preventDefault();

        const passwordValidationMessage = validatePassword(newPassword);
        if (passwordValidationMessage) {
            setErrorMessage(passwordValidationMessage);
            setOpen(true);
            return;
        }

        if (newPassword === confirmPassword) {
            resetPassword(Token, newPassword)
                .then(responseData => {
                    localStorage.setItem('accessToken', responseData.access_token);
                    localStorage.setItem('refreshToken', responseData.refresh_token);
                    window.location.href = '/LK';
                })
                .catch(error => {
                    let message;
                    if (error.response) {
                        switch (error.response.status) {
                            case 500:
                                message = 'Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.';
                                break;
                            case 429:
                                message = 'Слишком много запросов. Попробуйте позже.';
                                break;
                            case 400:
                                message = 'Заполните все поля!';
                                break;
                            case 403:
                                message = 'Вы пытались зайти по недействительному токену. Попробуйте еще раз!';
                                setTimeout(() => {
                                    window.location.href = '/forgot';
                                }, 5000);
                                break;
                            default:
                                message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                                break;
                        }
                    } else {
                        message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                    }
                    setErrorMessage(message);
                    setOpen(true);
                });
        } else {
            setErrorMessage('Пароли не совпадают');
            setOpen(true);
        }
    };

    if (loading) {
        return <div>Загрузка...</div>; // Optional loading indicator
    }

    return (
        <div className="form-container">
            {errorMessage ? (
                <Alert mode={'error'} message={errorMessage} open={open} setOpen={setOpen} />
            ) : (
                <>
                    <h2 className="form-title">Сбросить пароль</h2>
                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="newPassword">Новый пароль:</label>
                            <input
                                type="password"
                                id="newPassword"
                                name="newPassword"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="confirmPassword">Подтвердите пароль:</label>
                            <input
                                type="password"
                                id="confirmPassword"
                                name="confirmPassword"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                            />
                        </div>
                        <button type="submit">Сбросить пароль</button>
                    </form>
                </>
            )}
        </div>
    );
};

export default ResetPassword;
