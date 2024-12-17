import re

from email_validator import validate_email, EmailNotValidError
from kallosus_packages.over_logging import GetTraceback

import env_register  # noqa

get_traceback = GetTraceback(__file__)


def is_email_regex_valid(email: str) -> bool:
    """
    :param email: Email пользователя
    :return Прошел ли email валидацию с использованием regex
    """

    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    valid = EMAIL_REGEX.match(email)

    return True if valid else False


def is_email_real_valid(email: str) -> bool:
    """
    :param email: Email пользователя
    :return Прошел ли email валидацию путем отправки пустого сообщения и проверки DNS
    Может не выдавать ошибки, так как проверяется только домен:

    > `check_deliverability=True`: выполняются DNS-запросы, чтобы проверить правильность доменного имени в адресе электронной почты
    """

    try:
        validate_email(email, check_deliverability=True)
        valid = True
    except EmailNotValidError as e:
        get_traceback.error(f'{e}')
        valid = False

    return valid


if __name__ == '__main__':
    real_email = 'admin@kallosus.ru'
    real_email2 = 'pikromat1995@gmail.com'

    unreal_email = 'kek@sabaka.ru'
    print(
        f'{real_email}: regex: {is_email_regex_valid(real_email)}, check_deliverability: {is_email_real_valid(real_email)}')
    print(
        f'{real_email2}: regex: {is_email_regex_valid(real_email2)}, check_deliverability: {is_email_real_valid(real_email2)}')
    print(
        f'{unreal_email}: regex: {is_email_regex_valid(unreal_email)}, check_deliverability: {is_email_real_valid(unreal_email)}')
