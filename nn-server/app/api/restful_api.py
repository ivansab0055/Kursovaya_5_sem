import os
import re

from flask import current_app
from flask import request
from flask_jwt_extended import decode_token
from flask_restful import Resource
from jwt.exceptions import (ExpiredSignatureError,
                            DecodeError,
                            InvalidTokenError,
                            )
from kallosus_packages.over_logging import Logger, GetTraceback
from redis.exceptions import ConnectionError
from rq.exceptions import InvalidJobOperation

from database.db import create_tables, is_table_exists
from database.models import Task, User
from resources.errors import (format_error_to_return,
                              InternalServerError,
                              SomeRequestArgumentsMissing,
                              ExpiredTokenError,
                              BadTokenError,
                              IncorrectJobIDError,
                              WorkerDoesNotRunError,
                              JobDoesNotExist,
                              NoTasksError,
                              JobIsNotCurrentlyExecuted,
                              ArgumentError,
                              UserDoesNotExists,
                              FileExistError,
                              BucketSizeExceeded,
                              )
from storage.S3 import StorageApi
from utils.limiter import apply_limits

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)

Storage = StorageApi()


class PredictApi(Resource):
    """
    REST-API class для предсказания болезней растений
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: {'message': 'Prediction start', 'job_id': task.job_id}, 200 || ошибка, код ответа || {'status': task.status, 'job_id': task.job_id}, 400

        Добавляем задание на обработку видео в очередь

        URL: `/api/pd/v{__version__}/predict`

        Пример запроса:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjN9.2e6bS75p5SyJpacHBFic5KTMa8WA_UChrrAH8pucpyM",
            "queue_files": {"src": ["C:\\Users\\pikro\\Kallosus\\NN server\\DATA\\videos\\cars.mp4"], "folder": ["S3/user_id/dd_mm_yy/time"]},
            "sleep": 0,
            "save_output": true,
            "is_remove": false
        }

        или

        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjN9.2e6bS75p5SyJpacHBFic5KTMa8WA_UChrrAH8pucpyM",
            "queue_files": {"src": ["C:\\Users\\pikro\\Kallosus\\NN server\\DATA\\videos\\cars.mp4"], "dst": ["S3/user_id/dd_mm_yy/time"]}
        }
        """

        apply_limits('6/minute')

        try:
            body = request.get_json()

            access_token: str = body.get('access_token')
            queue_files: dict = body.get('queue_files')

            if not access_token or not queue_files:
                raise SomeRequestArgumentsMissing('Not all arguments are passed in the request')

            # Делаем уникальным, чтобы нельзя было обрабатывать дважды
            sources = queue_files['src']
            dst_folders = queue_files['dst']

            if len(sources) != len(dst_folders):
                raise ArgumentError('`sources` len must be the same as `dst_folders`')

            decoded = decode_token(access_token)
            user_id = decoded['sub']

            exists = User.find_by_id(user_id) is not None

            if not exists:
                raise UserDoesNotExists

            if not Storage.is_bucket_under_limit():
                raise BucketSizeExceeded

            for file in sources:
                if not Storage.path_exists(file):
                    raise FileExistError(f'File {file} does not exist')

            if not is_table_exists('task'):
                if os.environ.get('UNIT_TEST') in ['0', None]:
                    get_traceback.critical('No table: Task')
                else:
                    console_logger.debug('No table: Task')

                create_tables(current_app)

            # Создаем новую (у пользователя может быть много задач)
            task = Task(user_id=user_id,
                        job_id=None,
                        queue_files=sources,
                        user_current_time_folders=dst_folders,
                        )

            task.save_to_db()
            console_logger.debug('New task added')

            kwargs = {}
            for key in body:
                if key not in ['access_token', 'queue_files']:
                    kwargs[key] = body.get(key)

            task.launch_task(files=sources, current_time_folders=dst_folders, **kwargs)

            console_logger.debug(f'PredictApi: done_res_files: {task.done_res_files}, queue_files: {task.queue_files}')

            return {'message': 'Prediction start', 'task_id': task.id, 'job_id': task.job_id}, 200
        except ExpiredSignatureError as e:  # ошибка должна быть выше, чем: `DecodeError, InvalidTokenError`
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'DecodeError, InvalidTokenError: {e}')
            return format_error_to_return(BadTokenError)
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except ArgumentError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ArgumentError)
        except UserDoesNotExists as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UserDoesNotExists)
        except BucketSizeExceeded as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(BucketSizeExceeded)
        except FileExistError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(FileExistError, {'file': re.findall('File (.*) does not exist', str(e))[0]})
        except ConnectionError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(WorkerDoesNotRunError)
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)


class StatusApi(Resource):
    """
    REST-API class для проверки статуса работы
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: Прогресс выполнения и статус выполнения, код ответа

        URL: `/api/pd/v{__version__}/status`

        Пример запроса:
        {
            "access_token", "<Token>",
            "task_id": 0
        }
        """

        apply_limits('120/minute')

        try:
            body = request.get_json()

            access_token: str = body.get('access_token')
            task_id: int = body.get('task_id')

            if not task_id or not access_token:
                raise SomeRequestArgumentsMissing('`task_id` or `access_token` missing')

            decoded = decode_token(access_token)
            user_id = decoded['sub']

            exists = User.find_by_id(user_id) is not None
            if not exists:
                raise UserDoesNotExists

            task = Task.find_by_id(task_id)

            if not task:
                raise NoTasksError

            job_id = task.job_id

            if not job_id:
                raise IncorrectJobIDError('Job_id is `None`')

            job = current_app.task_queue.fetch_job(job_id)

            if not job:
                raise JobDoesNotExist('Job is `None`')

            progress = job.meta.get('progress', 0)
            eta = job.meta.get('eta', 0)
            video_no = job.meta.get('video_no', 0)
            videos_no = job.meta.get('videos_no', 0)
            stage = job.meta.get('stage', '')

            console_logger.debug('StatusApi')

            return {'progress': progress,
                    'status': task.status,
                    'eta': eta,  # Сколько осталось в секундах до конца обработки
                    'video_no': video_no,  # Какое видео обрабатывается сейчас
                    'videos_no': videos_no,  # Сколько всего видео
                    'stage': stage,
                    # Текущий этап обработки (video-processing/video-loading/images-loading/info-loading)
                    }, 200
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'DecodeError, InvalidTokenError: {e}')
            return format_error_to_return(BadTokenError)
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except UserDoesNotExists as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UserDoesNotExists)
        except NoTasksError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(NoTasksError)
        except IncorrectJobIDError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(IncorrectJobIDError)
        except JobDoesNotExist as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(JobDoesNotExist)
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)


class ResultApi(Resource):
    """
    REST-API class для получения результатов выполнения
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: Путь ко всем файлам с результатом в виде списка, а также список словарей для статуса загрузки файлов в облако

        URL: `/api/pd/v{__version__}/result`

        Пример запроса для получения всех файлов текущего пользователя:
        {
            "access_token": "<TOKEN>"
        }

        Пример запроса для получения файла текущей задачи:
        {
            "access_token": "<TOKEN>"
            "task_id": 0
        }
        """

        apply_limits('60/minute')

        try:
            body = request.get_json()

            access_token: str = body.get('access_token')
            task_id: int = body.get('task_id')

            if not access_token:
                raise SomeRequestArgumentsMissing('`access_token` missing')

            decoded = decode_token(access_token)
            user_id = decoded['sub']

            exists = User.find_by_id(user_id) is not None
            if not exists:
                raise UserDoesNotExists

            if task_id:  # Получаем done_res_files для одной задачи по ее id
                task = Task.find_by_id(task_id)

                if not task:
                    raise NoTasksError('No task using `task_id` found')

                done_res_files = task.done_res_files
                upload_files_status = task.upload_data
            else:  # Получаем done_res_files для всех задач пользователя по его id
                tasks = Task.find_by_user_id(user_id, False)

                if not tasks:
                    raise NoTasksError('No tasks using `user_id` found')

                done_res_files = []
                upload_files_status = []

                for task in tasks:
                    done = task.done_res_files
                    upload = task.upload_data

                    upload_files_status.append(upload)

                    if done:
                        done_res_files.extend(done)
                    else:
                        done_res_files.append(done)

            console_logger.debug(
                f'ResultApi: done_res_files: {done_res_files}, upload_files_status: {upload_files_status}')

            return {'files': done_res_files, 'upload_status': upload_files_status}, 200
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'DecodeError, InvalidTokenError: {e}')
            return format_error_to_return(BadTokenError)
        except UserDoesNotExists as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UserDoesNotExists)
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except NoTasksError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(NoTasksError)
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)


class StopJobApi(Resource):
    """
    REST-API class для остановки работы
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: Выполнение остановлено || ошибка, код ответа

        URL: `/api/pd/v{__version__}/stop`

        Пример запроса:
        {
            "access_token", "<Token>",
            "task_id": 0
        }
        """
        from rq.command import send_stop_job_command
        apply_limits('30/minute')

        try:
            body = request.get_json()

            access_token: str = body.get('access_token')
            task_id: int = body.get('task_id')

            if not task_id or not access_token:
                raise SomeRequestArgumentsMissing('`task_id` or `access_token` missing')

            decoded = decode_token(access_token)
            user_id = decoded['sub']

            exists = User.find_by_id(user_id) is not None
            if not exists:
                raise UserDoesNotExists

            task = Task.find_by_id(task_id)

            if not task:
                raise NoTasksError(f'No task with task_id: {task_id}')

            job_id = task.job_id

            if not job_id:
                raise IncorrectJobIDError('Job_id is `None`')

            job = current_app.task_queue.fetch_job(job_id)
            if job is None:  # заменяет отслеживание ошибок `NoRedisConnectionException`, `NoSuchJobError`
                console_logger.debug(f"No job in queue with id: {job_id}")
                raise JobDoesNotExist(f"No job in queue with id: {job_id}")

            console_logger.debug(f'Job: {job}, {job_id}')
            send_stop_job_command(current_app.redis, job_id)

            status = job.get_status()

            task.set_status('stopped')

            console_logger.debug(f'StopJobApi: {job_id} with status: {status}')

            return {'message': 'Job stop', 'status': status}, 200
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'DecodeError, InvalidTokenError: {e}')
            return format_error_to_return(BadTokenError)
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except UserDoesNotExists as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UserDoesNotExists)
        except IncorrectJobIDError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(IncorrectJobIDError)
        except NoTasksError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(NoTasksError)
        except JobDoesNotExist as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(JobDoesNotExist)
        except InvalidJobOperation as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(JobIsNotCurrentlyExecuted)
        # except (NoRedisConnectionException, NoSuchJobError) as e:
        #     get_traceback.error(f'{e}, {type(e)}')
        #     return format_error_to_return(IncorrectJobIDError)
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)
