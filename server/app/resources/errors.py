from typing import Union


class InternalServerError(Exception):
    """
    Неожиданная ошибка сервера - это чистый класс "исключений"
    status: 500
    """


class SomeRequestArgumentsMissing(Exception):
    """
    Некоторые аргументы в запросе отсутствуют
    status: 400
    """


class SchemaValidationError(Exception):
    """
    Некоторые поля в таблице модели отсутствуют (не хватает аргументов) или не прошли проверки Enum или Checks
    status: 400
    """


class EmailAlreadyExistsError(Exception):
    """
    Пользователь с указанным адресом электронной почты уже существует
    status: 400
    """


class UnauthorizedError(Exception):
    """
    Неверное имя пользователя или пароль
    status: 401
    """


class ServerPermissionError(Exception):
    """
    Нет прав для выполнения этого запроса
    status: 401
    """


class EmailError(Exception):
    """
    Пользователь ввел неверный email
    status: 400
    """


class BadTokenError(Exception):
    """
    Недопустимый токен - из jwt.exceptions (`DecodeError`, `InvalidTokenError`)
    status: 403
    """


class ExpiredTokenError(Exception):
    """
    from jwt.exceptions - ExpiredSignatureError
    status: 401
    """


ERRORS = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500,
        "from": "app",
    },
    "SomeRequestArgumentsMissing": {
        "message": "Some arguments in request are missing",
        "status": 400,
        "from": "app",
    },
    "SchemaValidationError": {
        "message": "Request is missing required database fields or didn't pass checks",
        "status": 400,
        "from": "app",
    },
    "EmailAlreadyExistsError": {
        "message": "User with given email address already exists",
        "status": 400,
        "from": "app",
    },
    "UnauthorizedError": {
        "message": "Invalid username, password or access_token",
        "status": 401,
        "from": "app",
    },
    "ServerPermissionError": {
        "message": "You do not have the rights to perform this action",
        "status": 401,
        "from": "app",
    },
    "EmailError": {
        "message": "Email is invalid",
        "status": 400,
        "from": "app",
    },
    "BadTokenError": {
        "message": "Invalid token",
        "status": 403,
        "from": "app",
    },
    "ExpiredTokenError": {
        "message": "Token expired",
        "status": 401,
        "from": "app",
    },

    "NoAuthorizationError": {
        "msg": "Missing Authorization Header",
        "status": 401,
        "from": "jwt",
    },
    "DecodeError": {
        "msg": "Not enough segments",
        "status": 422,
        "from": "jwt",
    },
    "ExpiredSignatureError": {
        "msg": "Token has expired",
        "status": 401,
        "from": "jwt",
    },
    "WrongTokenError": {
        "msg": "Only refresh tokens are allowed",
        "status": 422,
        "from": "jwt",
    },
}


def format_error_to_return(exception: [InternalServerError,
                                       SomeRequestArgumentsMissing,
                                       SchemaValidationError,
                                       EmailAlreadyExistsError,
                                       UnauthorizedError,
                                       ServerPermissionError,
                                       EmailError,
                                       BadTokenError,
                                       ExpiredTokenError,
                                       ],
                           additional_params: Union[dict, None] = None,
                           ) -> tuple[dict, int]:
    """
    :param exception: `InternalServerError`,`SchemaValidationError`, `SomeRequestArgumentsMissing`, `EmailAlreadyExistsError`,
    `UnauthorizedError`, `ServerPermissionError`, `BadTokenError`, `ExpiredTokenError`, `EmailError`
    :param additional_params: Дополнительные параметры сообщения
    :return: tuple[{message: error}, status]

    Форматирует ошибку под формат, который можно отдать клиентской части
    """

    error: dict = ERRORS[exception.__name__]
    status = error['status']
    message = {'message': error['message']}

    if additional_params:
        message.update(additional_params)

    return message, status


if __name__ == '__main__':
    print(format_error_to_return(ExpiredTokenError), format_error_to_return(SchemaValidationError))
