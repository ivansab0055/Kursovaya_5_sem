import React, { useRef, useState, useEffect } from 'react';
import ReactPlayer from 'react-player';

const VideoPreview = ({ url, homepage }) => {
    const playerRef = useRef(null);
    const [isUserInteracted, setIsUserInteracted] = useState(homepage);
    const [hasEnded, setHasEnded] = useState(false);
    const [isFading, setIsFading] = useState(homepage); // Начать с анимации только на homepage

    useEffect(() => {
        if (homepage) {
            setIsUserInteracted(true);
            setIsFading(true); // Начать плавное появление при загрузке
            setTimeout(() => setIsFading(false), 300); // Длительность плавного появления
        }
    }, [homepage]);

    const handleError = (e) => {
        if (process.env.REACT_APP_NODE_ENV === 'development') {
            console.error("Ошибка загрузки плеера: ", e);
        }
    };

    const isGif = url.endsWith('.gif');

    const handleEnded = () => {
        if (!homepage) {
            setHasEnded(true);
        }
    };

    const playerWrapperStyle = {
        position: 'relative',
        paddingTop: '56.25%',
        overflow: 'hidden',
    };

    const playerStyle = {
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        opacity: isFading ? 0.4 : 1, // Начальная непрозрачность 0 для плавного перехода
        transition: 'opacity 0.3s ease-in-out', // Плавный переход
    };

    return (
        <div style={playerWrapperStyle} onClick={() => setIsUserInteracted(true)}>
            {isGif ? (
                <img
                    src={url}
                    alt="GIF preview"
                    style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                    }}
                />
            ) : (
                <ReactPlayer
                    ref={playerRef}
                    url={url}
                    width="100%"
                    height="100%"
                    style={playerStyle}
                    controls={!homepage}
                    playing={isUserInteracted && !hasEnded}
                    loop={homepage}
                    muted={homepage}
                    onEnded={handleEnded}
                    onError={handleError}
                />
            )}
        </div>
    );
};

export default VideoPreview;
