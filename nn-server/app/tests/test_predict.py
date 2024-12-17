import json
import os
import time
from datetime import timedelta
from typing import NoReturn
from unittest.mock import MagicMock

from flask_jwt_extended import create_access_token
from kallosus_packages.over_logging import Logger
from redis.exceptions import ConnectionError

from api import __version__
from tests.BaseCase import BaseCase, Storage

console_logger = Logger(__file__)


class TestPredict(BaseCase):
    def test_successfully_execution(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешный запрос
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        # Создаем папку, где будет хранится наше видео
        create_folders_payload = json.dumps(
            {
                "access_token": access_token,
                "num_folders": 1
            }
        )

        response = self.test_client.post(f'/api/file_management/v{__version__}/create',
                                         headers={"Content-Type": "application/json"},
                                         data=create_folders_payload
                                         )

        predict_payload = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video],
                                "dst": response.json['folders']
                                },
            }
        )

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=predict_payload
                                         )

        # Останавливаем обработку (не работает под windows)
        task_id = response.json['task_id']
        payload = json.dumps(
            {
                "access_token": access_token,
                'task_id': task_id,
            }
        )

        status_response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                                headers={"Content-Type": "application/json"},
                                                data=payload,
                                                )

        while status_response.json['progress'] != 100 or status_response.json["status"] not in ['complete',
                                                                                                'error']:
            time.sleep(1.5)
            # Get status
            status_response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                                    headers={"Content-Type": "application/json"},
                                                    data=payload,
                                                    )
            console_logger.debug(f'{status_response.json["progress"]}, {status_response.json["status"]}')

        is_rm = self._clear_s3_folder()

        # Then
        self.assertEqual('Prediction start', response.json['message'])
        self.assertEqual(int, type(task_id))
        self.assertEqual(200, response.status_code)
        self.assertEqual(True, Storage.path_exists(self.test_s3_video))
        self.assertEqual(True, is_rm)

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
                "queue_files": {"src": [self.test_s3_video],
                                "dst": ["Some folder"],
                                },
            }
        )

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        # Then
        self.assertEqual('User does not exists', response.json['message'])
        self.assertEqual(404, response.status_code)

    def test_with_diff_len_queue_files(self) -> NoReturn:
        """
        :return: `NoReturn`
        Если в запросе src и dst разной длины, то будет ошибка `ArgumentError`
        """
        # Given
        payload = json.dumps(
            {
                "access_token": "token",
                "queue_files": {"src": [self.test_s3_video, self.test_s3_video],
                                "dst": ["Some folder"],
                                },
            }
        )

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        # Then
        self.assertEqual('The argument is specified incorrectly', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_with_exceeded_bucket(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем вызов ошибки `BucketSizeExceeded`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video],
                                "dst": ["Some folder"],
                                },
            }
        )

        os.environ['BUCKET_LIMIT_GB'] = '0'

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        os.environ['BUCKET_LIMIT_GB'] = ''

        # Then
        self.assertEqual('The size of the bucket has been exceeded', response.json['message'])
        self.assertEqual(413, response.status_code)

    def test_with_not_exist_file(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `FileExistError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        payload = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": ['File/path'],
                                "dst": ["Some folder"],
                                },
            }
        )

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        # Then
        self.assertEqual('File does not exist', response.json['message'])
        self.assertEqual('File/path', response.json['file'])
        self.assertEqual(404, response.status_code)

    def test_with_missing_access_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing` для токена
        """

        # Given
        payload = json.dumps(
            {
                "queue_files": {"src": [self.test_s3_video],
                                "dst": ["Some folder"],
                                },
            }
        )

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_with_missing_queue_files(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing` для обрабатываемых файлов
        """

        # Given
        payload = json.dumps(
            {
                "access_token": "Test"
            }
        )

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_without_arguments(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps({})

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        # Then
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_with_fake_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `BadTokenError`
        """

        # Given
        payload = json.dumps(
            {
                "access_token": "Fake",
                "queue_files": {"src": [self.test_s3_video],
                                "dst": ["Some folder"],
                                },
            }
        )

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        # Then
        self.assertEqual('Invalid token', response.json['message'])
        self.assertEqual(403, response.status_code)

    def test_with_expired_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `ExpiredTokenError`
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id), expires_delta=timedelta(microseconds=1))

        time.sleep(1)

        payload = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video],
                                "dst": ["Some folder"],
                                },
            }
        )

        # When
        response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                         headers={"Content-Type": "application/json"},
                                         data=payload
                                         )

        # Then
        self.assertEqual('Token expired', response.json['message'])
        self.assertEqual(401, response.status_code)

    def test_with_queue_task(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем обработку, когда есть очередь - просто добавляется в нее. Также, проверяем статусы: queue, run, complete
        """

        # Given
        with self.app.app_context():
            access_token = create_access_token(identity=str(self.test_user_id))

        predict_payload_1 = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video],
                                "dst": [f'{self.test_dst}/{self.test_user_id}/'],
                                },
            }
        )

        # When
        # 1 в очереди
        response_1 = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                           headers={"Content-Type": "application/json"},
                                           data=predict_payload_1,
                                           )

        task_id_1 = response_1.json['task_id']
        status_payload_1 = json.dumps(
            {
                "access_token": access_token,
                'task_id': task_id_1,
            }
        )

        # 2 В очереди
        predict_payload_2 = json.dumps(
            {
                "access_token": access_token,
                "queue_files": {"src": [self.test_s3_video],
                                "dst": [f'{self.test_dst}/{self.test_user_id + 1}/'],
                                },
            }
        )
        response_2 = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                           headers={"Content-Type": "application/json"},
                                           data=predict_payload_2,
                                           )

        task_id_2 = response_2.json['task_id']
        status_payload_2 = json.dumps(
            {
                "access_token": access_token,
                'task_id': task_id_2,
            }
        )

        # Проверяем, что 2 задача в очереди
        check_queue_status = self.test_client.post(f'/api/pd/v{__version__}/status',
                                                   headers={"Content-Type": "application/json"},
                                                   data=status_payload_2,
                                                   )
        self.assertEqual('queue', check_queue_status.json['status'])

        while True:
            time.sleep(1.5)
            # Get status
            status_response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                                    headers={"Content-Type": "application/json"},
                                                    data=status_payload_1,
                                                    )
            console_logger.debug(f'{status_response.json["progress"]}, {status_response.json["status"]}')

            if status_response.json['progress'] >= 100 and status_response.json["status"] in ['complete',
                                                                                              'error']:
                break

        self.assertEqual('complete', status_response.json["status"])

        # Проверяем, что 2 задача запущена
        check_run_status = self.test_client.post(f'/api/pd/v{__version__}/status',
                                                 headers={"Content-Type": "application/json"},
                                                 data=status_payload_2,
                                                 )
        self.assertEqual('run', check_run_status.json['status'])

        while True:
            time.sleep(1.5)
            # Get status
            status_response = self.test_client.post(f'/api/pd/v{__version__}/status',
                                                    headers={"Content-Type": "application/json"},
                                                    data=status_payload_2,
                                                    )
            console_logger.debug(f'{status_response.json["progress"]}, {status_response.json["status"]}')

            if status_response.json['progress'] >= 100 and status_response.json["status"] in ['complete',
                                                                                              'error']:
                break

        self.assertEqual('complete', status_response.json["status"])

        is_rm = self._clear_s3_folder()

        # Then
        self.assertEqual('Prediction start', response_1.json['message'])
        self.assertEqual('Prediction start', response_2.json['message'])
        self.assertEqual(200, response_1.status_code)
        self.assertEqual(200, response_2.status_code)

        self.assertEqual(True, is_rm)

    def test_without_worker(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку `WorkerDoesNotRunError`, если очередь не существует
        """

        # Настройка Mock для поднятия ConnectionError
        mock_queue = MagicMock()
        mock_queue.enqueue.side_effect = ConnectionError

        # Подменяем текущую очередь на Mock объект
        original_queue = self.app.task_queue
        self.app.task_queue = mock_queue

        try:
            # Given
            with self.app.app_context():
                access_token = create_access_token(identity=str(self.test_user_id))

            payload = json.dumps(
                {
                    "access_token": access_token,
                    "queue_files": {"src": [self.test_s3_video],
                                    "dst": [f'{self.test_dst}/{self.test_user_id + 1}/']
                                    },
                }
            )

            # When
            response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                             headers={"Content-Type": "application/json"},
                                             data=payload
                                             )

            self.assertEqual('Worker does not run', response.json['message'])
            self.assertEqual(403, response.status_code)
        finally:
            # Восстанавливаем оригинальную очередь
            self.app.task_queue = original_queue

    def test_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        payload = json.dumps(
            {
                "access_token": '',
                "queue_files": {"src": [self.test_video],
                                "dst": [self.test_video]
                                },
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post(f'/api/pd/v{__version__}/predict',
                                             headers={"Content-Type": "application/json"},
                                             data=payload
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
        response = self.test_client.get(f'/api/pd/v{__version__}/predict',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
