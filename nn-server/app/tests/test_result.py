import json
import os
import time
from datetime import timedelta
from typing import NoReturn

from flask_jwt_extended import create_access_token
from kallosus_packages.over_logging import Logger

from api import __version__
from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestResult(BaseCase):
    def test_successfully_get_result(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешный запрос
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video],
                                "dst": [f'{self.test_dst}/{self.test_user_id}/'],
                                },
            }
        )

        # When

        # Setup job
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        task_id = response.json['task_id']

        status_payload = json.dumps(
            {
                "access_token": access_token,
                "task_id": task_id,
            }
        )

        result_payload = json.dumps(
            {
                "access_token": access_token,
                "task_id": task_id,
            }
        )

        while True:
            time.sleep(1.5)

            status_resp = self.test_client.post(f'/api/pd/v{__version__}/status',
                                                headers={"Content-Type": "application/json"},
                                                data=status_payload,
                                                )
            progress = status_resp.json['progress']
            console_logger.debug(f'progress = {progress}%')
            if progress >= 100 and status_resp.json["status"] in ['complete', 'error']:
                console_logger.debug('Job done')
                break

        # Get result
        result_response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                                headers={"Content-Type": "application/json"},
                                                data=result_payload,
                                                )
        is_rm = self._clear_s3_folder()

        upload_status = result_response.json['upload_status']

        # Then
        self.assertEqual(list, type(result_response.json['files']))
        self.assertEqual(dict, type(upload_status))
        self.assertEqual(True, is_rm)
        self.assertEqual(200, result_response.status_code)

    def test_successfully_get_result_with_many_files(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешный запрос
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video],
                                "dst": [f'{self.test_dst}/{self.test_user_id}/'],
                                },
            }
        )

        # When

        # Setup job
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        task_id = response.json['task_id']

        status_payload = json.dumps(
            {
                "access_token": access_token,
                'task_id': task_id,
            }
        )

        results_payload = json.dumps(
            {
                "access_token": access_token,
            }
        )

        while True:
            time.sleep(1.5)

            status = self.test_client.post(f'/api/pd/v{__version__}/status',
                                           headers={"Content-Type": "application/json"},
                                           data=status_payload,
                                           )

            progress = status.json['progress']
            console_logger.debug(f'progress = {progress}%')

            if progress == 100:
                console_logger.debug('Job done')
                break

        # Get result
        result_response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                                headers={"Content-Type": "application/json"},
                                                data=results_payload,
                                                )
        is_rm = self._clear_s3_folder()

        # Then
        self.assertEqual(list, type(result_response.json['files']))
        self.assertEqual(1, len([x for x in result_response.json['files'] if x]))

        self.assertEqual(list, type(result_response.json['upload_status']))
        self.assertEqual(1, len([x for x in result_response.json['upload_status'] if
                                 x]))  # 1, т.к. видео одинаковые названия имеют
        self.assertEqual(dict, type(result_response.json['upload_status'][-1]))
        self.assertEqual(True, is_rm)
        self.assertEqual(200, result_response.status_code)

    def test_successfully_get_results(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешный запрос

        result_response: {'files': [[], [], 'data-test/test/1796/17_31_09_1734273069336.json'],
         'upload_status': [None, None, {'test-videos/cars_test.mp4': [{'video': True}, {'res-file': True}]}]}
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video],
                                "dst": [f'{self.test_dst}/{self.test_user_id}/'],
                                },
            }
        )

        # When

        # Setup job
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        task_id = response.json['task_id']

        status_payload = json.dumps(
            {
                "access_token": access_token,
                'task_id': task_id,
            }
        )

        results_payload = json.dumps(
            {
                "access_token": access_token,
            }
        )

        while True:
            time.sleep(1.5)

            status_response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                                    headers={"Content-Type": "application/json"},
                                                    data=status_payload,
                                                    )

            progress = status_response.json['progress']
            status = status_response.json['status']
            console_logger.debug(f'progress = {progress}%')

            if progress == 100 and status in ['complete']:
                console_logger.debug('Job done')
                break

        # Get result
        result_response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                                headers={"Content-Type": "application/json"},
                                                data=results_payload,
                                                )

        upload_status = result_response.json['upload_status']
        is_rm = self._clear_s3_folder()

        key_exists = any(isinstance(item, dict) and self.test_s3_video in item for item in upload_status)

        # Then
        self.assertEqual(list, type(result_response.json['files']))
        self.assertEqual(list, type(upload_status))
        self.assertTrue(key_exists, f"Key '{self.test_s3_video}' not found in upload_files_status")
        self.assertEqual(True, is_rm)
        self.assertEqual(200, result_response.status_code)

    def test_successfully_get_results_with_many_files(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешный запрос
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video, self.test_s3_video],
                                "dst": [f'{self.test_dst}/{self.test_user_id}/',
                                        f'{self.test_dst}/{self.test_user_id}/'],
                                },
            }
        )

        # When

        # Setup job
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        task_id = response.json['task_id']

        status_payload = json.dumps(
            {
                "access_token": access_token,
                'task_id': task_id,
            }
        )

        results_payload = json.dumps(
            {
                "access_token": access_token,
            }
        )

        while True:
            time.sleep(1.5)

            status = self.test_client.post(f'/api/pd/v{__version__}/status',
                                           headers={"Content-Type": "application/json"},
                                           data=status_payload,
                                           )

            progress = status.json['progress']
            console_logger.debug(f'progress = {progress}%')

            if progress == 100:
                console_logger.debug('Job done')
                break

        # Get result
        result_response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                                headers={"Content-Type": "application/json"},
                                                data=results_payload,
                                                )
        is_rm = self._clear_s3_folder()

        # Then
        self.assertEqual(list, type(result_response.json['files']))
        self.assertEqual(2, len([x for x in result_response.json['files'] if x]))

        self.assertEqual(list, type(result_response.json['upload_status']))
        self.assertEqual(1, len([x for x in result_response.json['upload_status'] if
                                 x]))  # 1, т.к. видео одинаковые названия имеют
        self.assertEqual(dict, type(result_response.json['upload_status'][-1]))
        self.assertEqual(True, is_rm)
        self.assertEqual(200, result_response.status_code)

    def test_with_not_exists_user_id(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем, можно ли начать обработку для пользователя, которого не существует - `UserDoesNotExists`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(10))

        payload = json.dumps(
            {
                "access_token": access_token,
            }
        )

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('User does not exists', response.json['message'])
        self.assertEqual(404, response.status_code)

    def test_get_result_without_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_get_results_with_empty_task(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку ``
        """

        self.clear_task_table()

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('No tasks were found by user id or task id', response.json['message'])
        self.assertEqual(404, response.status_code)

    def test_get_result_with_only_taskid(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {
                "task_id": 1,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_get_result_with_fake_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                'access_token': "Fake",
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_get_result_with_expired_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `ExpiredTokenError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id),
                                               expires_delta=timedelta(microseconds=1),
                                               )

        time.sleep(1)

        # Given
        payload = json.dumps(
            {
                'access_token': access_token,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_get_result_with_fake_task_id(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `NoTasksError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        # Given
        payload = json.dumps(
            {
                'access_token': access_token,
                'task_id': 100,
            }
        )

        # Get result
        response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                         headers={"Content-Type": "application/json"},
                                         data=payload,
                                         )

        # Then
        self.assertEqual('No tasks were found by user id or task id', response.json['message'])
        self.assertEqual(404, response.status_code)

    def test_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        payload = json.dumps(
            {
                'access_token': '',
                'task_id': 100,
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post(f'/api/pd/v{__version__}/result',
                                             headers={"Content-Type": "application/json"},
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
        response = self.test_client.get(f'/api/pd/v{__version__}/result',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
