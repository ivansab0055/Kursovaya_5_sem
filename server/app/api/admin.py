from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import decode_token
from flask_restful import Resource
from jwt.exceptions import (DecodeError,
                            InvalidTokenError,
                            ExpiredSignatureError,
                            )
from kallosus_packages.over_logging import GetTraceback, Logger
from sqlalchemy.exc import DataError


from database.models import db_rollback, User
from resources.errors import (InternalServerError,
                              format_error_to_return,
                              BadTokenError,
                              SomeRequestArgumentsMissing,
                              ExpiredTokenError,
                              UnauthorizedError,
                              EmailError,
                              SchemaValidationError,
                              ServerPermissionError,
                              )
from utils.limiter import apply_limits
from utils.validators import is_email_regex_valid, is_email_real_valid

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)


class AdminUserApi(Resource):
    """
    REST-API для администрирования пользователей (редактирование, удаление)
    """

    def post(self, user_id: int) -> tuple[dict, int]:
        """
        Обновление данных пользователя.

        URL: /api/admin/user/<user_id>

        Пример запроса:
        Body
        {
            "access_token": "<ACCESS_KEY>",
            "email": "<NEW_EMAIL>",
            "password": "<NEW_PASSWORD>",
            "role": "<NEW_ROLE>",
            "company": "Umbrella",
            "mailing": false
        }
        """

        apply_limits('30 per minute')

        try:
            body = request.get_json()

            access_token: str = body.get('access_token')
            email: str = body.get('email')
            password: str = body.get('password')
            role: str = body.get('role')
            company: str = body.get('company')
            mailing: bool = body.get('mailing')

            if not access_token or not (email or password or role or company or mailing):
                raise SomeRequestArgumentsMissing(
                    'Not all arguments are passed in the request, necessary is access_token and email|password|role|company|mailing')

            # Получаем текущего пользователя
            admin_id = decode_token(access_token)['sub']
            admin_user = User.find_by_id(admin_id)

            if not admin_user:
                raise UnauthorizedError('The administrator was not found')

            if admin_user.role != 'admin':
                raise ServerPermissionError("You do not have the rights to perform this action")

            # Начинаем редактировать пользователя
            user = User.find_by_id(user_id)

            if not user:
                raise UnauthorizedError('The user was not found')

            if user.role == 'admin':
                raise ServerPermissionError("You do not have the rights to edit admin")

            # Обновляем данные пользователя
            if email:
                if not is_email_regex_valid(email) or not is_email_real_valid(email):
                    console_logger.debug(f'Email does not pass is_email_real_valid')
                    raise EmailError

                user.update_email(email)
            if password:
                user.update_password(password)
            if role:
                user.update_role(role)
            if company:
                user.update_company(company)
            if mailing:
                user.set_subscribe(mailing)

            return {"message": "The user's data has been updated"}, 200
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except UnauthorizedError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UnauthorizedError)
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(BadTokenError)
        except EmailError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(EmailError)
        except ServerPermissionError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ServerPermissionError)
        except DataError as e:
            db_rollback()
            get_traceback.error(f'{e}')  # psycopg2.errors.InvalidTextRepresentation
            return format_error_to_return(SchemaValidationError)
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)

    def delete(self, user_id: int) -> tuple[dict, int]:
        """
        Удаление пользователя.

        URL: /api/admin/user/<user_id>

        Пример запроса:
        Header
        Authorization: Bearer <ACCESS_TOKEN>
        """

        apply_limits('30 per minute')

        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise SomeRequestArgumentsMissing('Access token is missing or invalid')

            access_token = auth_header.split(' ')[1]

            if not access_token:
                raise SomeRequestArgumentsMissing(
                    'Not all arguments are passed in the request, necessary is access_token')

            admin_id = decode_token(access_token)['sub']
            admin_user = User.find_by_id(admin_id)

            if not admin_user:
                raise UnauthorizedError('The administrator was not found')

            if admin_user.role != 'admin':
                raise ServerPermissionError("You do not have the rights to perform this action")

            user = User.find_by_id(user_id)

            if not user:
                raise UnauthorizedError('The user was not found')

            user.delete_from_db()

            return {"message": "The user has been deleted"}, 200
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except UnauthorizedError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UnauthorizedError)
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(BadTokenError)
        except ServerPermissionError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ServerPermissionError)
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)


class AdminLoginAsUserApi(Resource):
    """
    REST-API для администрирования пользователей (вход от его имени)
    """

    def get(self, user_id: int) -> tuple[dict, int]:
        """
        Вход от имени другого пользователя.

        URL: /api/admin/login_as/<user_id>

        Пример запроса:
        Header
        Authorization: Bearer <ACCESS_TOKEN>
        """

        apply_limits('30 per minute')

        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise SomeRequestArgumentsMissing('Access token is missing or invalid')

            access_token = auth_header.split(' ')[1]

            if not access_token:
                raise SomeRequestArgumentsMissing(
                    'Not all arguments are passed in the request, necessary is access_token')

            admin_id = decode_token(access_token)['sub']
            admin_user = User.find_by_id(admin_id)

            if not admin_user:
                raise UnauthorizedError('The administrator was not found')

            if admin_user.role != 'admin':
                raise ServerPermissionError("You do not have the rights to perform this action")

            target_user = User.find_by_id(user_id)

            if not target_user:
                raise UnauthorizedError('The user was not found')

            # Генерация токена для целевого пользователя
            token = create_access_token(identity=user_id)

            return {"access_token": token}, 200
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except UnauthorizedError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UnauthorizedError)
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except ServerPermissionError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ServerPermissionError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(BadTokenError)
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)


class AdminGetAllUsersApi(Resource):
    """
    REST-API для получения всех данных пользователя из БД в json формате
    """

    def get(self) -> tuple[dict, int]:
        """
        :return: информация о всех пользователях || ошибка, код ответа

        URL: /api/admin/users

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
                raise SomeRequestArgumentsMissing(
                    'Not all arguments are passed in the request, necessary is access_token')

            admin_id = decode_token(access_token)['sub']
            admin_user = User.find_by_id(admin_id)

            if not admin_user:
                raise UnauthorizedError('The administrator was not found')

            if admin_user.role != 'admin':
                raise ServerPermissionError("You do not have the rights to perform this action")

            users = User.get_all()
            data = {}
            for user in users:
                data[user.id] = user.json()

            return data, 200
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except UnauthorizedError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UnauthorizedError)
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except ServerPermissionError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ServerPermissionError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(BadTokenError)
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)
