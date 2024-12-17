import React from "react";
import { Link } from "react-router-dom";
import './Footer.css'; // Import the CSS file

function Footer() {
    return (
        <footer className="footer">
            <div className="footer-content">
                <div className="logo-section">
                    <img src={"/Kallosus_small.svg"} alt="Kallosus" className="logo" />
                    <div className="logo-with-text">
                        <img src={"/logo.png"} alt="Фонд содействия инновациям" className="logo" />
                        <p className="grant-text">
                            Сайт создан при поддержке гранта Фонда содействия инновациям, предоставленного в рамках программы
                            «Студенческий стартап» федерального проекта «Платформа университетского технологического предпринимательства»
                        </p>
                    </div>
                </div>


                <div className="section">
                    <h4 className="section-header">Информация</h4>
                    <ul className="link-list-column">
                        <li><Link to="/documents" className="info-link">Документы</Link></li>
                        <li><Link to="/help" className="info-link">Инструкция</Link></li>
                        <li>
                            <a
                                href="/userAgreement.pdf"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="info-link">
                                Пользовательское соглашение
                            </a>
                        </li>
                    </ul>
                </div>

                <div className="section">
                    <h4 className="section-header">Контакты</h4>
                    <p><strong>Обращайтесь по любым вопросам</strong></p>
                    <p>Почта: <a href="mailto:admin@kallosus.ru" className="link">admin@kallosus.ru</a></p>
                    <p>Телефон: <a href="tel:+79939134660" className="link">+7(995)155-46-60</a></p>
                    <p>Адрес: 115432, город Москва, пр-кт Андропова, д. 10</p>
                </div>
            </div>
            <div className="footer-bottom">
                <p>&copy; 2024 Kallosus</p>
            </div>
        </footer>
    );
}

export default Footer;
