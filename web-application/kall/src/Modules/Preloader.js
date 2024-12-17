import React, { useEffect } from 'react';
import './Preloader.css'; // Подключаем стили

const Preloader = () => {
    useEffect(() => {
        // Проверяем загрузку страницы
        const handleLoad = () => {
            const preloader = document.querySelector('.preloader');
            if (preloader) {
                preloader.classList.add('preloader-remove');
            }
        };

        // Проверяем, если страница уже загружена
        if (document.readyState === 'complete') {
            handleLoad();
        } else {
            // Вешаем событие, если загрузка ещё не завершена
            window.addEventListener('load', handleLoad);
        }

        return () => {
            // Очищаем слушатель, если компонент размонтирован
            window.removeEventListener('load', handleLoad);
        };
    }, []);

    return (
        <div className="preloader">
            <div className="spinner"></div>
        </div>
    );
};

export default Preloader;
