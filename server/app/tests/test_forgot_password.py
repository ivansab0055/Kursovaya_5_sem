import json
import os
from typing import NoReturn

from flask_jwt_extended import create_access_token
from kallosus_packages.over_logging import Logger

from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestResetPassword(BaseCase):
    def test_successful_reset(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        # Given
        payload = json.dumps(
            {
                'email': self.test_user_email,
            }
        )

        # Forgot
        response = self.test_client.post('/api/auth/forgot', headers={'Content-Type': 'application/json'}, data=payload)

        url = response.json['url']
        token = url[url.index('reset/'):].replace('reset/', '')

        token_payload = json.dumps(
            {
                'reset_token': token,
                'password': 'new cool pwd',
            }
        )

        # When
        response = self.test_client.post('/api/auth/reset',
                                         headers={'Content-Type': 'application/json'},
                                         data=token_payload,
                                         )

        # Then
        self.assertEqual(str, type(response.json['access_token']))
        self.assertEqual(str, type(response.json['refresh_token']))
        self.assertEqual(200, response.status_code)

    def test_reset_for_none_exists_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            reset_token = create_access_token(identity='1000')

        # Forgot
        token_payload = json.dumps(
            {
                'reset_token': reset_token,
                'password': 'new cool pwd',
            }
        )

        # When
        response = self.test_client.post('/api/auth/reset',
                                         headers={'Content-Type': 'application/json'},
                                         data=token_payload,
                                         )

        # Then
        self.assertEqual('Invalid username, password or access_token', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_reset_without_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        token_payload = json.dumps(
            {
                'password': 'new cool pwd',
            }
        )

        # When
        response = self.test_client.post('/api/auth/reset',
                                         headers={'Content-Type': 'application/json'},
                                         data=token_payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_reset_without_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        token_payload = json.dumps(
            {
                'token': 'token',
            }
        )

        # When
        response = self.test_client.post('/api/auth/reset',
                                         headers={'Content-Type': 'application/json'},
                                         data=token_payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_reset_with_fake_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        token_payload = json.dumps(
            {
                'reset_token': 'Fake token',
                'password': 'New pwd',
            }
        )

        # When
        response = self.test_client.post('/api/auth/reset',
                                         headers={'Content-Type': 'application/json'},
                                         data=token_payload,
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_reset_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        reset_token = self._create_reset(microseconds=1)

        # Given
        token_payload = json.dumps(
            {
                'reset_token': reset_token,
                'password': 'New pwd',
            }
        )

        # When
        response = self.test_client.post('/api/auth/reset',
                                         headers={'Content-Type': 'application/json'},
                                         data=token_payload,
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

        reset_token = self._create_reset(microseconds=1)

        # Given
        token_payload = json.dumps(
            {
                'reset_token': reset_token,
                'password': 'New pwd',
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post('/api/auth/reset',
                                             headers={'Content-Type': 'application/json'},
                                             data=token_payload,
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
        response = self.test_client.get(f'/api/auth/reset',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
