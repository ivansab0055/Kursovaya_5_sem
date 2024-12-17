import os
from typing import NoReturn

import rq
import rq_dashboard
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Api
from kallosus_packages.over_logging import Logger
from redis import Redis

import env_register  # noqa
from config import DEBUG
from database.db import initialize_db
from path_definitions import current_path, ENV_KALLOSUS_PROD, ENV_KALLOSUS_DEV, ENV_KALLOSUS_TEST
from resources.errors import ERRORS
from resources.routes import initialize_routes

console_logger = Logger(__file__)
console_logger.info(f'ROOT PATH: {current_path}')


class KallosusNNApplication:
    def __init__(self):
        self._app = None
        self._api = None
        self._limiter = None
        self._jwt_manager = None

    def get_app(self) -> Flask:
        """
       :return: `Flask`

       Получаем объект текущего класса приложения `self._app`
       """

        return self._app

    def get_limiter(self) -> Limiter:
        return self._limiter

    def _init_api(self) -> NoReturn:
        self._api = Api(self._app, errors=ERRORS)
        console_logger.info('REST-API initialized')

    def _init_jwt(self) -> NoReturn:
        self._jwt_manager = JWTManager(self._app)
        console_logger.info('JWTManager initialized')

    def _init_redis(self) -> NoReturn:
        self._app.redis = Redis.from_url(self._app.config['KALLOSUS_REDIS_URL'])
        self._app.task_queue = rq.Queue('pd-task', connection=self._app.redis)
        console_logger.info('Redis initialized')

    def _init_db(self) -> NoReturn:
        initialize_db(self._app)
        console_logger.info('DB initialized')

    def _init_routes(self) -> NoReturn:
        initialize_routes(self._api)
        console_logger.info('Routes initialized')

    def _init_limiter(self):
        # Настройка Limiter
        self._app.limiter = Limiter(
            get_remote_address,  # Получает IP-адрес клиента
            app=self._app,
            default_limits=["100 per minute"],  # Ограничение 1000 запросов в минуту
            storage_uri=f"{self._app.config['KALLOSUS_REDIS_URL']}/1",
        )
        console_logger.info('Limiter initialized')

    def _init_rq_dashboard(self) -> NoReturn:
        """
        :return:
        В Docker запускается отдельный сервис `rq-dashboard`, так что надобности
        в инициализации внутри приложения в продакшене нет.
        """

        self._app.config.from_object(rq_dashboard.default_settings)
        rq_dashboard.web.setup_rq_connection(self._app)

        self._app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
        console_logger.info('RQ dashboard initialized')

    def create_app(self) -> Flask:
        """
        :return: Flask application
        """

        self._app = Flask(__name__)
        log_path = os.environ.get("LOG_PATH")
        console_logger.debug(
            f'self._app.config["DEBUG"]: {self._app.config["DEBUG"]}; env debug: {DEBUG}; LOG_PATH: {None if not log_path else log_path}')

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

        self._app.config.from_pyfile(env)
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
        self._init_jwt()
        self._init_redis()

        self._init_limiter()

        self._init_rq_dashboard()

        self._init_db()

        self._init_routes()

        return self._app
