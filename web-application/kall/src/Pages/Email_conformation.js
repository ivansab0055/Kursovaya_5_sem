import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { confirmEmail } from '../Modules/Web-server_queries';
import './Login.css';
import Alert from "../Modules/Alert";

function EmailConfirm() {
    const navigate = useNavigate();
    const [token, setToken] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [open, setOpen] = useState(false);

    useEffect(() => {
        const storedAccessToken = localStorage.getItem('accessToken');
        const storedRefreshToken = localStorage.getItem('refreshToken');

        if (storedAccessToken && storedRefreshToken) {
            navigate('/LK');
            return;
        }

        const confirmEmailToken = async () => {
            try {
                const responseData = await confirmEmail(token);
                localStorage.setItem('accessToken', responseData.access_token);
                localStorage.setItem('refreshToken', responseData.refresh_token);
                window.location.href = '/LK';
                //navigate('/LK');
            } catch (error) {
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
                            message = 'Проблема с аккаунтом. Попробуйте еще раз.';
                            break;
                        case 403:
                            message = 'Проблема с токеном входа. Попробуйте еще раз.';
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
                setTimeout(() => {
                    navigate('/login');
                }, 3000);
            }
        };

        const path = window.location.pathname;
        const confirmIndex = path.indexOf('/confirm/');
        if (confirmIndex !== -1) {
            const tokenIndex = confirmIndex + '/confirm/'.length;
            const extractedToken = path.substring(tokenIndex);
            setToken(extractedToken);
            confirmEmailToken();
        }
    }, [token, navigate]);

    return (
        <div>
            <Alert mode={'error'} message={errorMessage} open={open} setOpen={setOpen} />
        </div>
    );
}

export default EmailConfirm;
