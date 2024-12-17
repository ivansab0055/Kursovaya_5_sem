import json
import os
from typing import NoReturn

from kallosus_packages.over_logging import Logger

from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestRefreshToken(BaseCase):
    def test_successful_refresh(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'password': 'mycoolpassword',
                'company': 'Fisting every day',
            }
        )

        # Signup
        response = self.test_client.post('/api/auth/signup',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )
        url = response.json['url']
        confirm_token = url[url.index('confirm/'):].replace('confirm/', '')

        data = json.dumps(
            {
                'confirm_token': confirm_token,
            }
        )

        response = self.test_client.post('/api/auth/confirm', headers={'Content-Type': 'application/json'}, data=data)

        # Refresh
        refresh_token = response.json['refresh_token']

        response = self.test_client.post('/api/token/refresh',
                                         headers={'Authorization': f'Bearer {refresh_token}'},
                                         )

        # Then
        self.assertEqual(dict, type(response.json))
        self.assertEqual(200, response.status_code)

        assert response.json['access_token']

    def test_refresh_without_token_in_header(self) -> NoReturn:
        """
        :return: `NoReturn`
        :note: Мы отправляем аргументы в заголовках, а не `data`
        Проверяем срабатывание ошибки `jwt.exceptions.NoAuthorizationError`
        """

        # Given
        response = self.test_client.post('/api/token/refresh',
                                         headers={'Content-Type': 'application/json'},
                                         )

        # Then
        self.assertEqual('Missing Authorization Header', response.json['msg'])
        self.assertEqual(401, response.status_code)

    def test_refresh_with_fake_data(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `jwt.exceptions.NoAuthorizationError`
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'password': 'mycoolpassword',
                'company': 'Fisting every day',
            }
        )

        response = self.test_client.post('/api/token/refresh',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Missing Authorization Header', response.json['msg'])
        self.assertEqual(401, response.status_code)

    def test_refresh_with_invalid_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `jwt.exceptions.DecodeError`
        """

        # Given
        response = self.test_client.post('/api/token/refresh',
                                         headers={'Authorization': f'Bearer Token'},
                                         )

        # Then
        self.assertEqual('Not enough segments', response.json['msg'])
        self.assertEqual(422, response.status_code)

    def test_refresh_with_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `flask_jwt_extended.exceptions.WrongTokenError`
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'password': 'mycoolpassword',
                'company': 'Fisting every day',
            }
        )

        # Signup
        response = self.test_client.post('/api/auth/signup',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )
        url = response.json['url']
        confirm_token = url[url.index('confirm/'):].replace('confirm/', '')

        data = json.dumps(
            {
                'confirm_token': confirm_token,
            }
        )

        response = self.test_client.post('/api/auth/confirm', headers={'Content-Type': 'application/json'}, data=data)

        # Refresh
        access_token = response.json['access_token']

        response = self.test_client.post('/api/token/refresh',
                                         headers={'Authorization': f'Bearer {access_token}'},
                                         )

        # Then
        self.assertEqual('Only refresh tokens are allowed', response.json['msg'])
        self.assertEqual(422, response.status_code)

    def test_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `jwt.exceptions.ExpiredSignatureError`
        """

        # Given
        refresh_token = self._create_refresh(microseconds=1)

        # Refresh
        response = self.test_client.post('/api/token/refresh',
                                         headers={'Authorization': f'Bearer {refresh_token}'},
                                         )

        # Then
        self.assertEqual('Token has expired', response.json['msg'])
        self.assertEqual(401, response.status_code)

    def test_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        refresh_token = self._create_refresh()

        for i in range(2):
            # When
            response = self.test_client.post('/api/token/refresh',
                                             headers={'Authorization': f'Bearer {refresh_token}'},
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
        response = self.test_client.get(f'/api/token/refresh',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
