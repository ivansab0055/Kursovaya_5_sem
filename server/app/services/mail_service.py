import time
from threading import Thread
from typing import NoReturn

from flask import Flask
from flask_mail import Message
from kallosus_packages.over_logging import Logger

import env_register  # noqa
from resources.errors import InternalServerError

console_logger = Logger(__file__)


def _send_async_email(app: Flask, msg: Message) -> NoReturn:
    """
    :param app: Flask application
    :param msg: сообщение в формате html/text
    :return: `NoReturn`
    """

    with app.app_context():
        try:
            app.mail.send(msg)
            console_logger.debug('Email send successfully')
            time.sleep(1)
        except ConnectionRefusedError:
            raise InternalServerError("[MAIL SERVER] not working")


def send_email(subject: str, sender: str, recipients: list, text_body: str, html_body: str) -> NoReturn:
    """
    :param subject: Тема письма
    :param sender: Отправитель
    :param recipients: Получатели
    :param text_body: Текст сообщения в формате txt
    :param html_body: Текст сообщения в формате html
    :return: `NoReturn`
    Вместо передачи current_app напрямую, мы используем `_get_current_object()` для получения актуального объекта current_app.
    Это важно, чтобы корректно передать контекст приложения внутри потока.
    """

    from flask import current_app

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=_send_async_email, args=(current_app._get_current_object(), msg)).start()

    return {'message': 'Email send'}, 200


if __name__ == '__main__':
    from config.config_dev import MAIL_DEFAULT_SENDER
    from flask import render_template
    from app import KallosusApplication

    app = KallosusApplication().create_app()

    with app.app_context():
        send_email('Test',
                   MAIL_DEFAULT_SENDER,
                   ['pikromat1995@gmail.com'],
                   render_template('test/test.txt',
                                   url='test',
                                   ),
                   render_template('test/test.html',
                                   url='test',
                                   ),
                   )
