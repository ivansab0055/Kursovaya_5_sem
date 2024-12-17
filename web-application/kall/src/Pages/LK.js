import React, {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";
import {confirmAccess, refreshToken} from '../Modules/Web-server_queries';
import ProgressBar from "../Modules/ProgressBar";

import {getObjectFromS3, getSignedUrl, uploadObjectToS3} from '../Modules/s3Helper';
import Matrix from "../Modules/Matrix";
import {create_folders, get_results, get_status, predict, stop} from "../Modules/NN_queries";
import Alert from "../Modules/Alert";
import "./LK.css"
import ChartModule from "../Modules/Chart";
import VideoPreview from "../Modules/VideoPreview";
import VideoUpload from "../Modules/VideoUpload";
import NoVideos from "./NoVideos";
import ErrorBoundary from "../Modules/ErrorBoundary";
import Preloader from "../Modules/Preloader";

function LK() {
    const navigate = useNavigate();
    const [errorMessage, setErrorMessage] = useState('');
    const [open, setOpen] = useState(false);
    const [serverEmail, setServerEmail] = useState('');
    const [noVideos, setNoVideos] = useState(false);  // Новый стейт для отображения NoVideos
    const [timer, setTimer] = useState(true);
    const [serverCompany, setServerCompany] = useState('');
    const [currentTask_id, setCurrentTask_id] = useState(0);
    const [eta, setEta] = useState(-1);
    const [status, setStatus] = useState();
    const [bar, setBar] = useState(0);
    const [loading, setLoading] = useState(false);
    const [chartData, setChartData] = useState();
    const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
    const [isProgressModalOpen, setIsProgressModalOpen] = useState(false);

    const [prevFiles, setPrevFiles] = useState([]);
    const [folder, setFolder] = useState([]);
    const [glLinks, setGlLinks] = useState([]);

    const [uploading, setUploading] = useState(false);

    const [infect, setInfect] = useState([]);
    const [videoUrl, setVideoUrl] = useState('');
    const [videoDate, setVideoDate] = useState('');
    //const [videoDate, setVideoDate] = useState('');

    // Modal visibility state
    const [isModalOpen, setIsModalOpen] = useState(false);

    const storedAccessToken = localStorage.getItem('accessToken');
    const storedRefreshToken = localStorage.getItem('refreshToken');

    const storedTask_id = parseInt(localStorage.getItem('Task_id'));

    function removeEmptyElements(array) {
        return array.filter(item => item !== '' && !(Array.isArray(item) && item.length === 0));
    }

    useEffect(() => {

// Генерация предустановленной ссылки

        if (!(storedAccessToken && storedRefreshToken)) {
            navigate('/login');
        }

        confirmAccess(storedAccessToken)
            .then(responseData => {
                setServerEmail(responseData.email);
                setServerCompany(responseData.company);
                if(responseData.role ==='admin')
                {
                    navigate('/adminlk')
                }
                localStorage.setItem('serverEmail', responseData.email)
                localStorage.setItem('serverCompany', responseData.company)
            })
            .catch(error => {
                let message;
                if (error.response) {
                    switch (error.response.status) {
                        case 401:
                            refreshToken(storedRefreshToken)
                                .then(responseData => {
                                    localStorage.setItem('accessToken', responseData.access_token);
                                    window.location.href = '/LK';
                                })
                                .catch(refreshError => {
                                    if (refreshError.response) {
                                        switch (refreshError.response.status) {
                                            case 500:
                                                message = 'Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.';
                                                break;
                                            case 429:
                                                message = 'Слишком много запросов. Попробуйте позже.';
                                                break;
                                            case 401:
                                                message = 'Пропущен заголовок авторизации. Обратитесь в поддержку.';
                                                setErrorMessage(message);
                                                setOpen(true);

                                                break;
                                            case 422:
                                                message = 'Проблема со входом. Вы будете перенаправлены на страницу входа';
                                                setErrorMessage(message);
                                                setOpen(true);
                                                setTimeout(() => {
                                                    window.location.href = '/logout';
                                                }, 5000);
                                                break;
                                            default:
                                                message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                                                setErrorMessage(message);
                                                setOpen(true);
                                                break;
                                        }
                                    } else {
                                        message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                                        setErrorMessage(message);
                                        setOpen(true);

                                    }
                                });
                            break;
                        case 500:
                            message = 'Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.';
                            break;
                        case 400:
                            message = 'Отсутствуют необходимые внутренние данные.';
                            setErrorMessage(message);
                            setOpen(true);
                            setTimeout(() => {
                                window.location.href = '/logout';
                            }, 5000);
                            break;
                        default:
                            message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                            setErrorMessage(message);
                            setOpen(true);
                            break;
                    }
                } else {
                    message = 'Что-то пошло не так. Попробуйте перезагрузить страницу и попробовать еще раз.';
                    setErrorMessage(message);
                    setOpen(true);

                }


            });
        if (storedTask_id) {
            setCurrentTask_id(storedTask_id)
            setLoading(true)
        }

        get_results(storedAccessToken)
            .then(result => {
                setPrevFiles(removeEmptyElements(result.files))
                if(removeEmptyElements(result.files)-1)
                    setNoVideos(true);
                setCurrentVideoIndex((removeEmptyElements(result.files)).length - 1)
            })
            .catch(error => {
                if(error.response) {
                    let message
                    switch (error.response.status) {
                        case 500:
                            message = 'Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.';
                            setErrorMessage(message);
                            setOpen(true)
                            break;

                        case 404:
                            //message = 'Вы еще не загрузили ни одного видео!'
                            setNoVideos(true);
                            //setErrorMessage(message);
                            //setOpen(true)
                            break;
                        case 400:
                            message = 'Не все аргументы были переданы на сервер!';
                            setErrorMessage(message);
                            setOpen(true)
                            break;
                        case 429:
                            message = 'Слишком много запросов, попробуте позже!';
                            setErrorMessage(message);
                            setOpen(true)
                            break;
                        default:
                            message = 'Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.';
                            setErrorMessage(message);
                            setOpen(true)
                            break;
                    }

                }
                else{
                    setErrorMessage('Нет ответа от сервера! Обратитесь в поддержку.');
                    setOpen(true)
                }

            })
    }, [navigate, storedAccessToken, storedRefreshToken]);

    useEffect(() => {
        if (glLinks.length > 0 && folder.length > 0) {
            const links_dict = {
                src: glLinks,
                dst: folder
            };
            predict(storedAccessToken, links_dict)
                .then(result => {
                    setCurrentTask_id(result.task_id);
                    localStorage.setItem('Task_id', (result.task_id).toString())
                })
                .catch(error => {
                    setErrorMessage(`Ошибка при обработке видео: ${error}`);
                    setOpen(true)
                });

        }
    }, [folder]);

    useEffect(() => {
        if (storedTask_id) {
            setCurrentTask_id(storedTask_id)
            setLoading(true)
        }
        //console.log('task - ', currentTask_id)
        //console.log('bar - ', bar)
        if (currentTask_id !== 0) {
            get_status(storedAccessToken, currentTask_id)
                .then(result => {
                    setBar(result.progress);
                    setStatus(result.status);
                    setEta(result.eta);
                    setLoading(true)
                })
                .catch(error => {

                    setErrorMessage(`Ошибка при получении статуса обработки: ${error}`);
                    setOpen(true)
                });
        }
    }, [currentTask_id, storedTask_id]);

    useEffect(() => {

        if ((status === "queue" || status === "run" || status === "complete") && loading && currentTask_id) {
            const interval = setInterval(() => {
                get_status(storedAccessToken, currentTask_id)
                    .then(result => {
                        setBar(result.progress);
                        setStatus(result.status);
                        setEta(result.eta);
                    })
                    .catch(error => {
                        setErrorMessage(`Ошибка при получении статуса обработки: ${error}`);
                        setOpen(true)
                    });
                if (status === "complete") {
                    clearInterval(interval);
                    setLoading(false);
                    setCurrentTask_id(0);
                    localStorage.removeItem('Task_id')
                    setBar(0);
                    setStatus('');
                    setIsProgressModalOpen(false)
                    get_results(storedAccessToken)
                        .then(result => {
                            setPrevFiles(removeEmptyElements(result.files))
                            setCurrentVideoIndex((removeEmptyElements(result.files)).length - 1)
                        })
                        .catch(error => {
                            setErrorMessage(`Ошибка при получении истории результатов анализа: ${error}`);
                            setOpen(true)
                        })

                    window.location.href = '/lk';

                } else if (status === 'error') {
                    clearInterval(interval);
                    setLoading(false);
                    setCurrentTask_id(0);
                    localStorage.removeItem('Task_id')
                    setBar(0);
                    setStatus('');
                    setIsProgressModalOpen(false)
                    setErrorMessage(`Ошибка при формировании ответа, попробуйте еще раз или обратитесь в поддержку!`);
                    setOpen(true)
                }

            }, 3000);
        }

    }, [status]);

    useEffect(() => {

        if (prevFiles.length > 0 && currentVideoIndex !== undefined) {

            const file = prevFiles[currentVideoIndex];

            const parts = file.split('/');
            const bucket = parts.slice(0, -1).join('/');
            const key = parts[parts.length - 1];
            const datePart = parts.find(part => /\d{2}_\d{2}_\d{2}/.test(part));
            const date = datePart ? datePart.replace(/_/g, '.') : 'Unknown Date';
            setVideoDate(date);
            setTimer(true)
            getObjectFromS3(bucket, key)
                .then(result => {
                    const jsonData = JSON.parse(result.data.Body.toString('utf-8'));
                    //setVideoS3Url(jsonData.dst);
                    setChartData(jsonData.num_detected);


                    getSignedUrl(jsonData.dst)
                        .then(result => {
                            setVideoUrl(result)
                            //console.log(result)
                        })
                        .catch(error => {
                            setErrorMessage(`Ошибка при получении видео: ${error}`);
                            setOpen(true);
                        })


                    fetchImages(jsonData.source_of_infection);
                })
                .catch(error => {
                    setErrorMessage(`Ошибка при получении изображений: ${error}`);
                    setOpen(true);
                });
            setTimer(false)
        }
    }, [currentVideoIndex, prevFiles]);

    const fetchImages = async (inf) => {
        setTimer(true)
        try {
            const images = await Promise.all(
                inf.map(async (item) => {

                    const parts = item[0].split('/');
                    const bucket = parts.slice(0, -1).join('/');
                    const key = parts[parts.length - 1];

                    const response = await getObjectFromS3(bucket, key);
                    const blob = new Blob([response.data.Body], {type: 'image/png'});
                    const imageUrl = URL.createObjectURL(blob);
                    return [imageUrl, item[1]];
                })
            );
            setInfect(images);
        } catch (error) {
            setErrorMessage(`Ошибка при получении изображений: ${error}`);
            setOpen(true);
        }
        setTimer(false)
    };

    const handlePrev = () => {
        if (currentVideoIndex > 0) {
            setCurrentVideoIndex(currentVideoIndex - 1);
        }
    };

    const handleNext = () => {
        if (currentVideoIndex < prevFiles.length - 1) {
            setCurrentVideoIndex(currentVideoIndex + 1);
        }
    };


    const handleUpload = async (uploadedFiles) => {
        try {
            setUploading(true);
            const folderCreation = await create_folders(storedAccessToken, uploadedFiles.length);
            const folders = folderCreation.folders;

            const links = [];
            // Upload each file to its corresponding folder
            for (let i = 0; i < folders.length; i++) {
                const file = uploadedFiles[i];
                links.push(`${folders[i]}${file.name}`);
                const onProgress = (progress) => {
                    setBar(progress)
                };
                const {data, error} = await uploadObjectToS3(folders[i], file.name, file, onProgress);
                if (error) {
                    setErrorMessage(`Ошибка при загрузке: ${error}`);
                    setOpen(true)
                }
            }
            setGlLinks(links);
            setFolder(folders);
            setIsProgressModalOpen(true)
            setIsModalOpen(false);
            setUploading(false);  // Останавливаем спиннер после завершения загрузки
        } catch (error) {
            setErrorMessage(`Ошибка загрузки файлов: ${error}`);
            setOpen(false);
            setUploading(false);  // Останавливаем спиннер в случае ошибки
        }
    };

    const handleStop = () => {
        stop(storedAccessToken, currentTask_id)
            .then(() => {
                setLoading(false);
                setIsProgressModalOpen(false);
                setCurrentTask_id(0);
                setBar(0);
                setStatus('');
                localStorage.removeItem('Task_id');
                window.location.href = '/lk';
            })
            .catch(error => {
                setErrorMessage(`Ошибка при остановке обработки: ${error}`);
                setOpen(true);
            });
    };

    return (

            <div className="main-content">
                <Alert mode={'error'} message={errorMessage} open={open} setOpen={setOpen}/>

                <div className="content-wrapper">
                    <div className="left-section">
                        <div className="navigation">
                            {currentVideoIndex > 0 && (
                                <button onClick={handlePrev}>{"<"}</button>
                            )}
                            {!noVideos ?(
                            <span>{`Video ${currentVideoIndex + 1}.mp4 - ${videoDate}`}</span>
                                ):(
                                <p className="first-video">Вы еще не загружали ни одного видео! Нажмите кнопку "+" чтобы начать работу.</p>
                            )}
                            {currentVideoIndex < prevFiles.length - 1 && (
                                <button onClick={handleNext}>{">"}</button>
                            )}
                        </div>
                        {infect.length > 0 && (
                            <>
                            <ErrorBoundary>
                                <VideoPreview url={videoUrl} homepage={false}/>
                            </ErrorBoundary>
                                <div >
                                    <ChartModule data={chartData}/>
                                </div>
                            </>
                        )}
                    </div>
                    <div className="right-section">
                        {loading || uploading ? (
                                <button onClick={() => setIsProgressModalOpen(true)}>Просмотр прогресса обработки</button>
                            ) :
                            (
                                <button onClick={() => setIsModalOpen(true)} className="add-button">+</button>
                            )}
                        {infect.length > 0 && (
                            timer ? (
                                <Preloader/>
                            ) : (
                                <div>
                                    <h3>Очаги поражения листьев:</h3>
                                    <Matrix data={infect}/>
                                </div>
                            )

                        )}

                    </div>
                </div>

                {isModalOpen && (
                    <div className="modal">
                        <div className="modal-content">
                            <span className="close" onClick={() => setIsModalOpen(false)}>&times;</span>
                            {uploading ? (
                                <ProgressBar progress={bar} label={'Загрузка видео на сервер...'}/>
                                //<div className="spinner"></div>  Спиннер при загрузке
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
                                    <ProgressBar progress={bar} label={'Обработка видео...'} eta={eta}/>
                                </div>
                                <button className="stop" onClick={handleStop}>Стоп</button>
                            </div>
                        </div>
                    </div>
                )}

            </div>

    );
}

export default LK;
