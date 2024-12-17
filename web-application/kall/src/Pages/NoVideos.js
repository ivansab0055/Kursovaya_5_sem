import React, { useState } from 'react';
import VideoUpload from "../Modules/VideoUpload";
import ProgressBar from "../Modules/ProgressBar";
import {uploadObjectToS3 } from "../Modules/s3Helper";
import {create_folders} from "../Modules/NN_queries"
import './NoVideos.css';

function NoVideos({ onUploadComplete, storedAccessToken }) {
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isProgressModalOpen, setIsProgressModalOpen] = useState(false);

    const handleUpload = async (uploadedFiles) => {
        try {
            setUploading(true);
            const folderCreation = await create_folders(storedAccessToken, uploadedFiles.length);
            const folders = folderCreation.folders;

            for (let i = 0; i < folders.length; i++) {
                const file = uploadedFiles[i];
                const onProgress = (progress) => {
                    setUploadProgress(progress);
                };
                await uploadObjectToS3(folders[i], file.name, file, onProgress);
            }

            setIsProgressModalOpen(true);
            setUploading(false);
            onUploadComplete();
        } catch (error) {
            console.error('Ошибка загрузки файлов:', error);
            setUploading(false);
        }
    };

    return (
        <div className="no-videos-container">
            <h2>Вы еще не загрузили ни одного видео!</h2>
            {uploading ? (
                <div className="spinner"></div> // Спиннер при загрузке
            ) : (
                <button className="add-button" onClick={() => setIsProgressModalOpen(true)}>+</button>
            )}


            {/*
            {isModalOpen && (
                <div className="modal">
                    <div className="modal-content">
                        <span className="close" onClick={() => setIsModalOpen(false)}>&times;</span>
                        {uploading ? (
                            <div className="spinner"></div> // Спиннер при загрузке
                        ) : (
                            <VideoUpload onFilesSelected={handleUpload} setUploading={setUploading}/>
                        )}
                    </div>
                </div>
            )}

            {isProgressModalOpen && (
                <div className="modal">
                    <div className="modal-content">
                        <span className="close" onClick={() => setIsProgressModalOpen(false)}>&times;</span>
                        <div className="modal-progress-wrapper">
                            <div className="progress-bar-container">
                                <ProgressBar progress={bar}/>
                            </div>
                            <button className="stop" onClick={handleStop}>Стоп</button>
                        </div>
                    </div>
                </div>
            )}
*/}
        </div>
    );
}

export default NoVideos;
