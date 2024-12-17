import React from 'react';
import "./Documents.css"
const Documents = () => {
    // Массив с информацией о документах
    const documents = [
        {
            name: 'Политика обработки персональных данных',
            url: '/Policy.pdf',
        },
        {
            name: 'Пользовательское соглашение',
            url: '/userAgreement.pdf',
        },
    ];

    return (
        <div className="documents-container">
            <h2>Документы для скачивания</h2>
            <ul className="document-list">
                {documents.map((doc, index) => (
                    <li key={index}>
                        <a href={doc.url} target="_blank" rel="noopener noreferrer">
                            {doc.name}
                        </a>
                    </li>
                ))}
            </ul>
            <button className="back-button" onClick={() => window.history.back()}>
                Назад
            </button>
        </div>
    );
};

export default Documents;
