import json
import os
import time
from datetime import timedelta
from typing import NoReturn

from flask_jwt_extended import create_access_token
from kallosus_packages.over_logging import Logger

from api import __version__
from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestCreateFolders(BaseCase):
    def test_successfully_create(self) -> NoReturn:
        """
        :return: `NoReturn`
        Тестирование верного запроса
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                "num_folders": 1
            }
        )

        # When
        response = self.test_client.post(f'/api/file_management/v{__version__}/create',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        self._clear_s3_folder()

        # Then
        self.assertEqual(list, type(response.json['folders']))
        self.assertEqual(200, response.status_code)

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
                "num_folders": 1
            }
        )

        # When
        response = self.test_client.post(f'/api/file_management/v{__version__}/create',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        # Then
        self.assertEqual('User does not exists', response.json['message'])
        self.assertEqual(404, response.status_code)

    def test_with_missing_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing`
        """

        payload = json.dumps(
            {
                "num_folders": 1
            }
        )

        # When
        response = self.test_client.post(f'/api/file_management/v{__version__}/create',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        self._clear_s3_folder()

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_with_missing_num_folders(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing`
        """

        payload = json.dumps(
            {
                "access_token": "Test"
            }
        )

        # When
        response = self.test_client.post(f'/api/file_management/v{__version__}/create',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        self._clear_s3_folder()

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_without_arguments(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing`
        """

        payload = json.dumps({})

        # When
        response = self.test_client.post(f'/api/file_management/v{__version__}/create',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        self._clear_s3_folder()

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_with_fake_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                "access_token": "Fake",
                "num_folders": 1
            }
        )

        # When
        response = self.test_client.post(f'/api/file_management/v{__version__}/create',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `ExpiredTokenError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id),
                                               expires_delta=timedelta(microseconds=1),
                                               )

        time.sleep(1)

        payload = json.dumps(
            {
                "access_token": access_token,
                "num_folders": 1
            }
        )

        # When
        response = self.test_client.post(f'/api/file_management/v{__version__}/create',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

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
                "num_folders": 1
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post(f'/api/file_management/v{__version__}/create',
                                             headers={"Content-Type": "application/json"},
                                             data=payload
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
        response = self.test_client.get(f'/api/file_management/v{__version__}/create',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
