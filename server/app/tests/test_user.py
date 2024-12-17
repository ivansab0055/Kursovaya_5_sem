import json
import os
import time
from datetime import timedelta
from typing import NoReturn

from flask_jwt_extended import create_access_token
from kallosus_packages.over_logging import Logger

from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestUser(BaseCase):
    def test_successful_get_data(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        response = self.test_client.get('/api/auth/user',
                                        headers={'Authorization': f'Bearer {access_token}'},
                                        )

        # Then
        self.assertEqual(dict, type(response.json))
        self.assertEqual(200, response.status_code)
        print(response.json)

        assert response.json['id']
        assert response.json['email']
        assert response.json['company']
        assert response.json['password']
        self.assertFalse(response.json['mailing'])
        assert response.json['created_at']

    def test_get_for_non_exist_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(1000))

        response = self.test_client.get('/api/auth/user',
                                        headers={'Authorization': f'Bearer {access_token}'},
                                        )

        # Then
        self.assertEqual('Invalid username, password or access_token', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_get_data_without_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        data = ''
        response = self.test_client.get('/api/auth/user',
                                        headers={'Authorization': f'{data}'},
                                        )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_get_data_with_invalid_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        access_token = 'fake token'

        response = self.test_client.get('/api/auth/user',
                                        headers={'Authorization': f'Bearer {access_token}'},
                                        )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_get_data_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id), expires_delta=timedelta(microseconds=1))

        time.sleep(1)

        response = self.test_client.get('/api/auth/user',
                                        headers={'Authorization': f'Bearer {access_token}'},
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
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        for i in range(2):
            # When
            response = self.test_client.get('/api/auth/user',
                                            headers={'Authorization': f'Bearer {access_token}'},
                                            )

        self.assertEqual(429, response.status_code)
        self.assertEqual('1 per 3 minute', response.json['message'])

        os.environ['LIMITER_LIMIT'] = '1000 per minute'

    def test_method_not_allowed(self) -> NoReturn:
        """
        :return:
        Проверяем ошибку `WrapperTestResponse streamed [405 METHOD NOT ALLOWED]`
        """

        # Given
        payload = json.dumps(
            {
            }
        )

        # Get result
        response = self.test_client.post(f'/api/auth/user',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
