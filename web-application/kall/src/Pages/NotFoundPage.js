import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
    return (
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
            <h1>404 - Page Not Found</h1>
            <p>Страница не найдена или еще не создана!</p>
            <Link to="/">Вернуться на главную</Link>
        </div>
    );
};

export default NotFoundPage;
