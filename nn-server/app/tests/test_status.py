import json
import os
import time
from datetime import timedelta
from typing import NoReturn
from unittest.mock import MagicMock

from flask_jwt_extended import create_access_token
from kallosus_packages.over_logging import Logger
from redis.exceptions import ConnectionError

from api import __version__
from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestStatus(BaseCase):
    def test_successfully_get_status(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешный запрос
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video],
                                "dst": [f'{self.test_dst}/{self.test_user_id}/'],
                                },
            }
        )

        # When

        # Setup job
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )
        task_id = response.json['task_id']

        # Get status
        status_payload = json.dumps(
            {
                "access_token": access_token,
                'task_id': task_id,
            }
        )
        status_response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                                headers={"Content-Type": "application/json"},
                                                data=status_payload,
                                                )

        while status_response.json['progress'] != 100 or status_response.json["status"] not in ['complete',
                                                                                                'error']:
            time.sleep(1.5)
            # Get status
            status_response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                                    headers={"Content-Type": "application/json"},
                                                    data=status_payload,
                                                    )
            console_logger.debug(
                f'{status_response.json["progress"]}, {status_response.json["eta"]}sec, {status_response.json["status"]}')

        expected_progress = 100

        is_rm = self._clear_s3_folder()

        # Then
        self.assertEqual(0, status_response.json['eta'])
        self.assertEqual(1, status_response.json['video_no'])
        self.assertEqual(1, status_response.json['videos_no'])
        self.assertEqual('info-loading', status_response.json['stage'])
        self.assertEqual(expected_progress, status_response.json['progress'])

        self.assertEqual(True, is_rm)
        self.assertEqual(200, status_response.status_code)

    def test_with_not_exists_user_id(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем, можно ли начать обработку для пользователя, которого не существует - `UserDoesNotExists`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(10))

        payload = json.dumps(
            {
                "access_token": access_token,
                "task_id": 1,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('User does not exists', response.json['message'])
        self.assertEqual(404, response.status_code)

    def test_get_with_incorrect_task_id(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `NoTasksError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                "task_id": 10000,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('No tasks were found by user id or task id', response.json['message'])
        self.assertEqual(404, response.status_code)

    def test_get_without_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                "task_id": 1,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_get_status_with_fake_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                'access_token': "Fake",
                "task_id": 1,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_get_status_with_expired_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `ExpiredTokenError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id), expires_delta=timedelta(microseconds=1))

        time.sleep(1)

        # Given
        payload = json.dumps(
            {
                'access_token': access_token,
                "task_id": 1,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_get_without_task_id(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                "access_token": "",
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_without_job_id(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `IncorrectJobIDError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                'task_id': self.clear_task_id,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        self.assertEqual('Incorrect job ID', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_with_incorrect_job_id(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `JobDoesNotExist`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                'task_id': self.test_task_id,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        self.assertEqual('Job does not exist', response.json['message'])
        self.assertEqual(404, response.status_code)

    def test_without_worker(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `JobDoesNotExist`, если подменили очередь
        """

        def fetch_job(job_id):
            return None  # Или фейковый объект, который вы хотите вернуть

        # Создаем mock для очереди
        mock_queue = MagicMock()
        mock_queue.enqueue.side_effect = ConnectionError
        mock_queue.fetch_job = fetch_job

        original_queue = self.app.task_queue
        self.app.task_queue = mock_queue

        try:
            with self.app.app_context():
                access_token = create_access_token(identity=str(self.test_user_id))

            # Подготавливаем payload для запроса статуса
            payload = json.dumps(
                {
                    "access_token": access_token,
                    'task_id': self.test_task_id
                }
            )

            # Отправляем запрос на получение статуса задачи
            response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                             headers={"Content-Type": "application/json"},
                                             data=payload,
                                             )

            # Проверяем, что ответ содержит ожидаемое сообщение и статус код
            self.assertEqual(response.status_code, 404)
            self.assertEqual('Job does not exist', response.json['message'])
        finally:
            # Восстанавливаем оригинальную очередь
            self.app.task_queue = original_queue

    def test_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        payload = json.dumps(
            {
                "access_token": '',
                'task_id': self.test_task_id
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                             headers={"Content-Type": "application/json"},
                                             data=payload,
                                             )

        self.assertEqual(429, response.status_code)
        self.assertEqual('1 per 3 minute', response.json['message'])

        os.environ['LIMITER_LIMIT'] = '1000 per minute'

    def test_method_not_allowed(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `WrapperTestResponse streamed [405 METHOD NOT ALLOWED]`
        """

        # Given
        payload = json.dumps(
            {
            }
        )

        # Get result
        response = self.test_client.get(f'/api/pd/v{__version__}/status',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
