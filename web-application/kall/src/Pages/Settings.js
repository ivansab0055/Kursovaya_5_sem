import React, { useEffect, useState } from "react";
import "./Settings.css";
import "./Login.css";
import { changePassword, confirmAccess, refreshToken, subscription } from "../Modules/Web-server_queries";
import { useNavigate } from "react-router-dom";
import Alert from "../Modules/Alert";
import validatePassword from "../Modules/ValidatePass";

function Settings() {
    const navigate = useNavigate();
    const [subscribed, setSubscribed] = useState();
    const storedAccessToken = localStorage.getItem('accessToken');
    const storedRefreshToken = localStorage.getItem('refreshToken');
    const storedEmail = localStorage.getItem('serverEmail');
    const storedCompany = localStorage.getItem('serverCompany');
    const [errorMessage, setErrorMessage] = useState('');
    const [alertMode, setAlertMode] = useState('error');
    const [open, setOpen] = useState(false);
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmNewPassword, setConfirmNewPassword] = useState('');
    const [activeSection, setActiveSection] = useState('password');

    useEffect(() => {
        if (!(storedAccessToken && storedRefreshToken)) {
            navigate('/login');
        }
        confirmAccess(storedAccessToken)
            .then(responseData => {
                setSubscribed(responseData.mailing);
            })
            .catch(error => {
                let message;
                if (error.response) {
                    switch (error.response.status) {
                        case 401:
                            refreshToken(storedRefreshToken)
                                .then(responseData => {
                                    localStorage.setItem('accessToken', responseData.access_token);
                                    window.location.href = '/settings';
                                })
                                .catch(refreshError => {
                                    if (refreshError.response) {
                                        switch (refreshError.response.status) {
                                            case 500:
                                                message = 'Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.';
                                                break;
                                            case 429:
                                                message = 'Слишком много запросов. Попробуйте позже.';
                                                break;
                                            case 401:
                                                message = 'Пропущен заголовок авторизации. Обратитесь в поддержку.';
                                                break;
                                            case 422:
                                                message = 'Проблема со входом. Вы будете перенаправлены на страницу входа.';
                                                break;
                                            default:
                                                message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                                                break;
                                        }
                                    } else {
                                        message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                                    }
                                });
                            break;
                        case 500:
                            message = 'Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.';
                            break;
                        case 429:
                            message = 'Слишком много запросов. Попробуйте позже.';
                            break;
                        case 400:
                            message = 'Отсутствуют необходимые внутренние данные.';
                            break;
                        default:
                            message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                            break;
                    }
                } else {
                    message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                }
                setAlertMode('error');
                setErrorMessage(message);
                setOpen(true);
                setTimeout(() => {
                    window.location.href = '/logout';
                }, 5000);
            });
    }, [navigate, storedAccessToken, storedRefreshToken]);

    const handleSubscriptionClick = (status) => {
        subscription(storedAccessToken, status)
            .then(() => {
                setSubscribed(status);
            })
            .catch(error => {
                setAlertMode('error');
                setErrorMessage(`Ошибка в результате попытки ${status ? 'подписаться' : 'отписаться'}: ${error}`);
                setOpen(true);
            });
    };

    const handlePasswordChange = () => {
        if (newPassword !== confirmNewPassword) {
            setAlertMode('error');
            setErrorMessage('Новые пароли не совпадают');
            setOpen(true);
            return;
        }
        const passwordValidationMessage = validatePassword(newPassword);
        if (passwordValidationMessage) {
            setErrorMessage(passwordValidationMessage);
            setOpen(true);
            return;
        }
        changePassword(storedAccessToken, oldPassword, newPassword)
            .then(() => {
                setOldPassword('');
                setNewPassword('');
                setConfirmNewPassword('');
                setAlertMode('success');
                setErrorMessage('Пароль успешно изменен');
                setOpen(true);
            })
            .catch(error => {
                setAlertMode('error');
                setErrorMessage(`Ошибка при смене пароля: ${error.message}`);
                setOpen(true);
            });
    };

    return (
        <div>
            <div className="settings-container">
                <div className="settings-sidebar">
                    <div className="user-info">
                        <p><strong>Email:</strong> {storedEmail}</p>
                        <p><strong>Компания:</strong> {storedCompany}</p>
                    </div>
                    <ul>
                        <li onClick={() => setActiveSection('password')}
                            className={activeSection === 'password' ? 'active' : ''}>
                            Сменить пароль
                        </li>
                        <li onClick={() => setActiveSection('subscription')}
                            className={activeSection === 'subscription' ? 'active' : ''}>
                            Подписка на рассылку
                        </li>
                    </ul>
                </div>

                <div className="settings-content">
                    <Alert mode={alertMode} message={errorMessage} open={open} setOpen={setOpen} />
                    {activeSection === 'password' && (
                        <div className="password-section">
                            <h2>Сменить пароль</h2>
                            <input
                                type="password"
                                placeholder="Старый пароль"
                                value={oldPassword}
                                onChange={(e) => setOldPassword(e.target.value)}
                            />
                            <input
                                type="password"
                                placeholder="Новый пароль"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                            />
                            <input
                                type="password"
                                placeholder="Подтвердите новый пароль"
                                value={confirmNewPassword}
                                onChange={(e) => setConfirmNewPassword(e.target.value)}
                            />
                            <button className="password-button" onClick={handlePasswordChange}>
                                Сменить пароль
                            </button>
                        </div>
                    )}

                    {activeSection === 'subscription' && (
                        <div className="subscription-section">
                            <h2>Подписаться на рассылку</h2>
                            <div className="subscription-banner">
                                {subscribed === null ? (
                                    <span>Загрузка данных...</span>
                                ) : subscribed ? (
                                    <>
                                        <span>Вы уже подписаны на рассылку!</span>
                                        <button className="unsubscribe-link" onClick={() => handleSubscriptionClick(false)}>
                                            Отписаться
                                        </button>
                                    </>
                                ) : (
                                    <>
                                        <span>Подпишитесь на нашу рассылку, чтобы не пропустить новости!</span>
                                        <button className="subscribe-button" onClick={() => handleSubscriptionClick(true)}>
                                            Подписаться
                                        </button>
                                    </>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Settings;
