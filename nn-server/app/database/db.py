from typing import NoReturn

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy import inspect

naming_convention = {
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention), engine_options={"pool_pre_ping": True})
migrate = Migrate()


def initialize_db(app: Flask) -> NoReturn:
    """
    :param app: Flask application instance
    :return: `NoReturn`
    Инициализация БД, создание ее и создание таблиц
    """

    db.init_app(app)
    migrate.init_app(app, db)
    create_tables(app)


def create_tables(app: Flask) -> NoReturn:
    """
    :param app: Flask application instance
    :return: `NoReturn`
    Создаем все таблицы SQLAlchemy
    """

    with app.app_context():
        db.create_all()


def is_table_exists(table_name: str) -> bool:
    inspector = inspect(db.engine)
    return inspector.has_table(table_name)
