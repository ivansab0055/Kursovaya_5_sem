import os

from dotenv import load_dotenv
from flask import current_app, request, render_template
from flask_jwt_extended import (create_access_token,
                                decode_token,
                                create_refresh_token,
                                )
from flask_restful import Resource
from jwt.exceptions import (ExpiredSignatureError,
                            DecodeError,
                            InvalidTokenError,
                            )
from kallosus_packages.over_logging import Logger, GetTraceback

from config import DEBUG
from database.models import User
from resources.errors import (InternalServerError,
                              BadTokenError,
                              ExpiredTokenError,
                              SomeRequestArgumentsMissing,
                              format_error_to_return,
                              EmailError,
                              UnauthorizedError,
                              )
from services.mail_service import send_email
from utils.limiter import apply_limits
from utils.validators import is_email_regex_valid

load_dotenv()

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)


class ForgotPasswordApi(Resource):
    """
    REST-API class для обработки нажатия кнопки забыли пароль,
    чтобы выслать на почту ссылку на страницу с вводом нового пароля
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: ссылка на страницу сброса пароля с токеном в ней || ошибка, код ответа

        request.host_url + 'reset/' - ссылка для перенаправления в почте

        URL: /api/auth/forgot

        Пример запроса:
        Body
        {
            "email": "test@test.com",
            "confirmation": false
        }
        """

        apply_limits('3 per 5 minute')

        url = request.host_url + 'reset/'

        try:
            body = request.get_json()
            email = body.get('email')
            confirmation = True if (body.get('confirmation') is None or not DEBUG) else body.get('confirmation')

            if not email:
                raise SomeRequestArgumentsMissing

            if not is_email_regex_valid(email):
                console_logger.debug('Did not pass `is_email_regex_valid`')
                raise EmailError

            user = User.find_by_email(email)

            if not user:
                raise UnauthorizedError

            user_id = str(user.id)
            user_email = user.email

            expires = current_app.config['CONFIRM_RESET_EXPIRES']
            hours = expires.days * 24 + expires.seconds // 3600
            reset_token = create_access_token(user_id, expires_delta=expires)

            console_logger.debug(f'Reset token: {reset_token}')

            if os.environ.get('UNIT_TEST') in ['0', None] and confirmation:
                return send_email(subject='[Kallosus] Сброс пароля',
                                  sender=current_app.config["MAIL_USERNAME"],
                                  recipients=[user_email],
                                  text_body=render_template('reset_password/reset_password.txt',
                                                            url=url + reset_token,
                                                            expires=str(hours),
                                                            support_email=current_app.config['SUPPORT_EMAIL'],
                                                            ),
                                  html_body=render_template('reset_password/reset_password.html',
                                                            url=url + reset_token,
                                                            expires=str(hours),
                                                            support_email=current_app.config['SUPPORT_EMAIL'],
                                                            ),
                                  )
            else:
                return {'url': url + reset_token}, 200
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except EmailError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(EmailError)
        except UnauthorizedError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UnauthorizedError)
        except Exception as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)


class ResetPasswordApi(Resource):
    """
    REST-API для сброса пароля, страница, с этим запросом содержит поле ввода нового пароля

    Пример запроса:
    Body
    {
        "reset_token": <TOKEN>,
        "password": <NEW_PASSWORD>,
        "emailing": false
    }
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: информация о том, что сообщение отправлено || токены || ошибка, код ответа

        URL: /api/auth/reset

        Запрос должен содержать "токен jwt", полученный по URL-адресу, и новый пароль
        """

        apply_limits('3 per 5 minute')

        url = request.host_url + 'lk/'

        try:
            body = request.get_json()

            reset_token = body.get('reset_token')
            password = body.get('password')
            emailing = True if (body.get('emailing') is None or not DEBUG) else body.get('emailing')

            if not reset_token or not password:
                raise SomeRequestArgumentsMissing(
                    'Not all arguments are passed in the request, necessary is reset_token and password')

            user_id = decode_token(reset_token)[
                'sub']  # sub - это ключ по умолчанию, используемый для хранения идентификатора (user ID)

            user = User.find_by_id(user_id)
            if not user:
                raise UnauthorizedError

            user.update_password(password)
            user.update_last_login()

            user_id = str(user.id)
            user_email = user.email

            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)

            if os.environ.get('UNIT_TEST') in ['0', None] and emailing:
                send_email(subject='[Kallosus] Пароль успешно сброшен',
                           sender=current_app.config["MAIL_USERNAME"],
                           recipients=[user_email],
                           text_body=render_template('pwd_reset_successfully/reset.txt',
                                                     url=url,
                                                     support_email=current_app.config['SUPPORT_EMAIL'],
                                                     ),
                           html_body=render_template('pwd_reset_successfully/reset.html',
                                                     url=url,
                                                     support_email=current_app.config['SUPPORT_EMAIL'],
                                                     ),
                           )

            return {'access_token': access_token,
                    'refresh_token': refresh_token,
                    }, 200
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
        except Exception as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)


class ChangePasswordApi(Resource):
    """
    REST-API для смены пароля

    Пример запроса:
    Body
    {
        "access_token": <ACCESS_TOKEN>,
        "old_password": <OLD_PASSWORD>,
        "new_password": <NEW_PASSWORD>,
        "emailing": true
    }
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: информация о том, что пароль сброшен || ошибка, код ответа

        URL: /api/auth/change_password
        """

        apply_limits('1 per minute')

        try:
            body = request.get_json()

            access_token = body.get('access_token')
            old_password = body.get('old_password')
            new_password = body.get('new_password')

            emailing = True if (body.get('emailing') is None or not DEBUG) else body.get('emailing')

            if not access_token or not old_password or not new_password:
                raise SomeRequestArgumentsMissing(
                    'Not all arguments are passed in the request, necessary is access_token, old_password and new_password')

            user_id = decode_token(access_token)['sub']

            user = User.find_by_id(user_id)

            if not user:
                raise UnauthorizedError

            authorized = user.check_password(old_password)

            if not authorized:
                raise UnauthorizedError

            user.update_password(new_password)
            user_email = user.email

            if os.environ.get('UNIT_TEST') in ['0', None] and emailing:
                send_email(subject='[Kallosus] Пароль успешно изменен',
                           sender=current_app.config["MAIL_USERNAME"],
                           recipients=[user_email],
                           text_body=render_template('change_password/changed.txt',
                                                     support_email=current_app.config['SUPPORT_EMAIL'],
                                                     ),
                           html_body=render_template('change_password/changed.html',
                                                     support_email=current_app.config['SUPPORT_EMAIL'],
                                                     ),
                           )

            return {'message': 'Password changed'}, 200
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
