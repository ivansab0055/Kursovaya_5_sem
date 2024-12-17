import json
import os
import time
from datetime import timedelta
from typing import NoReturn

from flask_jwt_extended import create_access_token
from kallosus_packages.over_logging import Logger

from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestChangePassword(BaseCase):
    def test_successful_changed(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                'access_token': access_token,
                'old_password': self.test_user_password,
                'new_password': 'my_cool_new_password',
            }
        )

        response = self.test_client.post('/api/auth/change_password',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Password changed', response.json['message'])
        self.assertEqual(200, response.status_code)

    def test_change_with_extra_field(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешный запрос, но с лишними полями
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                'access_token': access_token,
                'old_password': self.test_user_password,
                'new_password': 'my_cool_new_password',
                'extra': 'Extra field',
            }
        )

        response = self.test_client.post('/api/auth/change_password',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Password changed', response.json['message'])
        self.assertEqual(200, response.status_code)

    def test_change_password_with_incorrect_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(100))

        payload = json.dumps(
            {
                'access_token': access_token,
                'old_password': self.test_user_password,
                'new_password': 'my_cool_new_password',
            }
        )

        response = self.test_client.post('/api/auth/change_password',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Invalid username, password or access_token', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_change_without_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'old_password': self.test_user_password,
                'new_password': 'my_cool_new_password',
            }
        )

        response = self.test_client.post('/api/auth/change_password',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_change_without_new_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'access_token': 'Token',
                'old_password': self.test_user_password,
            }
        )

        response = self.test_client.post('/api/auth/change_password',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_change_without_old_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'access_token': 'Token',
                'new_password': 'New pwd',
            }
        )

        response = self.test_client.post('/api/auth/change_password',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_confirm_with_incorrect_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                'access_token': 'Token',
                'old_password': self.test_user_password,
                'new_password': 'my_cool_new_password',
            }
        )

        # When
        response = self.test_client.post('/api/auth/change_password',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_confirm_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id), expires_delta=timedelta(microseconds=1))

        time.sleep(0.5)

        # Given
        payload = json.dumps(
            {
                'access_token': access_token,
                'old_password': self.test_user_password,
                'new_password': 'my_cool_new_password',
            }
        )

        # When
        response = self.test_client.post('/api/auth/change_password',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_confirm_without_correct_old_pwd(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        # Given
        payload = json.dumps(
            {
                'access_token': access_token,
                'old_password': 'Fake pwd',
                'new_password': 'my_cool_new_password',
            }
        )

        # When
        response = self.test_client.post('/api/auth/change_password',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Invalid username, password or access_token', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                'access_token': access_token,
                'old_password': self.test_user_password,
                'new_password': 'my_cool_new_password',
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post('/api/auth/change_password',
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
        response = self.test_client.get(f'/api/auth/change_password',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
