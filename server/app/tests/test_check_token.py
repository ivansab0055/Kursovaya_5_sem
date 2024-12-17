import json
import os
import time
from datetime import timedelta
from typing import NoReturn

from flask_jwt_extended import create_access_token, create_refresh_token
from kallosus_packages.over_logging import Logger

from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestCheckToken(BaseCase):
    # ---------------- Access --------------------------
    def test_correct_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        # Given
        payload = json.dumps(
            {
                'access_token': access_token,
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('OK', response.json['message'])
        self.assertEqual(200, response.status_code)

    def test_incorrect_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                'access_token': 'fake-token',
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_expired_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id), expires_delta=timedelta(microseconds=1))

        time.sleep(1)

        # Given
        payload = json.dumps(
            {
                'access_token': access_token,
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_empty_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'access_token': '',
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    # ---------------- Refresh --------------------------
    def test_correct_refresh_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        with self.app.app_context():
            refresh_token = create_refresh_token(identity=str(self.test_user_id))

        # Given
        payload = json.dumps(
            {
                'refresh_token': refresh_token,
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('OK', response.json['message'])
        self.assertEqual(200, response.status_code)

    def test_incorrect_refresh_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                'refresh_token': 'fake-token',
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_empty_refresh_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'refresh_token': '',
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_expired_refresh_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        with self.app.app_context():
            refresh_token = create_refresh_token(identity=str(self.test_user_id),
                                                 expires_delta=timedelta(microseconds=1))

        time.sleep(0.8)

        # Given
        payload = json.dumps(
            {
                'refresh_token': refresh_token,
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    # ---------------- Confirm --------------------------
    def test_correct_confirm_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        confirm_token = self._create_confirm(minutes=1)

        # Given
        payload = json.dumps(
            {
                'confirm_token': confirm_token,
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('OK', response.json['message'])
        self.assertEqual(200, response.status_code)

    def test_incorrect_confirm_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                'confirm_token': 'fake-token',
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_empty_confirm_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'confirm_token': '',
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_expired_confirm_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        confirm_token = self._create_confirm(microseconds=1)

        # Given
        payload = json.dumps(
            {
                'confirm_token': confirm_token,
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    # ------------------ Reset -----------------------------
    def test_correct_reset_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        reset_token = self._create_reset(minutes=1)

        # Given
        payload = json.dumps(
            {
                'reset_token': reset_token,
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('OK', response.json['message'])
        self.assertEqual(200, response.status_code)

    def test_incorrect_reset_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                'reset_token': 'fake-token',
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_empty_reset_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'reset_token': '',
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_expired_reset_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        reset_token = self._create_reset(microseconds=1)

        # Given
        payload = json.dumps(
            {
                'reset_token': reset_token,
            }
        )

        # Check token
        response = self.test_client.post('/api/token/check_token',
                                         headers={'Content-Type': 'application/json'},
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
        reset_token = self._create_reset(microseconds=1)

        # Given
        payload = json.dumps(
            {
                'reset_token': reset_token,
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post('/api/token/check_token',
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
        response = self.test_client.get(f'/api/token/check_token',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
