import React, {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import ReCAPTCHA from 'react-google-recaptcha';
import "./Login.css";
import Alert from "../Modules/Alert";
import {login, validate_captcha} from "../Modules/Web-server_queries";

function Login() {
    const navigate = useNavigate();
    const [errorMessage, setErrorMessage] = useState('');
    const [open, setOpen] = useState(false);
    const [captchaToken, setCaptchaToken] = useState(null);

    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });

    useEffect(() => {
        const storedAccessToken = localStorage.getItem('accessToken');
        const storedRefreshToken = localStorage.getItem('refreshToken');
        if (storedAccessToken && storedRefreshToken) {
            navigate('/LK');
        }
    }, [navigate]);

    const handleSignUpClick = () => {
        navigate('/Signup');
    };

    const handleForgetPasswordClick = () => {
        navigate('/forgot');
    };

    const handleCaptchaChange = (token) => {
        setCaptchaToken(token);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (process.env.REACT_APP_NODE_ENV === 'production' && !captchaToken) {
            setErrorMessage('Пожалуйста, подтвердите, что вы не робот.');
            setOpen(true);
            return;
        }

        let resp_captcha = false;
        try{
            const response_captcha = await validate_captcha(captchaToken)
            resp_captcha = true;
        }catch (error){
            if (error.response) {
                switch (error.response.status) {
                    case 400:
                        setErrorMessage('Ошибка капчи. Перезагрузите страницу и попробуйте еще раз.');
                        setOpen(true);
                        break;
                    default:
                        setErrorMessage('Верификация капчи не удалась. Попробуйте еще раз.');
                        setOpen(true);
                        break;
                }
                resp_captcha = false;
            }
        }
        if (resp_captcha)
            try {
                // Send the CAPTCHA token to your backend for verification
                const loginResponse = await login(formData.email, formData.password);
                localStorage.setItem('accessToken', loginResponse.access_token);
                localStorage.setItem('refreshToken', loginResponse.refresh_token);
                window.location.href = '/LK';

            } catch (error) {
                //console.error('Error during login:', error);
                let message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                if (error.response) {
                    switch (error.response.status) {
                        case 500:
                            message = 'Что-то пошло не так. Страница будет перезагружена';
                            setErrorMessage(message);
                            setOpen(true);
                            setTimeout(() => {
                                window.location.href = '/login';
                            }, 5000);
                            break;
                        case 429:
                            message = 'Слишком много запросов. Попробуйте позже.';
                            break;
                        case 400:
                            message = 'Заполните все поля и пройдите капчу!';
                            break;
                        case 401:
                            message = 'Неверный логин или пароль. Проверьте правильность введенных данных.';
                            break;
                        default:
                            break;
                    }
                }
                setErrorMessage(message);
                setOpen(true);
            }
    };

    const handleInputChange = (event) => {
        const {name, value} = event.target;
        setFormData({
            ...formData,
            [name]: value
        });
    };

    return (
        <div className="form-container">
            <h2 className="form-title">Вход</h2>
            <Alert mode={'error'} message={errorMessage} open={open} setOpen={setOpen}/>

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="email">Email:</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Пароль:</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        required
                    />
                </div>

                <div className="captcha-container">
                    <ReCAPTCHA
                        sitekey={process.env.REACT_APP_RECAPTCHA_SITE_KEY}
                        onChange={handleCaptchaChange}
                    />
                </div>

                <button type="submit">Войти</button>
            </form>

            <div className="extra-buttons">
                <button onClick={handleForgetPasswordClick}>Забыли пароль?</button>
                <p>
                    <span className="inline-item">Еще нет аккаунта?</span>
                    <button className="signup-link" onClick={handleSignUpClick}>Создайте его!</button>
                </p>
            </div>
        </div>
    );
}

export default Login;
