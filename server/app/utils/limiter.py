import os

from flask import current_app
from flask_limiter.extension import LimitDecorator
from flask_limiter.util import get_remote_address


def apply_limits(limit: str):
    """
    :param limit: Лимит 0/minute
    :return:
    """

    if os.getenv('LIMITER_LIMIT'):
        limit = os.getenv('LIMITER_LIMIT')

    # Создайте декоратор лимита вручную
    limit_decorator = LimitDecorator(
        current_app.limiter,
        limit_value=limit,  # Лимит в n запросов
        key_func=get_remote_address  # Функция для получения ключа
    )
    # Вызовите метод __enter__ декоратора
    limit_decorator.__enter__()
