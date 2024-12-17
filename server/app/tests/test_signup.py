import json
import os
import re
from typing import NoReturn

from kallosus_packages.over_logging import Logger

from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestSignUp(BaseCase):
    # def test_real_successful_signup(self) -> NoReturn:
    #     """
    #     :return: `NoReturn`
    #     :result: Успех
    #     Регистрация с подтверждением по почте.
    #     Запрос на регистрацию -> получение из письма токена -> регистрация -> получение письма об успешно регистрации.
    #     Проверяем успешное выполнение запроса
    #     """
    #
    #     os.environ['UNIT_TEST'] = '0'
    #
    #     # Given
    #     payload = json.dumps(
    #         {
    #             'email': self.app.config['MAIL_USERNAME'],
    #             'company': 'Test corp',
    #             'password': 'mycoolpassword',
    #         }
    #     )
    #
    #     self.test_client.post('/api/auth/signup',
    #                           headers={'Content-Type': 'application/json'},
    #                           data=payload,
    #                           )
    #
    #     subject, letter_from, message = self.read_mail('[Kallosus] Подтвердите свою почту',
    #                                                    delete_successfully_read_msg=True,
    #                                                    )
    #
    #     confirm_token = re.findall("/confirm/(.*)\\r", message[0])[0]
    #
    #     data = json.dumps(
    #         {
    #             'confirm_token': confirm_token,
    #         }
    #     )
    #
    #     # When
    #     self.test_client.post('/api/auth/confirm', headers={'Content-Type': 'application/json'}, data=data)
    #
    #     subject, letter_from, message = self.read_mail('[Kallosus] Почта успешно подтверждена',
    #                                                    delete_successfully_read_msg=True,
    #                                                    )
    #
    #     os.environ['UNIT_TEST'] = '1'
    #
    #     # Then
    #     self.assertEqual('[Kallosus] Почта успешно подтверждена', subject)

    def test_successful_signup(self) -> NoReturn:
        """
        :return: `NoReturn`
        :result: Успех
        Тестируем регистрацию без подтверждения по почте
        Проверяем успешное выполнение запроса
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'company': 'Test corp',
                'password': 'mycoolpassword',
                'confirmation': False,
            }
        )

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

        # When
        response = self.test_client.post('/api/auth/confirm',
                                         headers={'Content-Type': 'application/json'},
                                         data=data,
                                         )

        # Then
        self.assertEqual(str, type(response.json['access_token']))
        self.assertEqual(str, type(response.json['refresh_token']))
        self.assertEqual(200, response.status_code)

    def test_signup_with_extra_field(self) -> NoReturn:
        """
        :return: `NoReturn`
        :result: Успех
        Тестируем регистрацию с лишними полями
        Проверяем успешное выполнение запроса
        """

        # Given
        payload = json.dumps(
            {
                'GayWebSite': 'mycoolusername',
                'email': 'paurakh011@gmail.com',
                'company': 'Test corp',
                'password': 'mycoolpassword'
            }
        )

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

        # When
        response = self.test_client.post('/api/auth/confirm',
                                         headers={'Content-Type': 'application/json'},
                                         data=data,
                                         )

        # Then
        self.assertEqual(str, type(response.json['access_token']))
        self.assertEqual(str, type(response.json['refresh_token']))
        self.assertEqual(200, response.status_code)

    def test_signup_without_email(self) -> NoReturn:
        """
        :return: `NoReturn`
        :result: Плохой запрос
        Тестируем регистрацию без поля email
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'password': 'mycoolpassword',
                'company': 'Test corp',
            }
        )

        # When
        response = self.test_client.post('/api/auth/signup',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_signup_with_incorrect_email(self) -> NoReturn:
        """
        :return: `NoReturn`
        :result: Плохой запрос
        Тестируем регистрацию с некорректным email - это проверит validators.py - `EmailError`
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail',
                'password': 'mycoolpassword',
                'company': 'Test corp',
            }
        )

        # When
        response = self.test_client.post('/api/auth/signup',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Email is invalid', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_signup_without_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'company': 'Test corp',
            }
        )

        # When
        response = self.test_client.post('/api/auth/signup',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_signup_same_user_if_not_confirmed(self) -> NoReturn:
        """
        :return: `NoReturn`
        :result: Успех
        Тестируем регистрацию уже зарегистрированного пользователя, если почта еще не подтверждена
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'password': 'mycoolpassword',
                'company': 'Test corp',
            }
        )

        self.test_client.post('/api/auth/signup',
                              headers={'Content-Type': 'application/json'},
                              data=payload,
                              )

        # When
        response = self.test_client.post('/api/auth/signup',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual(str, type(response.json['url']))
        self.assertEqual(200, response.status_code)

    def test_signup_already_existing_user(self) -> NoReturn:
        """
        :return: NoReturn
        :result: Плохой запрос.
        Тестируем регистрацию уже зарегистрированного пользователя.
        Проверяем срабатывание ошибки `EmailAlreadyExistsError`
        """

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'password': 'mycoolpassword',
                'company': 'Test corp',
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

        self.test_client.post('/api/auth/confirm',
                              headers={'Content-Type': 'application/json'},
                              data=data,
                              )

        # When
        response = self.test_client.post('/api/auth/signup',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('User with given email address already exists', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        payload = json.dumps(
            {
                'email': 'paurakh011@gmail.com',
                'password': 'mycoolpassword',
                'company': 'Test corp',
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post('/api/auth/signup',
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
        response = self.test_client.get(f'/api/auth/signup',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
