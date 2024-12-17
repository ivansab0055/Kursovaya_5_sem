import React, {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";
import {
    AdminGetAllUsers,
    AdminLoginAsUser,
    AdminUserDelete,
    AdminUserUpdate,
    confirmAccess,
    refreshToken
} from '../Modules/Web-server_queries';
import {format} from "date-fns";
import styles from './AdminLK.module.css';
import Alert from "../Modules/Alert";

function AdminLK() {
    const navigate = useNavigate();
    const [errorMessage, setErrorMessage] = useState('');
    const [open, setOpen] = useState(false);
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [isEditingUserData, setIsEditingUserData] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('');
    const [mailing, setMailing] = useState(false);
    const [company, setCompany] = useState('');
    const [serverEmail, setServerEmail] = useState('');
    const storedAccessToken = localStorage.getItem('accessToken');
    const storedRefreshToken = localStorage.getItem('refreshToken');

    useEffect(() => {
        if (!(storedAccessToken && storedRefreshToken)) {
            navigate('/login');
        }

        confirmAccess(storedAccessToken)
            .then(responseData => {
                if (responseData.role !== 'admin') {
                    navigate('/lk');
                } else {
                    setServerEmail(responseData.email)
                    fetchAllUsers();
                }
            })
            .catch(error => {
                handleAuthError(error);
            });
    }, [navigate, storedAccessToken, storedRefreshToken]);

    const handleAuthError = (error) => {
        let message;
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    refreshToken(storedRefreshToken)
                        .then(responseData => {
                            localStorage.setItem('accessToken', responseData.access_token);
                            window.location.href = '/adminlk';
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


    };
    useEffect(() => {
        // Set the initial role to 'admin' if selectedUser.role is 'admin'
        if (selectedUser)
            setRole(selectedUser.role === 'admin' ? 'admin' : 'user');
    }, [selectedUser]); // Runs whenever selectedUser changes
    const fetchAllUsers = () => {
        AdminGetAllUsers(storedAccessToken)
            .then(responseData => {
                setUsers(Object.values(responseData));
            })
            .catch(error => {
                setErrorMessage(`Ошибка загрузки списка пользователей: ${error}`);
                setOpen(true);
            });
    };

    const formatDateTime = (dateTime) => {
        return format(new Date(dateTime), "dd.MM.yyyy; HH:mm:ss");
    };

    const handleViewOrEdit = (user) => {
        setSelectedUser(user);
        setIsEditingUserData(false);
    };

    const handleEditUserData = () => {
        setIsEditingUserData(true);
    };

    const handleSaveUserData = () => {
        const updateData = {};
        if (email) updateData.email = email;
        if (password) updateData.password = password;
        if (role) updateData.role = role;
        if (company) updateData.company = company;
        if (updateData) {
            AdminUserUpdate(storedAccessToken, selectedUser.id, updateData)
                .then(() => {
                    setSelectedUser({...selectedUser, ...updateData});
                    setIsEditingUserData(false);
                    fetchAllUsers();
                })
                .catch(error => {
                    setErrorMessage(`Ошибка сохранения изменений:${error}`);
                    setOpen(true);
                });
        } else {
            setErrorMessage('Сделайте хотя бы одно изменение!')
            setOpen(true)
        }
    };

    const handleDeleteAccount = (userId) => {
        AdminUserDelete(storedAccessToken, userId)
            .then(() => {
                setUsers(users.filter(user => user.id !== userId));
                setSelectedUser(null);
            })
            .catch(error => {
                setErrorMessage(`Ошибка удаления пользователя: ${error}`);
                setOpen(true);
            });
    };

    const handleLoginAsUser = () => {
        AdminLoginAsUser(storedAccessToken, selectedUser.id)
            .then(result => {
                localStorage.setItem('accessToken', result.access_token);
                navigate('/lk');
            })
            .catch(error => {
                setErrorMessage(`Ошибка входа как пользователь. ${error}`);
                setOpen(true);
            });
    };

    const closeEditModal = () => setSelectedUser(null);

    return (
        <div className={styles.mainContent}>
            <Alert mode={'error'} message={errorMessage} open={open} setOpen={setOpen}/>
            <h2>Консоль администратора</h2>
            <p className="consent-text">
                {serverEmail}
            </p>
            <div className={styles.userTable}>
                <table>
                    <thead>
                    <tr>
                        <th>ID</th>
                        <th>Email</th>
                        <th>Компания</th>
                        <th>Роль</th>
                        <th>Последний вход</th>
                        <th>Действия</th>
                    </tr>
                    </thead>
                    <tbody>
                    {users.map(user => (
                        <tr key={user.id}>
                            <td>{user.id}</td>
                            <td>{user.email}</td>
                            <td>{user.company}</td>
                            <td>{user.role}</td>
                            <td>{formatDateTime(user.last_login_at)}</td>
                            <td>
                                <button onClick={() => handleViewOrEdit(user)}>
                                    {user.role === "admin" ? "Просмотреть" : "Изменить"}
                                </button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>

            {selectedUser && !isEditingUserData && (
                <div className={styles.modal}>
                    <div className={styles.modalContent}>
                        <Alert mode={'error'} message={errorMessage} open={open} setOpen={setOpen}/>
                        <h3>{selectedUser.role === "admin" ? "Информация о пользователе (Администратор)" : "Информация о пользователе"}</h3>
                        <p><b>ID:</b> {selectedUser.id}</p>
                        <p><b>Email:</b> {selectedUser.email}</p>
                        <p><b>Компания:</b> {selectedUser.company}</p>
                        <p><b>Роль:</b> {selectedUser.role}</p>
                        <p><b>Последний вход:</b> {formatDateTime(selectedUser.last_login_at)}</p>
                        <p><b>Создан:</b> {formatDateTime(selectedUser.created_at)}</p>
                        <p><b>Рассылка:</b> {selectedUser.mailing ? "Да" : "Нет"}</p>
                        {selectedUser.role !== "admin" && (
                            <div className={styles.buttonGroup}>
                                <button onClick={handleEditUserData}>Изменить данные пользователя</button>
                                <button onClick={handleLoginAsUser}>Войти как пользователь</button>
                                <button className={styles.deleteButton}
                                        onClick={() => handleDeleteAccount(selectedUser.id)}>
                                    Удалить пользователя
                                </button>
                            </div>
                        )}
                        <button onClick={closeEditModal}>Закрыть</button>
                    </div>
                </div>
            )}

            {selectedUser && isEditingUserData && (
                <div className={styles.modal}>
                    <div className={styles.modalContent}>
                        <Alert mode={'error'} message={errorMessage} open={open} setOpen={setOpen}/>
                        <h3>Изменение данных пользователя</h3>
                        <p>Если не хотите менять что-то, оставьте поле пустым.</p>
                        <div className={styles.adminField}>
                            <label>Email:</label>
                            <input
                                type="email"
                                placeholder={selectedUser.email}
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                        <div className={styles.adminField}>
                            <label>Пароль:</label>
                            <input
                                type="password"
                                placeholder="Пароль"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                        <div className={styles.adminField}>
                            <label>Компания:</label>
                            <input
                                type="text"
                                placeholder={selectedUser.company}
                                value={company}
                                onChange={(e) => setCompany(e.target.value)}
                            />
                        </div>
                        <div className={styles.adminField}>
                            <label>Роль:</label>
                            <select
                                value={role}
                                onChange={(e) => setRole(e.target.value)} // Update state on change
                            >
                                <option className={styles.option} value="user">Пользователь</option>
                                <option className={styles.option} value="admin">Админ</option>
                                <option className={styles.option} value="support">ТехПоддержка</option>
                                <option className={styles.option} value="moderator">Модератор</option>
                                <option className={styles.option} value="analyst">Аналитик</option>
                            </select>
                        </div>



                        <button onClick={handleSaveUserData}>Сохранить</button>
                        <button onClick={() => setIsEditingUserData(false)}>Отмена</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default AdminLK;
