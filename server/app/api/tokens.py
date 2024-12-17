from flask import request
from flask_jwt_extended import (create_access_token,
                                jwt_required,
                                get_jwt_identity,
                                decode_token,
                                )
from flask_restful import Resource
from jwt.exceptions import (DecodeError,
                            InvalidTokenError,
                            ExpiredSignatureError,
                            )
from kallosus_packages.over_logging import Logger, GetTraceback

from resources.errors import (InternalServerError,
                              format_error_to_return,
                              BadTokenError,
                              SomeRequestArgumentsMissing,
                              ExpiredTokenError,
                              )
from utils.limiter import apply_limits

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)


class CheckTokenApi(Resource):
    """
    REST-API для проверки токена
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: информация, полученная при декодировании токена || ошибка, код ответа

        URL: /api/token/check_token

        Пример запроса:
        Body
        {
            "<TOKEN_TYPE>_token": <TOKEN>
        }

        TOKEN_TYPE: access, refresh, confirm, reset

        Запрос должен содержать токен `jwt`
        """

        apply_limits('100 per minute')

        try:
            body = request.get_json()

            token = body.get('access_token')

            if not token:
                token = body.get('refresh_token')
                if not token:
                    token = body.get('confirm_token')
                    if not token:
                        token = body.get('reset_token')

            if not token:
                raise SomeRequestArgumentsMissing(
                    'Arguments are not passed in the request, necessary is `access_token` or `refresh_token` or `reset_token`')

            info = decode_token(token)

            console_logger.debug(f'Token info: {info}')

            return {'message': 'OK'}, 200
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(BadTokenError)
        except Exception as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)


class TokenRefreshApi(Resource):
    """
    REST-API class для обновления токена

    `@jwt_required(refresh=True)` означает, что мы можем обновить `access_token`, пока `refresh_token` не истек,
    в нашем случае 4 раза (28 дней - время жизни `JWT_REFRESH_TOKEN_EXPIRES` / 7 дней - время жизни `JWT_ACCESS_TOKEN_EXPIRES`)

    У этого класса есть другой api обработки ошибок, непосредственно из модуля `jwt`
    (они обрабатываются с указанием модуля, который ее выдал (`from: 'jwt'`):
    `jwt.exceptions.NoAuthorizationError: {'msg': 'Missing Authorization Header'}, 401`
    `jwt.exceptions.DecodeError: {'msg': 'Not enough segments'}, 422`
    `jwt.exceptions.ExpiredSignatureError: {'msg': 'Token has expired'}, 401`
    `flask_jwt_extended.exceptions.WrongTokenError: {'msg': 'Only refresh tokens are allowed'}, 422`
    """

    @jwt_required(refresh=True)
    def post(self) -> tuple[dict, int]:
        """
        :return: Новый токен доступа, код ответа

        URL: /api/auth/refresh

        Пример запроса (В header):
        Headers Authorization: Bearer <REFRESH_TOKEN>
        """

        apply_limits('1 per day')

        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        return {'access_token': access_token}, 200
