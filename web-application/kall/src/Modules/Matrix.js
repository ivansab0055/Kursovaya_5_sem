import React, { useState } from 'react';
import './Matrix.css';

const Matrix = ({ data }) => {
    const [modalImageUrl, setModalImageUrl] = useState(null);

    const handleImageClick = (imageUrl) => {
        setModalImageUrl(imageUrl);
    };

    const handleCloseModal = () => {
        setModalImageUrl(null);
    };

    // Limit the number of images to 9
    const limitedData = data.slice(0, 9);

    return (
        <div>
            <div className="matrix-container">
                {limitedData.map((item, index) => (
                    <div key={index} className="matrix-cell">
                        <div className="image" onClick={() => handleImageClick(item[0])}>
                            <img src={item[0]} alt={`Image ${index}`} />
                        </div>
                        <div className="number">{item[1].toFixed(2) + ' сек'}</div>
                    </div>
                ))}
            </div>
            {modalImageUrl && (
                <div className="modal" onClick={handleCloseModal}>
                    <div className="modal-content">
                        <span className="close" onClick={handleCloseModal}>&times;</span>
                        <img src={modalImageUrl} alt="Full Size" className="full-size-image" />
                    </div>
                </div>
            )}
        </div>
    );
};

export default Matrix;
