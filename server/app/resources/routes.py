from typing import NoReturn

from flask_restful import Api

from api.admin import AdminUserApi, AdminLoginAsUserApi, AdminGetAllUsersApi
from api.auth import SignupApi, LoginApi, ConfirmApi
from api.captcha import ValidCaptchaApi
from api.mailing import MailingSubscribeApi
from api.reset_password import ForgotPasswordApi, ResetPasswordApi, ChangePasswordApi
from api.tokens import TokenRefreshApi, CheckTokenApi
from api.user import UserApi


def initialize_routes(api: Api) -> NoReturn:
    """
    :param api: `flask_restful.Api`
    :return: `NoReturn`
    """

    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(ConfirmApi, '/api/auth/confirm')
    api.add_resource(LoginApi, '/api/auth/login')
    api.add_resource(UserApi, '/api/auth/user')
    api.add_resource(TokenRefreshApi, '/api/token/refresh')
    api.add_resource(CheckTokenApi, '/api/token/check_token')
    api.add_resource(ForgotPasswordApi, '/api/auth/forgot')
    api.add_resource(ResetPasswordApi, '/api/auth/reset')
    api.add_resource(ChangePasswordApi, '/api/auth/change_password')
    api.add_resource(ValidCaptchaApi, '/api/services/validate_captcha')
    api.add_resource(MailingSubscribeApi, '/api/mailing/subscribe')
    api.add_resource(AdminUserApi, '/api/admin/user/<int:user_id>')
    api.add_resource(AdminLoginAsUserApi, '/api/admin/login_as/<int:user_id>')
    api.add_resource(AdminGetAllUsersApi, '/api/admin/users')
