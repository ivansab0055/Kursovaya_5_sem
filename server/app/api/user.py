from flask import request
from flask_jwt_extended import decode_token
from flask_restful import Resource
from jwt.exceptions import (ExpiredSignatureError,
                            DecodeError,
                            InvalidTokenError,
                            )
from kallosus_packages.over_logging import Logger, GetTraceback

from database.models import User
from resources.errors import (SomeRequestArgumentsMissing,
                              InternalServerError,
                              BadTokenError,
                              ExpiredTokenError,
                              format_error_to_return,
                              UnauthorizedError
                              )
from utils.limiter import apply_limits

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)


class UserApi(Resource):
    """
    REST-API для получения всех данных пользователя из БД в json формате
    """

    def get(self) -> tuple[dict, int]:
        """
        :return: информация о пользователе || ошибка, код ответа

        URL: /api/auth/user

        Пример запроса:
        Header
        Authorization: Bearer <ACCESS_TOKEN>
        """

        apply_limits('60 per minute')

        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise SomeRequestArgumentsMissing('Access token is missing or invalid')

            access_token = auth_header.split(' ')[1]

            if not access_token:
                raise SomeRequestArgumentsMissing

            user_id = decode_token(access_token)['sub']

            user = User.find_by_id(user_id)
            if not user:
                raise UnauthorizedError('The user was not found')

            data = user.json()

            return data, 200
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(BadTokenError)
        except UnauthorizedError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UnauthorizedError)
        except Exception as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)
