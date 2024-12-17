import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import axios from 'axios';
import {forgotPass, validate_captcha} from "../Modules/Web-server_queries";
import {URL_web} from "../Modules/URL";
import Alert from "../Modules/Alert";
import ReCAPTCHA from "react-google-recaptcha";

function ForgotPassword() {
    const navigate = useNavigate();
    const [errorMessage, setErrorMessage] = useState('');
    const [open, setOpen] = React.useState(false);
    const [captchaToken, setCaptchaToken] = useState(null);

    const [formData, setFormData] = useState({
        email: ''
    });

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
        //const response_captcha = await
        validate_captcha(captchaToken)
            .then(response => {
                if (response.success) {
                    forgotPass(formData)
                        .then(result => {
                            const url = result.url;
                            //console.log(url) Подтверждение почты
                            navigate('/go_to_confirm');
                        })
                        .catch(error => {
                            let message;
                            if (error.response) {
                                switch (error.response.status) {
                                    case 500:
                                        message = 'Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.';
                                        //console.error('InternalServerError');
                                        break;
                                    case 429:
                                        message = 'Слишком много запросов. Попробуйте позже.';
                                        break;
                                    case 400:
                                        message = 'Аккаунта с такой почтой не существует.';
                                        //console.error('SomeRequestArgumentsMissing');
                                        break;

                                    default:
                                        message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                                        //console.error('Error:', error);
                                        break;
                                }
                            } else {
                                message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                            }
                            setErrorMessage(message);
                            setOpen(true);
                        });
                }
            })
            .catch(error => {
                setErrorMessage('Верификация капчи не удалась. Попробуйте еще раз.');
                setOpen(true);
            })


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
            <h2 className="form-title">Забыли пароль</h2>
            <Alert mode={'error'} message={errorMessage} open={open}
                   setOpen={setOpen}/>

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
                <div className="captcha-container">
                    <ReCAPTCHA
                        sitekey={process.env.REACT_APP_RECAPTCHA_SITE_KEY}
                        onChange={handleCaptchaChange}
                    />
                </div>
                <button type="submit">Сбросить пароль</button>

            </form>

            <div className="extra-buttons">
                <button onClick={() => navigate('/login')}>Вернуться к странице входа</button>
            </div>
        </div>
    );
}

export default ForgotPassword;
