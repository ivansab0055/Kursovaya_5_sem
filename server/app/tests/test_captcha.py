import json
import os
from typing import NoReturn

from kallosus_packages.over_logging import Logger

from config.config_prod import REACT_APP_RECAPTCHA_SECRET_KEY as PROD_SECRET_KEY
from config.config_test import REACT_APP_RECAPTCHA_SECRET_KEY as TEST_SECRET_KEY
from tests.BaseCase import BaseCase

console_logger = Logger(__file__)


class TestCaptcha(BaseCase):
    def test_successfully(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем успешное выполнение запроса
        """

        # Given
        payload = json.dumps(
            {
                'token': '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
            }
        )

        # Check token
        response = self.test_client.post('/api/services/validate_captcha',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        self.assertEqual(True, response.json['success'])
        self.assertEqual(200, response.status_code)

    def test_without_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `SomeRequestArgumentsMissing`
        """

        # Given
        payload = json.dumps(
            {

            }
        )

        # Check token
        response = self.test_client.post('/api/services/validate_captcha',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        self.assertEqual(False, response.json['success'])
        self.assertEqual('Some arguments in request are missing', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_with_fake_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `CAPTCHA verification failed`
        """

        os.environ['REACT_APP_RECAPTCHA_SECRET_KEY'] = PROD_SECRET_KEY

        # Given
        payload = json.dumps(
            {
                'token': '123'
            }
        )

        # Check token
        response = self.test_client.post('/api/services/validate_captcha',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        os.environ['REACT_APP_RECAPTCHA_SECRET_KEY'] = TEST_SECRET_KEY
        self.assertEqual(False, response.json['success'])
        self.assertEqual('CAPTCHA verification failed', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_with_fake_secret_key(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `CAPTCHA verification failed`
        """

        os.environ['REACT_APP_RECAPTCHA_SECRET_KEY'] = 'fake key'

        # Given
        payload = json.dumps(
            {
                'token': '123'
            }
        )

        # Check token
        response = self.test_client.post('/api/services/validate_captcha',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        os.environ['REACT_APP_RECAPTCHA_SECRET_KEY'] = TEST_SECRET_KEY
        self.assertEqual(False, response.json['success'])
        self.assertEqual('CAPTCHA verification failed', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_with_fake_secret_key_and_real_token(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем срабатывание ошибки `CAPTCHA verification failed`
        """

        os.environ['REACT_APP_RECAPTCHA_SECRET_KEY'] = 'fake key'

        # Given
        payload = json.dumps(
            {
                'token': '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
            }
        )

        # Check token
        response = self.test_client.post('/api/services/validate_captcha',
                                         headers={'Content-Type': 'application/json'},
                                         data=payload,
                                         )

        os.environ['REACT_APP_RECAPTCHA_SECRET_KEY'] = TEST_SECRET_KEY
        self.assertEqual(False, response.json['success'])
        self.assertEqual('CAPTCHA verification failed', response.json['message'])
        self.assertEqual(400, response.status_code)

    def test_limits(self) -> NoReturn:
        """
        :return: `NoReturn`
        Проверяем ошибку TOO MANY REQUESTS
        """

        os.environ['LIMITER_LIMIT'] = '1 per 3 minute'

        # Given
        payload = json.dumps(
            {
                'token': '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
            }
        )

        for i in range(2):
            # When
            response = self.test_client.post('/api/services/validate_captcha',
                                             headers={'Content-Type': 'application/json'},
                                             data=payload,
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
        response = self.test_client.get(f'/api/services/validate_captcha',
                                        headers={"Content-Type": "application/json"},
                                        data=payload,
                                        )

        # Then
        self.assertEqual('The method is not allowed for the requested URL.', response.json['message'])
        self.assertEqual(405, response.status_code)
