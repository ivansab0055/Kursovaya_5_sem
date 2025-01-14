import React from "react";
import "./Help.css";

function Help() {
    return (
        <div className="help-container">
            <h1>Помощь</h1>

            <h2>Навигация и использование возможностей Личного Кабинета</h2>

            <p>Добро пожаловать в раздел помощи! Здесь вы найдете полезные инструкции по навигации и использованию
                возможностей страницы Личный Кабинет (ЛК). Следуйте данным рекомендациям, чтобы упростить работу с нашим
                сервисом.</p>

            <h3>Загрузка видео</h3>
            <p>Чтобы загрузить видео, перейдите в раздел Личного Кабинета и нажмите на кнопку "+".
                Следуйте инструкциям на экране, чтобы успешно завершить процесс загрузки.</p>

            <h3>Мониторинг анализа</h3>
            <p>После загрузки видео вы сможете следить за процессом его анализа. В Личном Кабинете отображаются все
                текущие задачи и статус их выполнения. Обратите внимание на индикатор прогресса для отслеживания
                выполнения анализа.</p>

            <h3>Интерпретация результатов</h3>
            <p>После завершения анализа, результаты будут доступны в вашем Личном Кабинете. Ознакомьтесь с ними и
                используйте предоставленные данные для достижения своих целей.</p>

            <h3>Нужна дополнительная помощь?</h3>
            <p>
                Если у вас возникли вопросы, свяжитесь с нашей поддержкой по адресу:&nbsp;
                <a href="mailto:admin@kallosus.ru" className='linkStyle'>
                    admin@kallosus.ru
                </a>
            </p>
        </div>
    );
}

export default Help;
