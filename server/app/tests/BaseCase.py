import os

os.environ['UNIT_TEST'] = '1'  # noqa

import unittest

from app import KallosusApplication
from database.models import User, Task
from database.db import db
from kallosus_packages.over_logging import Logger
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                )
from flask_bcrypt import generate_password_hash
import imaplib
import email
from email.header import decode_header
import time
from datetime import timedelta
import codecs

from typing import NoReturn

console_logger = Logger(__file__)

os.environ['LIMITER_LIMIT'] = '1000 per minute'


class BaseCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаем тестовое приложение для всего класса
        cls.app = KallosusApplication().create_app()
        cls.app.config['TESTING'] = True

        # Пушим контекст
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        template = cls.app.config['TEMPLATE']
        static = cls.app.config['STATIC']

        console_logger.debug(f'TEMPLATE: {template}, STATIC: {static}')

        db.create_all()
        console_logger.debug(f'DB tables created')

        # Создаем тестовый клиент
        cls.test_client = cls.app.test_client()
        console_logger.debug(f'Test client created')

    def setUp(self):
        console_logger.info(f"[START]: {self.id().split('.')[-1]}")

        with self.app.app_context():
            if Task.query.first():
                db.session.query(Task).delete()
                db.session.commit()  # Применить изменения в базе данных
                console_logger.debug('Tasks removed')

            if User.query.first():
                db.session.query(User).delete()
                db.session.commit()
                console_logger.debug('Users removed')

            # Создаем тестового пользователя
            self.test_user_password = 'TESTPWD'
            self.test_user_email = 'test@gmail.com'
            self.test_user_data = {
                'email': self.test_user_email,
                'password': self.test_user_password,
                'role': 'user',
                'company': 'Test corp',
                'mailing': False,
            }
            self.test_user = User(email=self.test_user_email,
                                  password=generate_password_hash(self.test_user_password).decode('utf8'),
                                  company=self.test_user_data['company'],
                                  role=self.test_user_data['role'],
                                  mailing=self.test_user_data['mailing'],
                                  )

            self.test_user.save_to_db()
            self.test_user_id = self.test_user.id
            console_logger.info(f'Test User created {self.test_user_id}')

            # Создаем админа пользователя
            self.test_admin_password = 'ADMINTESTPWD'
            self.test_admin_email = 'admin@gmail.com'
            self.test_admin = User(email=self.test_admin_password,
                                   password=generate_password_hash(self.test_admin_password).decode('utf8'),
                                   company='Admin corp',
                                   role='admin',
                                   )

            self.test_admin.save_to_db()
            self.test_admin_id = self.test_admin.id
            console_logger.info(f'Test Admin created {self.test_admin_id}')

            # Создаем тестовые задачи
            self.clear_task = Task(user_id=self.test_user_id,
                                   job_id=None,
                                   queue_files=[],
                                   user_current_time_folders=[],
                                   )
            self.clear_task.save_to_db()
            self.clear_task_id = self.clear_task.id
            console_logger.info('clear_task Task 1 created')

            self.test_task = Task(user_id=self.test_user_id,
                                  job_id='a' * 36,
                                  queue_files=[],
                                  user_current_time_folders=[],
                                  )

            self.test_task.save_to_db()
            self.test_task_id = self.test_task.id
            console_logger.info('test_task Task 2 created')

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

        with cls.app.app_context():
            console_logger.debug(f'Remove Task and User elements in {db.engine.url.database} database...')
            try:
                if Task.query.first():
                    db.session.query(Task).delete()
                    db.session.commit()
                    console_logger.debug('Deleted all tasks successfully')

                if User.query.first():
                    db.session.query(User).delete()
                    db.session.commit()
                    console_logger.debug('Deleted all users successfully')
            except Exception as e:
                console_logger.error(f'Error during tearDown: {e}')
                db.session.rollback()

        console_logger.info("All the tests in this class are done")

    def read_mail(self,
                  successfully_subject: str,
                  timeout: int = 5,
                  total_attempts: int = 3,
                  mailbox: str = 'INBOX',
                  delete_successfully_read_msg: bool = False,
                  ) -> tuple[str | None, str | None, list | None]:
        """
        :param successfully_subject: Если тема прочитанного письма, как параметр, то сообщение дошло
        :param timeout: Сколько времени ждать, пока мы снова не прочитаем почтовый ящик
        :param total_attempts: Сколько попыток следует предпринять, пока сообщение не будет получено
        :param mailbox: Какой почтовый ящик (папка) читается, по умолчанию используется `INBOX`
        :param delete_successfully_read_msg: Нужно ли нам удалять уже успешно прочитанное сообщение
        :return: subject: str, letter_from: str, message: list
        """

        attempts = 1
        _subject = None

        username = self.app.config['MAIL_USERNAME']
        mail_pass = self.app.config['MAIL_PASSWORD']
        imap_server = self.app.config['IMAP_MAIL_SERVER']

        console_logger.debug(f'Username: {username}, PWD: {"*" * len(mail_pass)}, server: {imap_server}')

        imap = imaplib.IMAP4_SSL(imap_server)
        res = imap.login(username, mail_pass)

        if res[0] == 'OK':
            console_logger.debug('Connection to mail successful')
        else:
            console_logger.error('Connection to mail unsuccessful')
            self.fail('Connection to mail unsuccessful')
            self.__exit_from_mail(imap)

            return None, None, None

        while attempts <= total_attempts:
            time.sleep(timeout)

            inbox = imap.select(mailbox)

            if inbox[0] == 'OK':
                console_logger.debug(f'Successful get {mailbox}')
                unseen = imap.uid('search', 'UNSEEN', 'ALL')

                if unseen[0] == 'OK':
                    console_logger.debug(f'Successful get UNSEEN, {unseen[1]}')
                    ids = unseen[1][0].decode().split(' ')

                    if unseen[1][0]:

                        for mail_id in ids:
                            byte_mail_id = mail_id.encode()
                            console_logger.debug(f'mail id: {mail_id}, {byte_mail_id}')
                            res, msg_uid = imap.uid('fetch', byte_mail_id, '(RFC822)')
                            msg = email.message_from_bytes(msg_uid[0][1])

                            try:  # if cyrillic
                                _subject = ''
                                for i in range(len(decode_header(msg["Subject"]))):
                                    _subject += codecs.decode(decode_header(msg["Subject"])[i][0], 'utf-8')

                                _letter_from = msg['Return-path']
                                console_logger.debug('Subject decoded')
                            except(AttributeError, TypeError):
                                _subject = msg['Subject']
                                _letter_from = msg['Return-path']

                            _message = []
                            for part in msg.walk():
                                if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
                                    _message.append(part.get_payload())

                            console_logger.debug(f'Subject: {_subject}')
                            console_logger.debug(f'From: {_letter_from}')
                            console_logger.debug(f'Message: {_message}')

                            if _subject == successfully_subject:
                                if delete_successfully_read_msg:
                                    imap.uid('STORE', str(mail_id), '+FLAGS', '(\Deleted)')
                                    console_logger.debug('Email removed')

                                self.__exit_from_mail(imap)

                                return _subject, _letter_from, _message
                    else:
                        console_logger.error('No unread messages')
                else:
                    console_logger.error('Unsuccessful get UNSEEN')
            else:
                console_logger.error('Unsuccessful get INBOX')

            attempts += 1

        self.__exit_from_mail(imap)

        return None, None, None

    @staticmethod
    def __exit_from_mail(imap: imaplib.IMAP4_SSL) -> NoReturn:
        """
        :param imap: `IMAP4_SSL`
        :return: `NoReturn`
        """

        # безвозвратно удаляем сообщения, помеченные как удаленные,
        # из выбранного почтового ящика (в данном случае "ВХОДЯЩИЕ")
        imap.expunge()
        # закрываем mailbox
        imap.close()

        # выходим из аккаунта
        imap.logout()

    def _create_access(self, **kwargs):
        """
        :param kwargs: `timedelta` аргументы: hour, minutes, etc
        :return:
        """

        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id), expires_delta=timedelta(**kwargs))

        time.sleep(1)

        return access_token

    def _create_refresh(self, **kwargs):
        """
        :param kwargs: `timedelta` аргументы: hour, minutes, etc
        :return:
        """

        with self.app.app_context():
            refresh_token = create_refresh_token(identity=str(self.test_user_id), expires_delta=timedelta(**kwargs))

        time.sleep(1)

        return refresh_token

    def _create_confirm(self, **kwargs):
        """
        :param kwargs: `timedelta` аргументы: hour, minutes, etc
        :return:
        """

        with self.app.app_context():
            confirm_token = create_access_token(identity='email@cool.com',
                                                additional_claims={"email": '<email>', "password": '<hashed_pwd>',
                                                                   "company": '<company>'},
                                                expires_delta=timedelta(**kwargs),
                                                )
        time.sleep(1)

        return confirm_token

    def _create_reset(self, **kwargs):
        """
        :param kwargs: `timedelta` аргументы: hour, minutes, etc
        :return:
        """

        with self.app.app_context():
            reset_token = create_access_token(identity=str(self.test_user_id), expires_delta=timedelta(**kwargs))

        time.sleep(1)

        return reset_token
