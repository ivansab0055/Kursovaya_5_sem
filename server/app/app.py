import os
from typing import NoReturn

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_restful import Api
from kallosus_packages.over_logging import Logger

import env_register  # noqa
from config import DEBUG
from database.db import initialize_db
from path_definitions import ENV_KALLOSUS_PROD, ENV_KALLOSUS_DEV, ENV_KALLOSUS_TEST
from path_definitions import current_path
from resources.errors import ERRORS
from resources.routes import initialize_routes

console_logger = Logger(__file__)


class KallosusApplication:
    def __init__(self):
        self._app = None
        self._api = None
        self._bcrypt = None
        self._jwt_manager = None
        self._mail = None

    def get_app(self) -> Flask:
        """
        :return: `Flask`

        Получаем объект текущего класса приложения `self._app`
        """

        return self._app

    def get_mail(self) -> Mail:
        """
        :return: `Mail`

        Получаем объект текущего класса Mail для взаимодействия с почтой `self._mail`
        """

        return self._mail

    def _init_api(self) -> NoReturn:
        """
        Инициализирует REST API с использованием Flask-RESTful.

        Создает экземпляр `Api`, который связывает приложение с
        пользовательскими обработчиками ошибок из `ERRORS`.

        :return: `NoReturn`
        """

        self._api = Api(self._app, errors=ERRORS)
        console_logger.info('REST-API initialized')

    def _init_bcrypt(self) -> NoReturn:
        """
        Инициализирует Bcrypt для безопасного хэширования паролей.

        Создает экземпляр `Bcrypt` с привязкой к Flask-приложению,
        что позволяет использовать функции для создания и проверки хэшей паролей.

        :return: `NoReturn`
        """

        self._bcrypt = Bcrypt(self._app)
        console_logger.info('Bcrypt initialized')

    def _init_jwt(self) -> NoReturn:
        """
        Инициализирует JWT (JSON Web Token) менеджер.

        Создает экземпляр `JWTManager` для управления токенами
        в приложении, используя JSON Web Tokens для аутентификации.

        :return: `NoReturn`
        """

        self._jwt_manager = JWTManager(self._app)
        console_logger.info('JWTManager initialized')

    def _init_mail(self) -> NoReturn:
        """
        Инициализирует почтовую службу для отправки писем.

        Создает экземпляр `Mail`, который позволяет приложению
        отправлять электронные письма, используя конфигурацию
        из приложения Flask.

        :return: `NoReturn`
        """

        self._mail = Mail(self._app)
        console_logger.info('Mail initialized')

    def _init_db(self) -> NoReturn:
        """
        Инициализирует подключение к базе данных.

        Вызывает `initialize_db`, чтобы установить соединение
        и инициализировать доступ к базе данных в приложении.

        :return: `NoReturn`
        """

        initialize_db(self._app)
        console_logger.info('DB initialized')

    def _init_routes(self) -> NoReturn:
        """
        Инициализирует маршруты API для приложения.

        Вызывает `initialize_routes`, чтобы зарегистрировать
        доступные маршруты в приложении, связывая их с `Api`.

        :return: `NoReturn`
        """

        initialize_routes(self._api)
        console_logger.info('Routes initialized')

    def _init_limiter(self) -> NoReturn:
        """
        Настройка Limiter
        :return: `NoReturn`
        Не забудьте запустить сервис redis
        """

        self._app.limiter = Limiter(
            get_remote_address,  # Получает IP-адрес клиента
            app=self._app,
            default_limits=["100 per minute"],  # Ограничение 100 запросов в минуту
            storage_uri=f"{self._app.config['KALLOSUS_REDIS_URL']}/1",
        )
        console_logger.info('Limiter initialized')

    def create_app(self) -> Flask:
        """
        :return: `Flask`

        Развертываем (создаем) приложение
        """

        self._app = Flask(__name__)
        log_path = os.environ.get("LOG_PATH")
        console_logger.debug(
            f'self._app.config["DEBUG"]: {self._app.config["DEBUG"]}; env debug: {DEBUG}; LOG_PATH: {None if not log_path else log_path}, UNIT_TEST: {os.environ.get("UNIT_TEST")}')

        if DEBUG:
            CORS(self._app, resources={r"/api/*": {"origins": "*"}})
        else:
            CORS(self._app, resources={r"/api/*": {"origins": "https://kallosus.ru"}})

        if not DEBUG:
            env = ENV_KALLOSUS_PROD
        elif os.environ.get('UNIT_TEST') in ['0', None]:
            env = ENV_KALLOSUS_DEV
        else:
            env = ENV_KALLOSUS_TEST

        with open(env) as f:
            lines = ''.join(f.readlines())

        console_logger.debug(f'\n{lines}')

        # Инициализируем переменные среды для приложения из файла `config_dev.py`
        self._app.config.from_pyfile(env)
        self._app.config['TEMPLATE'] = os.path.join(current_path, self._app.template_folder)
        self._app.config['STATIC'] = os.path.join(current_path, self._app.static_folder)
        console_logger.info(f'Configured using {env}')

        if 'SQLALCHEMY_DATABASE_URI' in os.environ:
            if os.environ.get('UNIT_TEST') in ['0', None]:
                self._app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
                console_logger.info(
                    f'SQLALCHEMY_DATABASE_URI: {os.environ.get("SQLALCHEMY_DATABASE_URI")} in `os.environ`')
            else:
                self._app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_TEST_URI')
                console_logger.info(
                    f'SQLALCHEMY_DATABASE_TEST_URI: {os.environ.get("SQLALCHEMY_DATABASE_TEST_URI")} in `os.environ`')

        self._init_api()
        self._init_bcrypt()
        self._init_jwt()
        self._init_mail()
        self._init_limiter()
        self._app.mail = self._mail

        self._init_db()

        self._init_routes()

        return self._app


app = KallosusApplication().create_app()
