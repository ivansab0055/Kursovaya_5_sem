import json
import os
from typing import NoReturn

from kallosus_packages.over_logging import Logger

from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestLogin(BaseCase):
    def test_successful_login(self) -> NoReturn:
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

        self.test_client.post('/api/auth/confirm',
                              headers={'Content-Type': 'application/json'},
                              data=data,
                              )

        # When
        response = self.test_client.post('/api/auth/login',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual(str, type(response.json['access_token']))
        self.assertEqual(200, response.status_code)

    def test_login_without_arguments(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {

            }
        )

        # When
        response = self.test_client.post('/api/auth/login',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_login_without_email(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """
        # Given
        payload = json.dumps(
            {
                'password': 'adsf'
            }
        )

        # When
        response = self.test_client.post('/api/auth/login',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_login_without_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com'
            }
        )

        # When
        response = self.test_client.post('/api/auth/login',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_login_with_invalid_email(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        payload = {
            'email': 'paurakh012@gmail.com',
            'password': self.test_user_password,
            'company': 'Test corp',
        }

        response = self.test_client.post('/api/auth/login',
                                         headers={'Content-Type': 'application/json'},
                                         data=json.dumps(payload),
                                         )

        # Then
        self.assertEqual('Invalid username, password or access_token', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_login_with_invalid_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        payload = {
            'email': self.test_user_email,
            'password': 'myverycoolpassword',
            'company': 'Test corp',
        }

        # When
        response = self.test_client.post('/api/auth/login',
                                         headers={'Content-Type': 'application/json'},
                                         data=json.dumps(payload)
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
        payload = {
            'email': 'test@gmail.com',
            'password': 'myverycoolpassword',
            'company': 'Test corp',
        }

        for i in range(2):
            # When
            response = self.test_client.post('/api/auth/login',
                                             headers={'Content-Type': 'application/json'},
                                             data=json.dumps(payload)
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
        response = self.test_client.get(f'/api/auth/login',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
