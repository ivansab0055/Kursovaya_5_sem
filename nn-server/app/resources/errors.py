from typing import Union


class InternalServerError(Exception):
    """
    Unexpected server error is pure `Exception` class
    status: 500
    """


class SomeRequestArgumentsMissing(Exception):
    """
    Some arguments in request are missing
    status: 400
    """


class BadTokenError(Exception):
    """
    Invalid token - from jwt.exceptions (DecodeError, InvalidTokenError)
    status: 403
    """


class ExpiredTokenError(Exception):
    """
    from jwt.exceptions - ExpiredSignatureError
    status: 401
    """


class IncorrectJobIDError(Exception):
    """
    Incorrect job id
    status: 403
    """


class NoTasksError(Exception):
    """
    No tasks were found by user id or task id
    status: 403
    """


class WorkerDoesNotRunError(Exception):
    """
    Worker does not run
    status: 403
    """


class JobDoesNotExist(Exception):
    """
    Job does not exist
    status: 403
    - May be if worker, that run suing `rq worker` have different name, then `Redis` class
    """


class JobIsNotCurrentlyExecuted(Exception):
    """
    Job is not currently executing
    status: 403
    `rq.exceptions.InvalidJobOperation: Job is not currently executing`

    - Возникает, если задача создана, но еще не направлена на выполннение,
    при тестирование может возникнуть если worker еще не поднят
    """


class ArgumentError(Exception):
    """
    The argument is specified incorrectly
    status: 403

    - Возникает, когда переданные аргументы некорректны (тип, дина и т.п.)
    """


class UserDoesNotExists(Exception):
    """
    User does not exists
    status: 403

    - Возникает при проверке существования пользователя
    """


class FileExistError(Exception):
    """
    File does not exist
    status: 403

    - Возникает при проверке существования файла
    """


class BucketSizeExceeded(Exception):
    """
    The size of the bucket has been exceeded
    status: 413

    - Возникает при проверке размера бакета, если его размер превышен, не получится туда ничего сохранить
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
    "IncorrectJobIDError": {
        "message": "Incorrect job ID",
        "status": 403,
        "from": "app",
    },
    "NoTasksError": {
        "message": "No tasks were found by user id or task id",
        "status": 404,
        "from": "app",
    },
    "WorkerDoesNotRunError": {
        "message": "Worker does not run",
        "status": 403,
        "from": "app",
    },
    "JobDoesNotExist": {
        "message": "Job does not exist",
        "status": 404,
        "from": "app",
    },
    "JobIsNotCurrentlyExecuted": {
        "message": "Job is not currently executing",
        "status": 403,
        "from": "app",
    },
    "ArgumentError": {
        "message": "The argument is specified incorrectly",
        "status": 400,
        "from": "app",
    },
    "UserDoesNotExists": {
        "message": "User does not exists",
        "status": 404,
        "from": "app",
    },
    "FileExistError": {
        "message": "File does not exist",
        "status": 404,
        "from": "app",
    },
    "BucketSizeExceeded": {
        "message": "The size of the bucket has been exceeded",
        "status": 413,
        "from": "app",
    },
}


def format_error_to_return(exception: [InternalServerError,
                                       SomeRequestArgumentsMissing,
                                       BadTokenError,
                                       ExpiredTokenError,
                                       IncorrectJobIDError,
                                       NoTasksError,
                                       WorkerDoesNotRunError,
                                       JobDoesNotExist,
                                       JobIsNotCurrentlyExecuted,
                                       ArgumentError,
                                       UserDoesNotExists,
                                       FileExistError,
                                       BucketSizeExceeded,
                                       ],
                           additional_params: Union[dict, None] = None
                           ):
    """
    :param exception: `InternalServerError`, `SomeRequestArgumentsMissing`, `BadTokenError`,
    `ExpiredTokenError`, `IncorrectJobIDError`, `NoTasksError`, `WorkerDoesNotRunError`, `JobDoesNotExist`,
    `JobIsNotCurrentlyExecuted`, `ArgumentError`, `UserDoesNotExists`, `FileExistError`, `BucketSizeExceeded`
    :return: tuple[{message: error}, status]
    :param additional_params: Дополнительные параметры сообщения
    """

    error: dict = ERRORS[exception.__name__]
    status = error['status']
    message = {'message': error['message']}

    if additional_params:
        message.update(additional_params)

    return message, status


if __name__ == '__main__':
    print(format_error_to_return(ExpiredTokenError), format_error_to_return(InternalServerError))
