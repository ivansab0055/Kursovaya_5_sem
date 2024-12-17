import os

import requests
from flask import request
from flask_restful import Resource
from kallosus_packages.over_logging import GetTraceback, Logger

from config import REACT_APP_RECAPTCHA_SECRET_KEY
from resources.errors import format_error_to_return, InternalServerError, SomeRequestArgumentsMissing
from utils.limiter import apply_limits

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)


class ValidCaptchaApi(Resource):
    def post(self) -> tuple[dict, int]:
        """
        :return:
        Валидируем ReCaptcha

        URL: /api/services/validate_captcha

        Пример запроса:
        Body
        {
            "token": <ReCaptcha user token>
        }
        """

        secret_key = REACT_APP_RECAPTCHA_SECRET_KEY

        if os.environ.get('REACT_APP_RECAPTCHA_SECRET_KEY'):
            secret_key = os.environ.get('REACT_APP_RECAPTCHA_SECRET_KEY')

        apply_limits('5/minute')

        try:
            body = request.get_json()
            token = body.get('token')

            if not token:
                raise SomeRequestArgumentsMissing('Not all arguments are passed in the request, necessary is token')

            response = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': secret_key,
                    'response': token,
                }
            )
            result = response.json()
            console_logger.debug(
                f'token: {token[:4] + "*" + token[-4:]}, response: {response}, {result.get("success")}')

            if result.get('success'):
                return {'success': True}, 200
            else:
                return {'success': False, 'message': 'CAPTCHA verification failed'}, 400

        except SomeRequestArgumentsMissing as e:
            get_traceback.error(f'{e}')
            return format_error_to_return(SomeRequestArgumentsMissing, additional_params={'success': False})
        except InternalServerError as error:
            get_traceback.critical(f'CAPTCHA verification error: {error}')
            return format_error_to_return(InternalServerError, additional_params={'success': False})
