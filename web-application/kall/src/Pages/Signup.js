import React, {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import ReCAPTCHA from 'react-google-recaptcha';
import {login, signup, validate_captcha} from "../Modules/Web-server_queries";
import "./Login.css";
import Alert from "../Modules/Alert";
import validatePassword from "../Modules/ValidatePass";

function Signup() {
    const [errorMessage, setErrorMessage] = useState('');
    const [open, setOpen] = useState(false);
    const [captchaToken, setCaptchaToken] = useState(null);
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '',
        company: '',
        password: '',
        password2: ''
    });

    useEffect(() => {
        const storedAccessToken = localStorage.getItem('accessToken');
        const storedRefreshToken = localStorage.getItem('refreshToken');

        if (storedAccessToken && storedRefreshToken) {
            navigate('/LK');
        }
    }, [navigate]);


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

        const passwordValidationMessage = validatePassword(formData.password);
        if (passwordValidationMessage) {
            setErrorMessage(passwordValidationMessage);
            setOpen(true);
            return;
        }

        if (formData.password !== formData.password2) {
            setErrorMessage('Пароли не совпадают');
            setOpen(true);
            return;
        }

        try {
            const response_captcha = await validate_captcha(captchaToken)

            if (response_captcha.success) {
                // If CAPTCHA is verified, proceed with login
                const responseData = await signup(formData.email, formData.password, formData.company);
                navigate('/go_to_confirm');
            } else {
                setErrorMessage('Верификация капчи не удалась. Попробуйте еще раз.');
                setOpen(true);
            }

        } catch (error) {
            let message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
            if (error.response) {
                switch (error.response.status) {
                    case 500:
                        message = 'Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.';
                        break;
                    case 429:
                        message = 'Слишком много запросов. Попробуйте позже.';
                        break;
                    case 400:
                        message = 'Аккаунт с такой почтой уже существует, или капча не пройдена.';
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
            <h2 className="form-title">Регистрация</h2>
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
                    <label htmlFor="company">Компания:</label>
                    <input
                        type="text"
                        id="company"
                        name="company"
                        value={formData.company}
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
                <div className="form-group">
                    <label htmlFor="password2">Повторите пароль:</label>
                    <input
                        type="password"
                        id="password2"
                        name="password2"
                        value={formData.password2}
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

                <button type="submit">Зарегистрироваться</button>
                <p className="consent-text">
                    Даю <a href="/Policy.pdf" target="_blank" rel="noopener noreferrer" className="consent-link">согласие</a> на обработку своих персональных данных.
                </p>
            </form>
            <div className="extra-buttons">
                <button onClick={() => navigate('/login')}>Вернуться к странице входа</button>
            </div>
        </div>
    );
}

export default Signup;
