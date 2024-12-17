import env_register  # noqa

try:
    from .db import db
except ImportError:
    from db import db
from sqlalchemy.ext.mutable import MutableList

from flask import current_app
from flask_bcrypt import generate_password_hash, check_password_hash

from redis.exceptions import RedisError
from rq.exceptions import NoSuchJobError
from rq.job import Job
from typing import Self, Union, NoReturn
import json
import pytz
from sqlalchemy import asc as sql_asc_sort

from datetime import datetime

from kallosus_packages.over_logging import GetTraceback

get_traceback = GetTraceback(__file__)


def db_rollback() -> NoReturn:
    """
    :return: `NoReturn`
    """

    db.session.rollback()


# Note: Точная копия этого файла лежит на всех серверах
class User(db.Model):
    __tablename__ = 'user'
    """
    Название таблицы
    """

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    """
    id элемента таблицы
    """

    email = db.Column(db.String(255), unique=True, nullable=False)
    """
    Почта пользователя
    """

    company = db.Column(db.String(255), nullable=False)
    """
    Компания, которую представляет пользователь
    """

    password = db.Column(db.String(500), nullable=False)
    """
    Пароль пользователя
    """

    mailing = db.Column(db.Boolean, default=False, nullable=False)
    """
    Подписан ли пользователь на рассылку
    """

    role = db.Column(db.Enum('admin', 'user', 'support', 'moderator', 'analyst', name='user_roles'),
                     default='user',
                     nullable=False,
                     )
    """
    Роль пользователя.
    Возможные роли: 'admin', 'user', 'support', 'moderator', 'analyst'
    """

    last_login_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Moscow')), nullable=False)
    """
    Дата последнего входа в аккаунт по Московскому времени
    """

    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Moscow')), nullable=False)
    """
    Дата создания записи по Московскому времени
    """

    def update_role(self, new_role: str) -> NoReturn:
        """
        Обновляет роль пользователя.
        :param new_role: Новая роль пользователя admin/user/support/moderator/analyst.
        :return: `NoReturn`
        """

        self.role = new_role
        self.save_to_db()

    def update_last_login(self) -> NoReturn:
        """
        Обновляет поле last_login_at текущей датой и временем.
        :return: `NoReturn`
        """

        self.last_login_at = datetime.now()
        self.save_to_db()

    def update_email(self, new_email: str) -> NoReturn:
        """
        Устанавливает новый email для пользователя.
        :param new_email: Новый email пользователя
        :return: `NoReturn`
        """

        self.email = new_email
        self.save_to_db()

    def update_company(self, new_company: str) -> NoReturn:
        """
        Устанавливает новый email для пользователя.
        :param new_company: Новое название организации пользователя
        :return: `NoReturn`
        """

        self.company = new_company
        self.save_to_db()

    def hash_password(self) -> NoReturn:
        """
        :return: `NoReturn`

        Хэш-пароля с использованием `flask_bcrypt`
        """

        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password: str) -> bool:
        """
        :param password: Пароль пользователя в виде обычной строки (не хэш)

        :return: bool - тот же пароль, или нет
        """

        return check_password_hash(self.password, password)

    def update_password(self, password: str) -> NoReturn:
        """
        :param password: Новый пароль пользователя (не зашифрованный)

        :return: `NoReturn`
        Обновляем пароль пользователя, хэшируем его и сохраняем в БД
        """

        self.password = password
        self.hash_password()
        self.save_to_db()

    def json(self) -> dict:
        """
        :return: Вся информация о пользователе в формате `dict`
        """

        data = {
            'id': self.id,
            'email': self.email,
            'company': self.company,
            'password': self.password,
            'mailing': self.mailing,
            'role': self.role,
            'last_login_at': str(self.last_login_at),
            'created_at': str(self.created_at),
        }

        return data

    def save_to_db(self) -> NoReturn:
        """
        :return: `NoReturn`

        Сохраняем пользователя в БД
        """

        db.session.add(self)  # session - коллекция объектов для базы данных
        db.session.commit()

    def delete_from_db(self) -> NoReturn:
        """
        :return: `NoReturn`

        Удаляем текущего пользователя из БД
        """

        db.session.delete(self)
        db.session.commit()

    def set_subscribe(self, subscribe: bool) -> NoReturn:
        """
        :param subscribe: Подписаться ли на рассылку
        :return: class 'database.models.User'
        """

        self.mailing = subscribe
        self.save_to_db()

    @classmethod
    def find_by_email(cls, email: str) -> Self:
        """
        :param email: Почта пользователя
        :return: class 'database.models.User'

        Поиск пользователя по электронной почте
        """

        return cls.query.filter_by(email=email).first()  # SELECT * FROM users

    @classmethod
    def find_by_id(cls, _id: int) -> Self:
        """
        :param _id: id пользователя
        :return: class 'database.models.User'

        Поиск пользователя по id
        """

        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_all(cls) -> list[Self]:
        """
        :return: list 'database.models.User'

        Возврат всех пользователей отсортированных по id
        """

        return cls.query.order_by(sql_asc_sort(User.id)).all()


class Task(db.Model):
    __tablename__ = 'task'
    """
    Название таблицы
    """

    id = db.Column(db.BigInteger, primary_key=True, unique=True, autoincrement=True, nullable=False)
    """
    id элемента таблицы
    """

    job_id = db.Column(db.String(36), nullable=True)
    """
    Job id, пример: 368d4eb4-b733-42c8-a005-f8d4843808e2
    """

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    """
    Связь с базой данных пользователя на другом веб-сервере
    ondelete='CASCADE' указывает SQLAlchemy на использование каскадного удаления при удалении записей из таблицы Task,
     что приведет к автоматическому удалению связанных записей из таблицы User.
    """

    status = db.Column(db.String(36), default='queue', nullable=False)
    """
    Статус задачи, один из: queue, run, complete, stopped, error
    """
    _STATUSES = ['queue', 'run', 'complete', 'stopped', 'error']

    user_current_time_folders = db.Column(MutableList.as_mutable(db.PickleType), default=[])
    """
    Пути к папкам пользователя, где лежат src видео:
    S3/user_id/dd_mm_yy/time
    `[S3/user_id_1/dd_mm_yy/time, S3/user_id_1/dd_mm_yy/time2]`
    """

    queue_files = db.Column(MutableList.as_mutable(db.PickleType), default=[])
    """
    `.mp4, .jpg, .png` файлы, которые должны быть обработаны моделью ML
    `[file.mp4, file2.mp4]`
    """

    done_res_files = db.Column(MutableList.as_mutable(db.PickleType), default=[])
    """
    Список json файлов, которые уже обработаны
    """

    is_files_upload = db.Column(db.Text, nullable=True)
    """
    `dict` объект, показывающей, сохранены ли успешно все файлы, если хоть что-то False,
    то может быть ошибка:
        {'test-videos/cars_test.mp4': [
            {'video': True}, - Загружено ли выходное видео в S3
            {'image_1': True}, {'image_2': True}, {'image_3': True}, {'image_4': True}, - Загружены ли изображения в S3
            {'res-file': True} - Загружен ли json в S3
            ]
        }
    """

    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Moscow')), nullable=False)
    """
    Дата создания записи по Московскому времени
    """

    @property
    def upload_data(self) -> dict:
        """
        :return:
        Достаем из в БД `is_files_upload`
        """

        return json.loads(self.is_files_upload) if self.is_files_upload else self.is_files_upload

    @upload_data.setter
    def upload_data(self, upload_data: dict) -> NoReturn:
        """
        :return:
        Заносим в БД `is_files_upload`
        """

        self.is_files_upload = json.dumps(upload_data)

    def launch_task(self, *args, **kwargs) -> NoReturn:
        """
        :param args: необходимые аргументы для запуска задачи
        :param kwargs: необходимые аргументы для запуска задачи (`images`, `user_folder`,  `is_remove`, `sleep`)
        :return: `NoReturn`
        """

        self.status = 'queue'

        try:
            meta = {
                'task_id': self.id,
            }

            rq_job = current_app.task_queue.enqueue('task.predict.predict_on_video',
                                                    *args,
                                                    **kwargs,
                                                    meta=meta,
                                                    job_timeout=-1,
                                                    )
        except ValueError as e:
            get_traceback.error(f'{e}')
            raise ValueError('You must run rq worker and app in the same folder')

        job_id = rq_job.get_id()

        self.job_id = job_id

        db.session.commit()

    def finish_task(self, output_files: list, is_files_upload: dict, error: bool = False) -> NoReturn:
        """
        :param output_files: путь к выходным файлам
        :param is_files_upload: `dict` объект, показывающей, сохранены ли успешно все файлы
        :param error: если задание завершено с ошибкой, меняем статус задачи в БД
        :return: `NoReturn`
        """

        if not error:
            self.status = 'complete'
            self.done_res_files = output_files
            self.upload_data = is_files_upload
        else:
            self.status = 'error'

        self.queue_files.clear()

        db.session.commit()

    def get_rq_job(self) -> Union[Job, None]:
        """
        :return: `Job`
        """

        try:
            rq_job = Job.fetch(self.job_id, connection=current_app.redis)
        except (RedisError, NoSuchJobError):
            return None

        return rq_job

    def get_progress(self) -> Union[float, int]:
        """
        :return: Прогресс выполнения `float`/`int`
        """

        job = self.get_rq_job()

        return job.meta.get('progress', 0) if job is not None else 100

    def json(self) -> dict:
        """
        :return: Полная информация о пользователе типа `dict`
        """

        data = {
            'id': self.id,
            'job_id': self.job_id,
            'user_id': self.user_id,
            'status': self.status,
            'user_current_time_folders': self.user_current_time_folders,
            'queue_files': self.queue_files,
            'done_res_files': self.done_res_files,
            'is_files_upload': self.upload_data,
            'date': str(self.date),
        }

        return data

    def set_status(self, status: str):
        if status not in self._STATUSES:
            raise ValueError(f'status must be one of {self._STATUSES}')

        self.status = status
        self.save_to_db()

    def save_to_db(self) -> NoReturn:
        """
        :return: `NoReturn`
        Сохранить задачу в `db`
        """

        db.session.add(self)  # session - коллекция объектов для базы данных
        db.session.commit()

    def delete_from_db(self) -> NoReturn:
        """
        :return: `NoReturn`
        Удаляем задачу из `db`
        """

        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_job_id(cls, job_id: str) -> Self:
        """
        :param job_id: id задачи
        :return: class 'database.models.User'
        Получаем сущность БД по `job_id`
        """

        return cls.query.filter_by(job_id=job_id).first()

    @classmethod
    def find_by_user_id(cls, user_id: int, first: bool = True) -> Self:
        """
        :param user_id: id пользователя
        :param first: Получить только первую запись

        :return: class 'database.models.User'
        Получаем сущности БД по `user_id`
        """

        rec = cls.query.filter_by(user_id=user_id)

        if first:
            rec = rec.first()
        else:
            rec = rec.all()

        return rec

    @classmethod
    def find_by_id(cls, task_id: int) -> Self:
        """
        :param task_id: id задачи

        :return: class 'database.models.Task'

        Поиск задачи по id (уникальная)
        """

        rec = cls.query.filter_by(id=task_id).first()

        return rec


if __name__ == '__main__':
    from app import KallosusNNApplication
    from database.models import User, Task

    app = KallosusNNApplication().create_app()

    with app.app_context():
        user = User.find_by_email('test0@gmail.com')
        if not user:
            user = User(email='test0@gmail.com',
                        password='TEST',
                        company='Test corp',
                        )
            user.save_to_db()

        task = Task(user_id=user.id,
                    job_id='abc' * 12,
                    queue_files=[],
                    done_res_files=['file1.json', 'file2.json'],
                    user_current_time_folders=[f'data-test/{user.id}'],
                    upload_data={'test-videos/cars_test.mp4':
                        [
                            {'video': True},
                            {'image_1': True}, {'image_2': True}, {'image_3': True}, {'image_4': True},
                            {'res-file': True}
                        ]
                    }
                    )

        task.save_to_db()

        print(user.json())
        print(task.json())
