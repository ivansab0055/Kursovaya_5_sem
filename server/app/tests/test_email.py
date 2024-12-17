from typing import NoReturn

from flask import current_app, render_template
from kallosus_packages.over_logging import Logger

from services.mail_service import send_email
from tests.BaseCase import BaseCase

console_logger = Logger(__file__)

RECIPIENT = 'pikromat1995@gmail.com'
SITE_URL = 'https://kallosus.ru'


class TestResetPasswordEmail(BaseCase):
    def test_send_confirm(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешную отправку письма для подтверждения почты
        """

        with self.app.app_context():
            hours = 24

            msg, status = send_email(subject='[Kallosus] Подтвердите свою почту',
                                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                                     recipients=[RECIPIENT],
                                     text_body=render_template('confirm_email/confirm_email.txt',
                                                               url=SITE_URL + '/CONFIRM_URL',
                                                               expires=str(hours),
                                                               support_email=current_app.config['SUPPORT_EMAIL'],
                                                               ),
                                     html_body=render_template('confirm_email/confirm_email.html',
                                                               url=SITE_URL + '/CONFIRM_URL',
                                                               expires=str(hours),
                                                               support_email=current_app.config['SUPPORT_EMAIL'],
                                                               ),
                                     )

        self.assertEqual('Email send', msg['message'])
        self.assertEqual(200, status)

    def test_send_successfully_sign_up(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешную отправку письма о том, что пользователь зарегистрирован
        """

        with self.app.app_context():
            msg, status = send_email(subject='[Kallosus] Почта успешно подтверждена',
                                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                                     recipients=[RECIPIENT],
                                     text_body=render_template('email_confirmed/confirmed.txt',
                                                               url=SITE_URL,
                                                               support_email=current_app.config['SUPPORT_EMAIL'],
                                                               ),
                                     html_body=render_template('email_confirmed/confirmed.html',
                                                               url=SITE_URL,
                                                               support_email=current_app.config['SUPPORT_EMAIL'],
                                                               ),
                                     )

        self.assertEqual('Email send', msg['message'])
        self.assertEqual(200, status)

    def test_send_forgot_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешную отправку письма сброса пароля
        """

        with self.app.app_context():
            hours = 24

            msg, status = send_email(subject='[Kallosus] Сброс пароля',
                                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                                     recipients=[RECIPIENT],
                                     text_body=render_template('reset_password/reset_password.txt',
                                                               url=SITE_URL + '/RESET_TOKEN',
                                                               expires=str(hours),
                                                               support_email=current_app.config['SUPPORT_EMAIL'],
                                                               ),
                                     html_body=render_template('reset_password/reset_password.html',
                                                               url=SITE_URL + '/RESET_TOKEN',
                                                               expires=str(hours),
                                                               support_email=current_app.config['SUPPORT_EMAIL'],
                                                               ),
                                     )

        self.assertEqual('Email send', msg['message'])
        self.assertEqual(200, status)

    def test_send_successfully_reset_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешную отправку письма, информирующего о том, что пароль сброшен
        """

        with self.app.app_context():
            msg, status = send_email(subject='[Kallosus] Пароль успешно сброшен',
                                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                                     recipients=[RECIPIENT],
                                     text_body=render_template('pwd_reset_successfully/reset.txt',
                                                               url=SITE_URL,
                                                               support_email=current_app.config['SUPPORT_EMAIL'],
                                                               ),
                                     html_body=render_template('pwd_reset_successfully/reset.html',
                                                               url=SITE_URL,
                                                               support_email=current_app.config['SUPPORT_EMAIL'],
                                                               ),
                                     )

        self.assertEqual('Email send', msg['message'])
        self.assertEqual(200, status)

    def test_send_successfully_changed_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешную отправку письма, информирующего о том, что пароль изменен
        """

        with self.app.app_context():
            msg, status = send_email(subject='[Kallosus] Пароль успешно изменен',
                                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                                     recipients=[RECIPIENT],
                                     text_body=render_template('change_password/changed.txt',
                                                               support_email=current_app.config['SUPPORT_EMAIL'],
                                                               ),
                                     html_body=render_template('change_password/changed.html',
                                                               support_email=current_app.config['SUPPORT_EMAIL'],
                                                               ),
                                     )

        self.assertEqual('Email send', msg['message'])
        self.assertEqual(200, status)

    def test_send_test_email(self) -> NoReturn:
        """
        :return: `NoReturn`
        Только для mail.ru
        Сообщение может находиться в папке "спам".
        Отключите группировку сообщений в 'мою' папку
        """

        subj = 'Test email'
        with self.app.app_context():
            msg, status = send_email(subject=subj,
                                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                                     recipients=[current_app.config['MAIL_DEFAULT_SENDER']],
                                     text_body=render_template('test/test.txt',
                                                               url='test_send_test_email',
                                                               ),
                                     html_body=render_template('test/test.html',
                                                               url='test_send_test_email',
                                                               ),
                                     )

        subject, letter_from, message = self.read_mail(successfully_subject=subj,
                                                       delete_successfully_read_msg=True,
                                                       )

        self.assertEqual('Test email', subject)
        self.assertEqual('Email send', msg['message'])
        self.assertEqual(200, status)
