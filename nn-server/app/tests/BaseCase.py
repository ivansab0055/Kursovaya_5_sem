import os

os.environ['UNIT_TEST'] = '1'  # noqa

import unittest

from app import KallosusNNApplication
from database.models import Task, User
from database.db import db
from kallosus_packages.over_logging import Logger

from path_definitions import current_path, tests_env_file
from storage import local_test_s3_path, remote_test_s3_path
import shutil
from typing import Union
from storage.S3 import StorageApi

if os.environ['DATA_STORAGE'] != 's3':
    raise EnvironmentError('DATA_STORAGE must be s3')

Storage = StorageApi()

console_logger = Logger(__file__)


class BaseCase(unittest.TestCase):
    @staticmethod
    def _update_env(test: int):
        with open(tests_env_file, 'r') as f:
            lines = f.readlines()

        new_line = f'UNIT_TEST="{test}"\n'
        for i, line in enumerate(lines):
            if line.startswith('UNIT_TEST='):
                lines[i] = new_line
                break
        else:
            # Если переменная не найдена, добавляем её в конец файла
            lines.append(new_line)

        with open(tests_env_file, 'w') as f:
            f.writelines(lines)

    @classmethod
    def setUpClass(cls):
        cls._update_env(1)

        # Создаем тестовое приложение для всего класса
        cls.app = KallosusNNApplication().create_app()
        cls.app.config['TESTING'] = True

        # Пушим контекст
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        db.create_all()
        console_logger.debug(f'DB tables created')

        # Создаем тестовый клиент
        cls.test_client = cls.app.test_client()
        console_logger.debug(f'Test client created')

        cls.test_video = os.path.join(os.path.dirname(current_path), 'DATA', 'videos', 'apple_rust.mp4')
        cls.test_s3_video = 'test-videos/cars_test.mp4'
        if not os.path.exists(cls.test_video):
            console_logger.warning(f'{cls.test_video} does not exists, used video from yandex disk url')
            cls.test_video = 'https://disk.yandex.ru/i/DmkPOSwcHLXqww'

        if Storage.get_storage() == 'local':
            cls.test_dst = os.path.join(local_test_s3_path, 'test')
        else:
            cls.test_dst = Storage.path_join(remote_test_s3_path, 'test')

        os.makedirs(cls.test_dst, exist_ok=True)

    def setUp(self):
        console_logger.info(f"[START]: {self.id().split('.')[-1]}")

        with self.app.app_context():
            if Task.query.first():
                db.session.query(Task).delete()
                db.session.commit()
                console_logger.debug('Tasks removed')

            if User.query.first():
                db.session.query(User).delete()
                db.session.commit()
                console_logger.debug('Users removed')

            self.test_user = User(email='test@gmail.com',
                                  password='TEST',
                                  company='Test corp'
                                  )

            self.test_user.save_to_db()
            self.test_user_id = self.test_user.id
            console_logger.info(f'Test User created {self.test_user_id}')

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
        cls._update_env(0)
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

    def clear_task_table(self):
        with self.app.app_context():
            if Task.query.first():
                db.session.query(Task).delete()
                db.session.commit()
                console_logger.debug('Deleted all tasks successfully')

    @staticmethod
    def value_in_list(value: Union[str, int, float], list_value: list):
        return value in list_value

    @staticmethod
    def _clear_s3_folder() -> bool:
        """
        :return: Очищено ли
        Очищаем тестовую папку для хранения данных обработки
        """
        is_rm = True

        if Storage.get_storage() == 'local':
            for filename in os.listdir(local_test_s3_path):
                file_path = os.path.join(local_test_s3_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

                    return False
        else:
            is_folder_rm = Storage.rm_folder(f'{remote_test_s3_path}/')

            console_logger.info(f'Is s3 removed: {is_folder_rm}')

        return is_rm
