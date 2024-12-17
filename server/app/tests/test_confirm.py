import json
import os
from typing import NoReturn

from kallosus_packages.over_logging import Logger

from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestConfirm(BaseCase):
    def test_successful_confirm(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'company': 'Test corp',
                'password': 'mycoolpassword',
            }
        )

        response = self.test_client.post('/api/auth/signup', headers={'Content-Type': 'application/json'}, data=payload)
        url = response.json['url']
        confirm_token = url[url.index('confirm/'):].replace('confirm/', '')

        data = json.dumps(
            {
                'confirm_token': confirm_token,
            }
        )

        # When
        response = self.test_client.post('/api/auth/confirm', headers={'Content-Type': 'application/json'}, data=data)

        # Then
        self.assertEqual(str, type(response.json['access_token']))
        self.assertEqual(str, type(response.json['refresh_token']))
        self.assertEqual(200, response.status_code)

    def test_confirm_with_extra_field(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса с лишними полями
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'company': 'Test corp',
                'password': 'mycoolpassword',
            }
        )

        response = self.test_client.post('/api/auth/signup', headers={'Content-Type': 'application/json'}, data=payload)
        url = response.json['url']
        confirm_token = url[url.index('confirm/'):].replace('confirm/', '')

        data = json.dumps(
            {
                'confirm_token': confirm_token,
                'extra_field': 'missing',
            }
        )

        # When
        response = self.test_client.post('/api/auth/confirm', headers={'Content-Type': 'application/json'}, data=data)

        # Then
        self.assertEqual(str, type(response.json['access_token']))
        self.assertEqual(str, type(response.json['refresh_token']))
        self.assertEqual(200, response.status_code)

    def test_confirm_without_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'company': 'Test corp',
                'password': 'mycoolpassword',
            }
        )

        self.test_client.post('/api/auth/signup', headers={'Content-Type': 'application/json'}, data=payload)

        data = json.dumps(
            {
            }
        )

        # When
        response = self.test_client.post('/api/auth/confirm', headers={'Content-Type': 'application/json'}, data=data)

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_confirm_with_incorrect_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        data = json.dumps(
            {
                'confirm_token': 'haha token',
            }
        )

        # When
        response = self.test_client.post('/api/auth/confirm', headers={'Content-Type': 'application/json'}, data=data)

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_confirm_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        confirm_token = self._create_confirm(microseconds=1)

        data = json.dumps(
            {
                'confirm_token': confirm_token,
            }
        )

        # When
        response = self.test_client.post('/api/auth/confirm',
                                         headers={'Content-Type': 'application/json'},
                                         data=data,
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
        confirm_token = self._create_confirm(microseconds=1)
        data = json.dumps(
            {
                'confirm_token': confirm_token,
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post('/api/auth/confirm',
                                             headers={'Content-Type': 'application/json'},
                                             data=data,
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
        response = self.test_client.get(f'/api/auth/confirm',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
