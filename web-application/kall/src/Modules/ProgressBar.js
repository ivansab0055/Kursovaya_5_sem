import React from 'react';
import './ProgressBar.css';

const ProgressBar = ({ progress, label, eta }) => {
    const roundedProgress = Math.round(progress);

    // Function to format ETA
    const formatETA = (seconds) => {
        if (seconds >= 3600) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours} ч${hours > 1 ? 'сек' : ''} ${minutes} мин`;
        } else if (seconds >= 60) {
            const minutes = Math.floor(seconds / 60);
            const sec = seconds % 60;
            return `${minutes} мин ${sec} сек`;
        } else {
            return `${seconds} сек`;
        }
    };

    return (
        <div className="progress-bar-container">
            <div className="progress-bar-background">
                <div
                    className="progress-bar-fill"
                    style={{
                        width: `${roundedProgress}%`,
                        backgroundColor: roundedProgress === 100 ? '#4caf50' : '#4a8751'
                    }}
                />
                <div className="progress-bar-text">{label} {roundedProgress}%</div>
            </div>
            {eta !== undefined && (
                <div className="progress-bar-eta">
                    Примерное оставшееся время: {formatETA(eta)}
                </div>
            )}
        </div>
    );
};

export default ProgressBar;
