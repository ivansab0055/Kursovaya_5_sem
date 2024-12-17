import json
import os
import time
from datetime import timedelta
from typing import NoReturn

from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token
from kallosus_packages.over_logging import Logger

from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestAdminUserApi(BaseCase):
    def _get_user_data(self) -> dict:
        """
        :return: Данные пользователя
        Получаем все поля пользователя test user
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        response = self.test_client.get('/api/auth/user',
                                        headers={'Authorization': f'Bearer {access_token}'},
                                        )
        json_response = response.json
        if response.status_code == 401:
            return {}

        data = {
            'id': json_response['id'],
            'email': json_response['email'],
            'company': json_response['company'],
            'password': json_response['password'],
            'mailing': json_response['mailing'],
            'role': json_response['role'],
            'last_login_at': json_response['last_login_at'],
            'created_at': json_response['created_at'],
        }

        return data

    # -------------------------------------------- POST ---------------------------------------------------------------
    def test_successful_edit_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по редактированию данных пользователя
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_email = 'new_email_test@test.com'
        new_pwd = 'newpwd123'
        new_role = 'moderator'
        new_company = 'Unit test company'
        new_mailing = True

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "email": new_email,
                "password": new_pwd,
                "role": new_role,
                "company": new_company,
                "mailing": new_mailing,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )
        new_user_data = self._get_user_data()

        # Then
        self.assertEqual("The user's data has been updated", response.json['message'])

        self.assertEqual(new_email, new_user_data['email'])
        self.assertEqual(True, check_password_hash(new_user_data['password'], new_pwd))
        self.assertEqual(new_role, new_user_data['role'])
        self.assertEqual(new_company, new_user_data['company'])
        self.assertEqual(new_mailing, new_user_data['mailing'])

        self.assertEqual(200, response.status_code)

    def test_successful_edit_email(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по редактированию email
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_email = 'new_email_test@test.com'

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "email": new_email,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )
        new_user_data = self._get_user_data()

        # Then
        self.assertEqual("The user's data has been updated", response.json['message'])
        self.assertEqual(new_email, new_user_data['email'])
        self.assertEqual(True, check_password_hash(new_user_data['password'], self.test_user_password))
        self.assertEqual('user', new_user_data['role'])
        self.assertEqual(200, response.status_code)

    def test_successful_edit_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по редактированию пароля
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_pwd = 'newpwd123'

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "password": new_pwd,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )
        new_user_data = self._get_user_data()

        # Then
        self.assertEqual("The user's data has been updated", response.json['message'])
        self.assertEqual(self.test_user_email, new_user_data['email'])
        self.assertEqual(True, check_password_hash(new_user_data['password'], new_pwd))
        self.assertEqual('user', new_user_data['role'])
        self.assertEqual(200, response.status_code)

    def test_successful_edit_role(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по редактированию данных пользователя
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_role = 'moderator'

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "role": new_role,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )
        new_user_data = self._get_user_data()

        # Then
        self.assertEqual("The user's data has been updated", response.json['message'])
        self.assertEqual(self.test_user_email, new_user_data['email'])
        self.assertEqual(True, check_password_hash(new_user_data['password'], self.test_user_password))
        self.assertEqual('moderator', new_user_data['role'])
        self.assertEqual(200, response.status_code)

    def test_successful_edit_company(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по редактированию данных пользователя
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_company = 'Unit test company'

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "company": new_company,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )
        new_user_data = self._get_user_data()

        # Then
        self.assertEqual("The user's data has been updated", response.json['message'])

        self.assertEqual(self.test_user_email, new_user_data['email'])
        self.assertEqual(True, check_password_hash(new_user_data['password'], self.test_user_password))
        self.assertEqual(self.test_user_data['role'], new_user_data['role'])
        self.assertEqual(new_company, new_user_data['company'])
        self.assertEqual(self.test_user_data['mailing'], new_user_data['mailing'])

        self.assertEqual(200, response.status_code)

    def test_successful_edit_mailing(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по редактированию данных пользователя
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_mailing = True

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "mailing": new_mailing,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )
        new_user_data = self._get_user_data()

        # Then
        self.assertEqual("The user's data has been updated", response.json['message'])

        self.assertEqual(self.test_user_email, new_user_data['email'])
        self.assertEqual(True, check_password_hash(new_user_data['password'], self.test_user_password))
        self.assertEqual(self.test_user_data['role'], new_user_data['role'])
        self.assertEqual(self.test_user_data['company'], new_user_data['company'])
        self.assertEqual(new_mailing, new_user_data['mailing'])

        self.assertEqual(200, response.status_code)

    def test_successful_edit_email_and_password(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по редактированию пароля
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_email = 'new_email_test@test.com'
        new_pwd = 'newpwd123'

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "email": new_email,
                "password": new_pwd,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )
        new_user_data = self._get_user_data()

        # Then
        self.assertEqual("The user's data has been updated", response.json['message'])
        self.assertEqual(new_email, new_user_data['email'])
        self.assertEqual(True, check_password_hash(new_user_data['password'], new_pwd))
        self.assertEqual('user', new_user_data['role'])
        self.assertEqual(200, response.status_code)

    def test_successful_edit_email_and_role(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по редактированию пароля
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_email = 'new_email_test@test.com'
        new_role = 'admin'

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "email": new_email,
                "role": new_role,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )
        new_user_data = self._get_user_data()

        # Then
        self.assertEqual("The user's data has been updated", response.json['message'])
        self.assertEqual(new_email, new_user_data['email'])
        self.assertEqual(new_role, new_user_data['role'])
        self.assertEqual(200, response.status_code)

    def test_edit_without_data_arguments(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        payload = json.dumps(
            {
                "access_token": admin_access_token,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Some arguments in request are missing", response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_edit_without_all_arguments(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        payload = json.dumps(
            {
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Some arguments in request are missing", response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_edit_with_invalid_email(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `EmailError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_email = 'new_email_test-test.com'

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "email": new_email,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Email is invalid", response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_edit_with_invalid_role(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SchemaValidationError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_role = 'shit role'

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "role": new_role,
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Request is missing required database fields or didn't pass checks", response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_edit_with_invalid_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(1000))

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                'email': '<EMAIL>',
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Invalid username, password or access_token", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_edit_with_incorrect_user_rights(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ServerPermissionError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                'email': '<EMAIL>',
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_admin_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("You do not have the rights to perform this action", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_edit_admin_user_rights(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ServerPermissionError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                'email': '<EMAIL>',
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("You do not have the rights to perform this action", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_edit_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id),
                                                     expires_delta=timedelta(microseconds=1),
                                                     )

        time.sleep(0.5)

        # Given
        payload = json.dumps(
            {
                "access_token": admin_access_token,
                'email': '<EMAIL>',
            }
        )

        # When
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_edit_with_bad_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                "access_token": 'fake token',
                'email': '<EMAIL>',
            }
        )

        # When
        response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_edit_non_existent_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                'email': '<EMAIL>',
            }
        )

        # Change user data
        response = self.test_client.post(f'/api/admin/user/1000',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual("Invalid username, password or access_token", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_edit_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        new_email = 'new_email_test@test.com'

        payload = json.dumps(
            {
                "access_token": admin_access_token,
                "email": new_email,
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post(f'/api/admin/user/{self.test_user_id}',
                                             headers={'Content-Type': 'application/json'},
                                             data=payload,
                                             )

        self.assertEqual(429, response.status_code)
        self.assertEqual('1 per 3 minute', response.json['message'])

        os.environ['LIMITER_LIMIT'] = '1000 per minute'

    def test_edit_method_not_allowed(self) -> NoReturn:
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
        response = self.test_client.get(f'/api/admin/user/{self.test_user_id}',
                                        headers={'Content-Type': 'application/json'},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)

    # -------------------------------------------- DELETE -------------------------------------------------------------
    def test_successful_delete_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по удалению пользователя
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        # When
        response = self.test_client.delete(f'/api/admin/user/{self.test_user_id}',
                                           headers={'Authorization': f'Bearer {admin_access_token}'},
                                           )
        new_user_data = self._get_user_data()

        # Then
        self.assertEqual("The user has been deleted", response.json['message'])
        self.assertEqual({}, new_user_data)  # Пользователя нет
        self.assertEqual(200, response.status_code)

    def test_delete_without_data_arguments(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        payload = json.dumps(
            {
                "": '',
            }
        )

        # When
        response = self.test_client.delete(f'/api/admin/user/{self.test_user_id}',
                                           headers={'Content-Type': 'application/json'},
                                           data=payload,
                                           )

        # Then
        self.assertEqual("Some arguments in request are missing", response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_delete_with_invalid_admin_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(1000))

        # When
        response = self.test_client.delete(f'/api/admin/user/{self.test_user_id}',
                                           headers={'Authorization': f'Bearer {admin_access_token}'},
                                           )

        # Then
        self.assertEqual("Invalid username, password or access_token", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_delete_with_incorrect_user_rights(self):
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ServerPermissionError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        # When
        response = self.test_client.delete(f'/api/admin/user/{self.test_user_id}',
                                           headers={'Authorization': f'Bearer {access_token}'},
                                           )

        # Then
        self.assertEqual("You do not have the rights to perform this action", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_delete_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id),
                                                     expires_delta=timedelta(microseconds=1),
                                                     )

        time.sleep(0.5)

        # When
        response = self.test_client.delete(f'/api/admin/user/{self.test_user_id}',
                                           headers={'Authorization': f'Bearer {admin_access_token}'},
                                           )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_delete_with_bad_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        admin_access_token = 'fake-token'

        # When
        response = self.test_client.delete(f'/api/admin/user/{self.test_user_id}',
                                           headers={'Authorization': f'Bearer {admin_access_token}'},
                                           )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_delete_non_existent_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))
        # When
        response = self.test_client.delete(f'/api/admin/user/1000',
                                           headers={'Authorization': f'Bearer {admin_access_token}'},
                                           )

        # Then
        self.assertEqual("Invalid username, password or access_token", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_delete_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        for i in range(2):
            # When
            response = self.test_client.delete(f'/api/admin/user/{self.test_user_id}',
                                               headers={'Authorization': f'Bearer {admin_access_token}'},
                                               )

        self.assertEqual(429, response.status_code)
        self.assertEqual('1 per 3 minute', response.json['message'])

        os.environ['LIMITER_LIMIT'] = '1000 per minute'

    def test_delete_method_not_allowed(self) -> NoReturn:
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
        response = self.test_client.get(f'/api/admin/user/{self.test_user_id}',
                                        headers={'Content-Type': 'application/json'},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)


class TestAdminLoginAsUserApi(BaseCase):
    def test_successful_login_as_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по входу через пользователя
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        # When
        response = self.test_client.get(f'/api/admin/login_as/{self.test_user_id}',
                                        headers={'Authorization': f'Bearer {admin_access_token}'},
                                        )

        # Then
        self.assertEqual(str, type(response.json['access_token']))
        self.assertEqual(200, response.status_code)

    def test_login_without_data_arguments(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        admin_access_token = ''

        # When
        response = self.test_client.get(f'/api/admin/login_as/{self.test_user_id}',
                                        headers={'Authorization': f'Bearer {admin_access_token}'},
                                        )

        # Then
        self.assertEqual("Some arguments in request are missing", response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_login_with_invalid_admin_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(1000))

        # When
        response = self.test_client.get(f'/api/admin/login_as/{self.test_user_id}',
                                        headers={'Authorization': f'Bearer {admin_access_token}'},
                                        )

        # Then
        self.assertEqual("Invalid username, password or access_token", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_login_with_incorrect_user_rights(self):
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ServerPermissionError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        # When
        response = self.test_client.get(f'/api/admin/login_as/{self.test_user_id}',
                                        headers={'Authorization': f'Bearer {access_token}'},
                                        )

        # Then
        self.assertEqual("You do not have the rights to perform this action", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_login_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id),
                                                     expires_delta=timedelta(microseconds=1),
                                                     )

        time.sleep(0.5)
        # When
        response = self.test_client.get(f'/api/admin/login_as/{self.test_user_id}',
                                        headers={'Authorization': f'Bearer {admin_access_token}'},
                                        )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_login_with_bad_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        access_token = 'fake-token'

        # When
        response = self.test_client.get(f'/api/admin/login_as/{self.test_user_id}',
                                        headers={'Authorization': f'Bearer {access_token}'},
                                        )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_login_non_existent_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        # When
        response = self.test_client.get(f'/api/admin/login_as/1000',
                                        headers={'Authorization': f'Bearer {admin_access_token}'},
                                        )

        # Then
        self.assertEqual("Invalid username, password or access_token", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_login_with_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        for i in range(2):
            # When
            response = self.test_client.get(f'/api/admin/login_as/{self.test_user_id}',
                                            headers={'Authorization': f'Bearer {admin_access_token}'},
                                            )

        self.assertEqual(429, response.status_code)
        self.assertEqual('1 per 3 minute', response.json['message'])

        os.environ['LIMITER_LIMIT'] = '1000 per minute'

    def test_login_method_not_allowed(self) -> NoReturn:
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
        response = self.test_client.post(f'/api/admin/login_as/{self.test_user_id}',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)


class TestAdminGetAllUsersApi(BaseCase):
    def test_successful_get_users(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса по получению всех пользователей
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        # When
        response = self.test_client.get(f'/api/admin/users',
                                        headers={'Authorization': f'Bearer {admin_access_token}'},
                                        )

        # Then
        self.assertEqual(dict, type(response.json[str(self.test_admin_id)]))
        self.assertEqual(dict, type(response.json[str(self.test_user_id)]))
        self.assertEqual(200, response.status_code)

    def test_login_without_data_arguments(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        admin_access_token = ''

        # When
        response = self.test_client.get(f'/api/admin/users',
                                        headers={'Authorization': f'Bearer {admin_access_token}'},
                                        )

        # Then
        self.assertEqual("Some arguments in request are missing", response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_login_with_invalid_admin_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(1000))

        # When
        response = self.test_client.get(f'/api/admin/users',
                                        headers={'Authorization': f'Bearer {admin_access_token}'},
                                        )

        # Then
        self.assertEqual("Invalid username, password or access_token", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_login_with_incorrect_user_rights(self):
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ServerPermissionError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        # When
        response = self.test_client.get(f'/api/admin/users',
                                        headers={'Authorization': f'Bearer {access_token}'},
                                        )

        # Then
        self.assertEqual("You do not have the rights to perform this action", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_login_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `ExpiredTokenError`
        """

        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id),
                                                     expires_delta=timedelta(microseconds=1),
                                                     )

        time.sleep(0.5)

        # When
        response = self.test_client.get(f'/api/admin/users',
                                        headers={'Authorization': f'Bearer {admin_access_token}'},
                                        )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_login_with_bad_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `BadTokenError`
        """

        # Given
        access_token = 'Fake token'

        # When
        response = self.test_client.get(f'/api/admin/users',
                                        headers={'Authorization': f'Bearer {access_token}'},
                                        )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_login_non_existent_admin_user(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `UnauthorizedError`
        """

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id * 2))
        # When
        response = self.test_client.get(f'/api/admin/users',
                                        headers={'Authorization': f'Bearer {admin_access_token}'},
                                        )

        # Then
        self.assertEqual("Invalid username, password or access_token", response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_login_with_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        with self.app.app_context():
            admin_access_token = create_access_token(identity=str(self.test_admin_id))

        for i in range(2):
            # When
            response = self.test_client.get(f'/api/admin/users',
                                            headers={'Authorization': f'Bearer {admin_access_token}'},
                                            )

        self.assertEqual(429, response.status_code)
        self.assertEqual('1 per 3 minute', response.json['message'])

        os.environ['LIMITER_LIMIT'] = '1000 per minute'

    def test_login_method_not_allowed(self) -> NoReturn:
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
        response = self.test_client.post(f'/api/admin/users',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
