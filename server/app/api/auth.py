import os

from flask import request, render_template, current_app
from flask_bcrypt import generate_password_hash
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                decode_token,
                                )
from flask_restful import Resource
from jwt.exceptions import (ExpiredSignatureError,
                            DecodeError,
                            InvalidTokenError,
                            )
from kallosus_packages.over_logging import Logger, GetTraceback
from sqlalchemy.exc import ProgrammingError, IntegrityError

from config import DEBUG
from database.models import User
from resources.errors import (SchemaValidationError,
                              UnauthorizedError,
                              InternalServerError,
                              EmailAlreadyExistsError,
                              EmailError,
                              format_error_to_return,
                              ExpiredTokenError,
                              BadTokenError,
                              SomeRequestArgumentsMissing,
                              )
from services.mail_service import send_email
from utils.limiter import apply_limits
from utils.validators import is_email_regex_valid, is_email_real_valid

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)


class SignupApi(Resource):
    """
    REST-API class для регистрации
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: ссылка на страницу подтверждения || ошибка, код ответа

        URL: /api/auth/signup

        Пример запроса:
        Body
        {
            "email": "test@test.com",
            "company": "Test company",
            "password": "Test password",
            "confirmation": false
        }
        """

        apply_limits('5 per 5 minute')

        url = request.host_url + 'confirm/'

        try:
            body = request.get_json()

            email = body.get('email')
            password = body.get('password')
            company = body.get('company')
            confirmation = True if (body.get('confirmation') is None or not DEBUG) else body.get('confirmation')

            if not (email and password and company):
                raise SomeRequestArgumentsMissing(
                    'Not all arguments are passed in the request, necessary is email, password, company')

            if not is_email_regex_valid(email):
                raise EmailError

            exists = User.find_by_email(email) is not None

            if exists:
                raise EmailAlreadyExistsError

            if not is_email_real_valid(email):
                console_logger.debug(f'Email does not pass is_email_real_valid')
                raise EmailError

            hashed_pwd = generate_password_hash(password).decode('utf8')

            additional_claims = {"email": email, "password": hashed_pwd, "company": company}

            expires = current_app.config['CONFIRM_RESET_EXPIRES']
            hours = expires.days * 24 + expires.seconds // 3600
            confirm_token = create_access_token(identity=email,
                                                additional_claims=additional_claims,
                                                expires_delta=expires,
                                                )

            if os.environ.get('UNIT_TEST') in ['0', None] and confirmation:
                return send_email(subject='[Kallosus] Подтвердите свою почту',
                                  sender=current_app.config["MAIL_USERNAME"],
                                  recipients=[email],
                                  text_body=render_template('confirm_email/confirm_email.txt',
                                                            url=url + confirm_token,
                                                            expires=str(hours),
                                                            support_email=current_app.config['SUPPORT_EMAIL'],
                                                            ),
                                  html_body=render_template('confirm_email/confirm_email.html',
                                                            url=url + confirm_token,
                                                            expires=str(hours),
                                                            support_email=current_app.config['SUPPORT_EMAIL'],
                                                            ),
                                  )
            else:
                return {'url': url + confirm_token}, 200
        except EmailAlreadyExistsError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(EmailAlreadyExistsError)
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except EmailError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(EmailError)
        except Exception as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)


class ConfirmApi(Resource):
    """
    Rest-API для подтверждения почты после регистрации
    """

    def post(self) -> tuple[dict, int]:
        """
        :return: информация о том, что сообщение отправлено || токены || ошибка, код ответа

        URL: /api/auth/confirm

        Пример запроса:
        Body
        {
            "confirm_token": "",
            "emailing": false
        }
        """

        apply_limits('5 per 5 minute')

        url = request.host_url + 'lk/'

        try:
            body = request.get_json()
            console_logger.debug(f'{body}')
            confirm_token = body.get('confirm_token')

            if not confirm_token:
                raise SomeRequestArgumentsMissing(
                    'Not all arguments are passed in the request, necessary is confirm_token')

            user_info = decode_token(confirm_token)

            email = user_info.get('email')
            password = user_info.get('password')  # Уже зашифрованный пароль
            company = user_info.get('company')
            emailing = True if (body.get('emailing') is None or not DEBUG) else body.get('emailing')

            if not (email and password and company):
                raise SchemaValidationError(
                    'Some arguments in `confirm_token` are missing, necessary is email, password and company')

            user = User(email=user_info['email'],
                        password=user_info['password'],
                        company=user_info['company'],
                        mailing=False,
                        role='user',
                        )

            user.save_to_db()

            user_id = str(user.id)
            user_email = user.email

            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)

            console_logger.debug(f'access_token: {access_token},\n refresh_token: {refresh_token}')

            if os.environ.get('UNIT_TEST') in ['0', None] and emailing:
                send_email(subject='[Kallosus] Почта успешно подтверждена',
                           sender=current_app.config["MAIL_USERNAME"],
                           recipients=[user_email],
                           text_body=render_template('email_confirmed/confirmed.txt',
                                                     url=url,
                                                     support_email=current_app.config['SUPPORT_EMAIL'],
                                                     ),
                           html_body=render_template('email_confirmed/confirmed.html',
                                                     url=url,
                                                     support_email=current_app.config['SUPPORT_EMAIL'],
                                                     ),
                           )

            return {'access_token': access_token,
                    'refresh_token': refresh_token,
                    }, 200
        except SchemaValidationError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SchemaValidationError)
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except ExpiredSignatureError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(ExpiredTokenError)
        except IntegrityError as e:
            get_traceback.error(f'{e}')
            if 'UNIQUE constraint failed: user.email' in str(e) or 'Duplicate entry' in str(e):
                return format_error_to_return(EmailAlreadyExistsError)
            else:
                return format_error_to_return(SchemaValidationError)
        except ProgrammingError as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SchemaValidationError)
        except (DecodeError, InvalidTokenError) as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(BadTokenError)
        except Exception as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)


class LoginApi(Resource):
    """
    REST-API class для входа

    Ошибки:
    Invalid salt:
    Если пароль не был зашифрован - INSERT INTO public."user" (email, company, password, date)
    VALUES ('BAD_PWD@bad.com', 'Company', '123456', '23-02-2004');

    """

    def post(self) -> tuple[dict, int]:
        """
        :return: токены || ошибка, код ответа

        URL: /api/auth/login

        Пример запроса:
        Body
        {
            "email": "test@gmail.com",
            "password": "12345678"
        }
        """

        apply_limits('5 per 5 minute')

        try:
            body = request.get_json()

            email = body.get('email')
            password = body.get('password')

            if not email or not password:
                raise SomeRequestArgumentsMissing(
                    'Not all arguments are passed in the request, necessary is email and password')

            user = User.find_by_email(email)

            if not user:
                raise UnauthorizedError

            authorized = user.check_password(password)

            if not authorized:
                raise UnauthorizedError

            user.update_last_login()

            user_id = str(user.id)

            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)

            return {'access_token': access_token,
                    'refresh_token': refresh_token,
                    }, 200
        except (UnauthorizedError, ProgrammingError) as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(UnauthorizedError)
        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing)
        except ValueError as e:
            if str(e) == 'Invalid salt':
                get_traceback.critical(f'{e}', print_full_exception=True)
                return format_error_to_return(UnauthorizedError)
            else:
                raise Exception
        except Exception as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            return format_error_to_return(InternalServerError)
