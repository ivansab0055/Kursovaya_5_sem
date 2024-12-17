from database.models import User
from flask import request
from flask_jwt_extended import decode_token
from flask_restful import Resource
from jwt.exceptions import (ExpiredSignatureError,
                            DecodeError,
                            InvalidTokenError,
                            )
from kallosus_packages.over_logging import Logger, GetTraceback

from resources.errors import (format_error_to_return,
                              InternalServerError,
                              SomeRequestArgumentsMissing,
                              ExpiredTokenError,
                              BadTokenError,
                              UserDoesNotExists,
                              )
from storage.S3 import StorageApi
from utils.limiter import apply_limits

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)

Storage = StorageApi()


class CreateFoldersApi(Resource):
    """
    REST-API class для создания всех необходимых папок
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: путь до папки с данным src файлом || ошибка, код ответа

        Создаем необходимые папки

        Пример запроса:
        Body:
        ```
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjN9.2e6bS75p5SyJpacHBFic5KTMa8WA_UChrrAH8pucpyM",
            "num_folders": 2
        }
        ```
        """

        apply_limits('6 per minute')

        try:
            body = request.get_json()

            access_token: str = body.get('access_token')
            num_folders: int = body.get('num_folders')

            console_logger.debug(f'{body}')

            if not access_token or not num_folders:
                raise SomeRequestArgumentsMissing('Not all arguments are passed in the request')

            decoded = decode_token(access_token)
            user_id = decoded['sub']

            exists = User.find_by_id(user_id) is not None

            if not exists:
                raise UserDoesNotExists

            user_folder = Storage.create_user_folder(user_id)
            dd_mm_yy_folder = Storage.create_dd_mm_yy_folder(user_folder)

            folders = []
            for i in range(num_folders):
                folders.append(Storage.create_current_time_folder(dd_mm_yy_folder))

            console_logger.debug(f'{folders}')
            return {'folders': folders}, 200
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'DecodeError, InvalidTokenError: {e}')
            return format_error_to_return(BadTokenError)
        except UserDoesNotExists as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UserDoesNotExists)
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)
