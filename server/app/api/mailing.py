from flask import request
from flask_jwt_extended import decode_token
from flask_restful import Resource
from jwt.exceptions import (DecodeError,
                            InvalidTokenError,
                            ExpiredSignatureError,
                            )
from kallosus_packages.over_logging import GetTraceback, Logger

from database.models import User
from resources.errors import (InternalServerError,
                              format_error_to_return,
                              BadTokenError,
                              SomeRequestArgumentsMissing,
                              ExpiredTokenError,
                              UnauthorizedError,
                              )
from utils.limiter import apply_limits

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)


class MailingSubscribeApi(Resource):
    def post(self) -> tuple[dict, int]:
        """
        :return:
        Устанавливаем параметр рассылки

        URL: /api/mailing/subscribe

        Пример запроса:
        Body
        {
            "access_token": "test@test.com",
            "subscribe": true
        }
        """

        apply_limits('5 per minute')

        try:
            body = request.get_json()
            access_token = body.get('access_token')
            subscribe = body.get('subscribe')

            if not access_token or subscribe is None:
                raise SomeRequestArgumentsMissing(
                    'Not all arguments are passed in the request, necessary is access_token and subscribe')

            info = decode_token(access_token)
            user_id = info['sub']

            user = User.find_by_id(user_id)
            if not user:
                raise UnauthorizedError

            user.set_subscribe(subscribe)

            return {'message': 'Subscription changed'}, 200
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
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)
