import React, {useEffect, useState} from 'react';
import './Home.css';
import {useNavigate} from "react-router-dom";
import VideoPreview from "../Modules/VideoPreview";
import Footer from "../Nav/Footer";
import Alert from "../Modules/Alert";
import {getSignedUrl} from "../Modules/s3Helper";
import ErrorBoundary from "../Modules/ErrorBoundary";
function Home() {
    const navigate = useNavigate();
    const [videoUrl, setVideoUrl] = useState('');
    //const [photoUrl, setPhotoUrl] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [open, setOpen] = useState(false);
    useEffect(() => {
        // Прокрутка к видео модулю при загрузке страницы
        const videoSection = document.querySelector('.home-container');
        if (videoSection) {
            videoSection.scrollIntoView({behavior: 'smooth'});
        }/*
        getSignedUrl('Home-page/poland_fields_for_home_page.mp4')
            .then(result => {
                setVideoUrl(result)
            })
            .catch(error => {
                setErrorMessage(`Ошибка воспроизведения видео: ${error}`);
                setOpen(true)
            })*/
    }, []);
    const handleClick = () => {
        navigate('/login');
    }

    const scrollToContent = () => {
        const contentSection = document.querySelector('.content-section');
        contentSection.scrollIntoView({behavior: 'smooth'});
    }

    return (
        <div className="home-container">
            <Alert mode={'error'} message={errorMessage} open={open} setOpen={setOpen}/>
            <div className="video-background">
                <ErrorBoundary>
                    <VideoPreview url={"/golden-wheat-field.mp4"} homepage={true}/>
                </ErrorBoundary>
                <div className="overlay-text">
                    <h1>Искусство видеть сквозь листья</h1>
                    <div className="scroll-icon" onClick={scrollToContent}>&#x25BC;</div>
                </div>
            </div>

            <div className="content-section">
                <div className="why-section">
                    <h2>Зачем сотрудничать с Kallosus</h2>
                    <p>
                        Улучшите урожайность и защитите посевы с помощью уникальной технологии определения болезней
                        растений по видео. Наша автоматизированная система позволит вам оперативно реагировать на
                        угрозы, оптимизировать использование ресурсов и повысить эффективность, обеспечивая высокое
                        качество урожая.
                        <br/>
                        <br/>
                        Если вы интересуетесь проверкой культур из списка, то присоединитесь к нам уже сегодня, чтобы
                        улучшить процесс выращивания и получить высокие результаты в сельском хозяйстве.
                    </p>
                    <button className="join-button" onClick={handleClick}>Присоединиться</button>
                </div>

                <div className="skills-section">
                    <h2>Что мы умеем</h2>
                    <div className="cards-container">
                        <div className="card green-card">
                            <h3>Широкий спектр культур и болезней</h3>
                            <p>
                                Наша технология охватывает более 14 различных культур, включая зерновые, овощные,
                                фруктовые деревья и виноградники. Мы способны идентифицировать сотни различных болезней
                                и поражений, начиная от грибковых инфекций и заканчивая вирусными заболеваниями и
                                повреждениями, вызванными насекомыми-вредителями.
                            </p>
                        </div>
                        <div className="card light-green-card">
                            <h3>Снижение затрат и повышение эффективности</h3>
                            <p>
                                Наши решения помогают значительно снизить расходы на обработку и лечение растений, за
                                счет точного определения проблемных зон и применения целевых мер. Это не только экономит
                                ресурсы, но и уменьшает негативное воздействие на окружающую среду.
                            </p>
                        </div>
                        <div className="card yellow-card">
                            <h3>Комплексная диагностика</h3>
                            <p>
                                Мы предлагаем комплексные решения для мониторинга состояния здоровья растений, используя
                                беспилотные летательные аппараты (БПЛА). Наши системы позволяют оперативно обнаруживать
                                признаки заболеваний и вредителей на ранних стадиях, что значительно увеличивает шансы
                                на успешное лечение и минимизацию потерь урожая.
                            </p>
                        </div>
                        <div className="card green-card">
                            <h3>Прогнозирование и предотвращение</h3>
                            <p>
                                Мы не только выявляем текущие проблемы, но и предоставляем прогнозы развития заболеваний
                                на основе исторических данных и текущих климатических условий. Это позволяет планировать
                                профилактические меры и предотвращать распространение болезней.
                            </p>
                        </div>
                        <div className="card light-green-card">
                            <h3>Поддержка и консультации</h3>
                            <p>
                                Наши специалисты всегда готовы предоставить консультации и поддержку по вопросам
                                использования технологий и оптимизации процессов мониторинга и лечения растений. Мы
                                стремимся к долгосрочному сотрудничеству и успеху наших клиентов.
                            </p>
                        </div>
                    </div>

                </div>

            </div>
            <Footer/>
        </div>

    );
}

export default Home;
