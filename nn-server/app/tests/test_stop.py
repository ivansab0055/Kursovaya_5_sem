import json
import os
import platform
import time
from datetime import timedelta
from typing import NoReturn
from unittest.mock import patch

from flask_jwt_extended import create_access_token
from kallosus_packages.over_logging import Logger
from rq.connections import NoRedisConnectionException

from api import __version__
from tests.BaseCase import BaseCase

"""
sudo service redis-server start
cd web_server
rq worker pd-task
"""

console_logger = Logger(__file__)

if platform.system() == 'Windows':
    console_logger.critical(f'You cant stop redis rq job on Windows system')


class TestStop(BaseCase):
    def test_successfully_stop(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем верный запрос
        """

        if platform.system() == 'Windows':
            self.assertTrue(True, 'You cant stop redis rq job on Windows system')
            return

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        predict_payload = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video],
                                "dst": [f'{self.test_dst}/{self.test_user_id}/',
                                        ],
                                },
                "sleep": 1,
            }
        )

        # When

        # Setup job
        response = self.test_client.post(f"/api/pd/v{__version__}/predict",
                                         headers={"Content-Type": "application/json"},
                                         data=predict_payload,
                                         )

        task_id = response.json["task_id"]

        payload = json.dumps(
            {
                "access_token": access_token,
                "task_id": task_id,
            }
        )

        # Stop job
        while True:
            pred_resp = self.test_client.post(f"/api/pd/v{__version__}/stop",
                                              headers={"Content-Type": "application/json"},
                                              data=payload,
                                              )

            console_logger.debug(f'pred_resp.json: {pred_resp.json}')
            if pred_resp.json['message'] == 'Job stop':
                break

            time.sleep(1)

        # Get status
        status_response = self.test_client.post(f"/api/pd/v{__version__}/status",
                                                headers={"Content-Type": "application/json"},
                                                data=payload,
                                                )
        self._clear_s3_folder()

        # Then
        self.assertEqual('Job stop', pred_resp.json['message'])
        self.assertEqual(int, type(status_response.json["progress"]))
        self.assertEqual('stopped', status_response.json["status"])
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
        response = self.test_client.post(f"/api/pd/v{__version__}/stop",
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('User does not exists', response.json['message'])
        self.assertEqual(404, response.status_code)

    def test_stop_without_args(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
            }
        )

        # Get result
        response = self.test_client.post(f"/api/pd/v{__version__}/stop",
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Some arguments in request are missing", response.json["message"])
        self.assertEqual(400, response.status_code)

    def test_get_status_with_fake_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                "access_token": "Fake",
                "task_id": 1,
            }
        )

        # Get result
        response = self.test_client.post(f"/api/pd/v{__version__}/result",
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Invalid token", response.json["message"])
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
                "access_token": access_token,
                "task_id": 1,
            }
        )

        # Get result
        response = self.test_client.post(f"/api/pd/v{__version__}/result",
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Token expired", response.json["message"])
        self.assertEqual(401, response.status_code)

    def test_stop_with_fake_task_id(self) -> NoReturn:
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
        response = self.test_client.post(f"/api/pd/v{__version__}/stop",
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("No tasks were found by user id or task id", response.json["message"])
        self.assertEqual(404, response.status_code)

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
                "task_id": self.clear_task_id,
            }
        )

        # Get result
        response = self.test_client.post(f"/api/pd/v{__version__}/stop",
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Incorrect job ID", response.json["message"])
        self.assertEqual(403, response.status_code)

    def test_with_fake_job(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку IncorrectJobIDError` (`NoSuchJob`), которая теперь `JobDoesNotExist`, `current_app.task_queue.fetch_job(job_id)` выдаст, что задачи нет в очереди
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                "task_id": self.test_task_id,
            }
        )

        # Get result
        response = self.test_client.post(f"/api/pd/v{__version__}/stop",
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Job does not exist", response.json["message"])
        self.assertEqual(404, response.status_code)

    def test_without_worker(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `IncorrectJobIDError` (`NoRedisConnectionException`), которая на самом деле теперь
        `JobDoesNotExist` благодаря `current_app.task_queue.fetch_job(job_id)`

        `patch` используется для временного замещения функции `send_stop_job_command` исключением `NoRedisConnectionException`.
        Это позволяет контролировать поведение функции при её вызове во время тестирования.
        """

        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        with patch("rq.command.send_stop_job_command", side_effect=NoRedisConnectionException):
            # Given
            payload = json.dumps(
                {
                    "access_token": access_token,
                    "task_id": self.test_task_id,
                }
            )

            # Get result
            response = self.test_client.post(f"/api/pd/v{__version__}/stop",
                                             headers={"Content-Type": "application/json"},
                                             data=payload,
                                             )

            # Then
            self.assertEqual("Job does not exist", response.json["message"])
            self.assertEqual(404, response.status_code)

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
                "task_id": self.test_task_id,
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post(f"/api/pd/v{__version__}/stop",
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
        response = self.test_client.get(f"/api/pd/v{__version__}/stop",
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual("The method is not allowed for the requested URL.", response.json["message"])
        self.assertEqual(405, response.status_code)
