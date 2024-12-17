import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import './VideoUpload.css';
import Alert from "./Alert";

const VideoUpload = ({ onFilesSelected, setUploading }) => {
    const [files, setFiles] = useState([]);
    const MAX_FILE_SIZE = 3 * 1024 * 1024 * 1024; // 1GB in bytes
    const [errorMessage, setErrorMessage] = useState('');
    const [open, setOpen] = useState(false);
    const onDrop = useCallback((acceptedFiles) => {
        // Filter out files larger than 1GB
        const validFiles = acceptedFiles.filter(file => file.size <= MAX_FILE_SIZE);
        const newFiles = validFiles.filter(file =>
            !files.some(prevFile => prevFile.name === file.name)
        );

        const updatedFiles = [
            ...files,
            ...newFiles.map(file => Object.assign(file, {
                preview: URL.createObjectURL(file)
            }))
        ].slice(0, 5); // Ограничение на максимум 5 файлов

        setFiles(updatedFiles);

        // Alert user if some files were too large
        if (acceptedFiles.length > validFiles.length) {
            setErrorMessage('Некоторые файлы нельзя загрузить, так как превышают ограничение в 1 ГБ.');
            setOpen(true)
        }
    }, [files]);

    const removeFile = (fileName) => {
        setFiles(prevFiles => {
            const updatedFiles = prevFiles.filter(file => file.name !== fileName);
            updatedFiles.forEach(file => URL.revokeObjectURL(file.preview)); // Освобождение ресурсов
            return updatedFiles;
        });
    };

    const handleUpload = () => {
        setUploading(true);  // Устанавливаем состояние загрузки
        onFilesSelected(files);  // Передаем файлы в родительский компонент
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {'video/*': ['.mp4', '.mkv', '.avi']},
        multiple: true
    });

    useEffect(() => {
        // Cleanup URL objects when component unmounts
        return () => {
            files.forEach(file => URL.revokeObjectURL(file.preview));
        };
    }, [files]);

    return (
        <div className='main'>
            <Alert mode={'error'} message={errorMessage} open={open} setOpen={setOpen}/>
            <div {...getRootProps({ className: 'dropzone' })} style={{ minHeight: files.length > 0 ? 'auto' : '150px' }}>
                <input {...getInputProps()} />
                {files.length === 0 && (
                    <div className="placeholder">
                        <img src={"/cloud.png"} alt="Cloud" className="placeholder-image" />
                        <p>{isDragActive ? 'Перетащите видео сюда ...' : 'Перетащите видео сюда или нажмите, чтобы выбрать файлы'}</p>
                    </div>
                )}
                <div className="preview-container">
                    {files.map(file => (
                        <div key={file.name} className="preview">
                            <video src={file.preview} controls />
                            <button className="remove-button" onClick={(e) => { e.stopPropagation(); removeFile(file.name); }}>×</button>
                            <p>{file.name}</p>
                        </div>
                    ))}
                </div>
            </div>
            {files.length > 0 && (
                <button className="upload-button" onClick={handleUpload}>Загрузить</button>
            )}
        </div>
    );
};

export default VideoUpload;
