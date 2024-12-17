import json
import os
import time
from datetime import timedelta
from typing import NoReturn

from flask_jwt_extended import create_access_token
from kallosus_packages.over_logging import Logger

from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestSubscribeApi(BaseCase):
    def test_successfully_set_subscribe(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        # Given
        payload = json.dumps(
            {
                'access_token': access_token,
                'subscribe': True
            }
        )

        # Check token
        response = self.test_client.post('/api/mailing/subscribe',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        self.assertEqual('Subscription changed', response.json['message'])
        self.assertEqual(200, response.status_code)

    def test_not_exists_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'subscribe': True
            }
        )

        # Check token
        response = self.test_client.post('/api/mailing/subscribe',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_not_exists_subscribe(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                'access_token': access_token
            }
        )

        # Check token
        response = self.test_client.post('/api/mailing/subscribe',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_without_args(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
            }
        )

        # Check token
        response = self.test_client.post('/api/mailing/subscribe',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_with_not_exists_user(self) -> NoReturn:
        """
        :return:
        Проверяем ошибку `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(100))

        # Given
        payload = json.dumps(
            {
                'access_token': access_token,
                'subscribe': True
            }
        )

        # Check token
        response = self.test_client.post('/api/mailing/subscribe',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        self.assertEqual('Invalid username, password or access_token', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_with_fake_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                'access_token': 'fake',
                'subscribe': True
            }
        )

        # Check token
        response = self.test_client.post('/api/mailing/subscribe',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id), expires_delta=timedelta(microseconds=1))

        time.sleep(0.8)

        # Given
        payload = json.dumps(
            {
                'access_token': access_token,
                'subscribe': True
            }
        )

        # Check token
        response = self.test_client.post('/api/mailing/subscribe',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id), expires_delta=timedelta(microseconds=1))

        payload = json.dumps(
            {
                'access_token': access_token,
                'subscribe': True
            }
        )

        for i in range(2):
            # Check token
            response = self.test_client.post('/api/mailing/subscribe',
                                             headers={'Content-Type': 'application/json'},
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
        response = self.test_client.get(f'/api/mailing/subscribe',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
