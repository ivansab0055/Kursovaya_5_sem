import json
import mimetypes
import os
import time
from typing import NoReturn, Callable, Union

import boto3
import cv2
import numpy as np
from boto3.s3.transfer import TransferConfig
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError
from kallosus_packages.over_logging import Logger, GetTraceback
from tqdm import tqdm

import env_register  # noqa
from storage import local_main_s3_path, local_test_s3_path, remote_main_s3_path, remote_test_s3_path

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)


class ProgressPercentage:
    def __init__(self, filename, callback: Union[Callable, None] = None):
        """
        :param filename: Путь до файла
        :param callback: Обратный вызов, в него передается процент загруженного видео
        """

        self._filename = filename
        self._callback = callback

        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = tqdm(total=self._size, unit='B', unit_scale=True, desc=filename)

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount
        self._lock.update(bytes_amount)

        if self._callback:
            self._callback(self.get_progress())

    def get_progress(self) -> float:
        """
        :return: `float`
        Возвращает прогресс загрузки файла в S3, не в процентах
        """

        return self._seen_so_far / self._size


class StorageApi:
    """
    API для работы с файловыми хранилищами, будь то локальное или S3 хранилище. При работе на Windows,
    пути автоматически форматируются под Unix формат, но для папок необходимо явно указывать, что это папка,
    с помощью обратного слеша.
    Путь должен быть обработан с использованием функционала `StorageApi.path_join`, без этого использовать функции Api запрещено.
    """

    def __init__(self, storage: str = os.getenv('DATA_STORAGE')):
        """
        :param storage: `os.getenv('DATA_STORAGE')` локальное или удаленное хранилище - local/s3
        """

        self.storage = storage
        self.s3: boto3.client = None

        if self.storage not in ['local', 's3']:
            raise EnvironmentError('DATA_STORAGE must be either local or s3')

        if self.storage == 's3':
            self._auth()

        self.bucket_name = 'kallosus-data-storage'

    def get_storage(self) -> str:
        """
        :return: `self.storage`
        """

        return self.storage

    def set_storage(self, value: str):
        """
        :param value: Значение `self.storage`
        :return:
        """

        if self.storage != value:
            self.storage = value

            if value == 's3':
                self._auth()

    def _auth(self) -> NoReturn:
        """
        :return:
        Авторизация
        """

        # Настройка конфигурации с повторными попытками
        config = Config(
            retries={
                'max_attempts': 3,  # Максимальное количество попыток
                'mode': 'standard'  # Стандартный режим повтора
            }
        )

        self.s3 = boto3.client("s3",
                               endpoint_url="https://s3.storage.selcloud.ru",
                               region_name="ru-1",
                               aws_access_key_id="56c93acad0814ed1a7da9cc5469bb6c8",
                               aws_secret_access_key="e09f00af41e246cb8601da8d4cab8b27",
                               config=config,
                               )

    def get_user_folder(self, user_id: int) -> str:
        """
        :param user_id: идентификатор пользователя для создания основной папки пользователя
        :return: Путь до папки пользователя
        """

        if self.storage == 'local':
            if os.environ.get('UNIT_TEST') in ['0', None]:
                path = local_main_s3_path
            else:
                path = local_test_s3_path

            user_folder = self.path_join(path, str(user_id))
        else:
            if os.getenv('DEBUG') == 'True':
                user_folder = self.path_join(remote_test_s3_path, str(user_id))
            else:
                user_folder = self.path_join(remote_main_s3_path, str(user_id))

            user_folder = self.ensure_trailing_slash(user_folder)

        return user_folder

    def create_user_folder(self, user_id: int) -> str:
        """
        :param user_id: идентификатор пользователя для создания основной папки пользователя
        :return: путь до папки
        """

        user_folder = self.get_user_folder(user_id)

        if not self.path_exists(user_folder):
            self.makedirs(user_folder)
            console_logger.debug(f'{self.storage}: user_folder - {user_folder} created')

        return user_folder

    def create_dd_mm_yy_folder(self, user_folder: str) -> str:
        """
        :param user_folder: путь к основной папке пользователя
        :return: путь до папки dd_mm_yy
        """

        dmy = time.strftime("%d_%m_%y")
        dd_mm_yy_folder = self.ensure_trailing_slash(self.path_join(user_folder, dmy))

        if not self.path_exists(dd_mm_yy_folder):
            self.makedirs(dd_mm_yy_folder)
            console_logger.debug(f'{self.storage}: dd_mm_yy - {dd_mm_yy_folder} created')

        return dd_mm_yy_folder

    def create_current_time_folder(self, dd_mm_yy: str) -> str:
        """
        :param dd_mm_yy: Путь до папки пользователя и папки дня, в который было загружено видео
        :return: Путь до папки current_time (user_folder, dd_mm_yy, current_time)
        """

        current_time = self.ensure_trailing_slash(self.path_join(dd_mm_yy, str(time.time())))

        if not self.path_exists(current_time):
            self.makedirs(current_time)
            console_logger.debug(f'{self.storage}: current_time: {current_time} created')

        return current_time

    def save_data_to_specific_folder(self, current_time_folder: str, data: dict) -> str:
        """
        :param current_time_folder: путь до папки с временем загрузки src
        :param data: словарь .json с болезнями и тп
        :return: путь к файлу json формата `%H_%M_%S`
        """

        h_m_s_ms = time.strftime("%H_%M_%S_") + str(time.time_ns() // 1_000_000)

        filename = h_m_s_ms + '.json'
        dst = self.path_join(current_time_folder, filename)

        self.save_json(dst, data)

        return dst

    def upload_large_file(self, src: str, dst: str, progress_callback: Union[Callable, None] = None) -> bool:
        """
        :param src: Файл, который загружаем src.mp4 (локальный)
        :param dst: Куда загружаем dst.mp4
        :param progress_callback: Обратный вызов для `ProgressPercentage`
        :return: Удалось или нет
        """

        if not os.path.exists(src):
            console_logger.error(f'{src} does not exists')
            return False

        mime = self._get_mime(src)

        # Конфигурация мультипарт-загрузки
        config = TransferConfig(
            multipart_threshold=1024 * 25,  # Порог, с которого начинается мультипарт-загрузка, в байтах
            max_concurrency=10,  # Количество параллельных потоков
            multipart_chunksize=1024 * 25,  # Размер каждой части, в байтах
            use_threads=True,
        )

        try:
            self.s3.upload_file(
                Filename=src,
                Bucket=self.bucket_name,
                Key=dst,
                Config=config,
                ExtraArgs={'ContentType': mime} if mime else {},
                Callback=ProgressPercentage(src, progress_callback),
            )
            console_logger.debug(f'Successfully uploaded {src} to {self.bucket_name}/{dst}')

            return True
        except Exception as e:
            get_traceback.critical(f'Error uploading file: {e}', print_full_exception=True)

            return False

    def get_download_link(self, filename: str, expiration=7 * 24 * 60 * 60):
        """
        :param filename: Путь до файла в S3 bucket
        :param expiration: Сколько действительна ссылка по-умолчанию 7 дней - это максимум
        :return:

        Возвращает загрузочную ссылку для файла (действует в течение 7 дней)
        """

        try:
            if self.storage == 's3':
                url = self.s3.generate_presigned_url('get_object',
                                                     Params={'Bucket': self.bucket_name,
                                                             'Key': filename,
                                                             },
                                                     ExpiresIn=expiration,
                                                     )
            else:
                url = filename
        except NoCredentialsError as e:
            get_traceback.error(f'{e}')
            return None

        return url

    def get_bucket_size(self) -> int:
        """
        :return: Размер бакета в байтах
        """

        total_size = 0
        continuation_token = None

        while True:
            # Запрашиваем список объектов в бакете
            if continuation_token:
                response = self.s3.list_objects_v2(Bucket=self.bucket_name, ContinuationToken=continuation_token)
            else:
                response = self.s3.list_objects_v2(Bucket=self.bucket_name)

            # Проверяем наличие объектов в ответе
            if 'Contents' in response:
                for obj in response['Contents']:
                    total_size += obj['Size']

            # Проверяем наличие следующей страницы результатов
            if response.get('IsTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break

        return total_size

    def is_bucket_under_limit(self, limit_gb: int = 10) -> bool:
        """
        :param limit_gb: Какой максимальный размер бакета в Гб
        :return: Превышен ли размер или нет
        """

        if os.getenv('BUCKET_LIMIT_GB'):
            limit_gb = int(os.getenv('BUCKET_LIMIT_GB'))
        else:
            limit_gb = limit_gb

        limit_bytes = limit_gb * (1024 ** 3)

        if self.get_bucket_size() > limit_bytes:
            return False
        else:
            return True

    # -----------------------------------------------------------------------------------------------------------------
    @staticmethod
    def win_to_linux_path(path: str) -> str:
        """
        :param path: Путь до папки/файла
        :return: Обновленный путь, формата S3 (Unix)
        """

        if "\\" in path:
            path = path.replace("\\", "/")

        return path

    def save_json(self, dst: str, data: dict) -> bool:
        """
        :param dst: Куда сохраняем файл
        :param data: Словарь, который сохраняем в json
        :return: Успешно ли сохранение
        """

        if self.storage == 'local':
            with open(dst, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        elif self.storage == 's3':
            self.s3.put_object(Bucket=self.bucket_name,
                               Body=json.dumps(data, ensure_ascii=False, indent=4),
                               Key=dst,
                               )

        return True

    def makedirs(self, path: str, exist_ok=True) -> bool:
        """
        :param path: Папка(-и), для S3 мы сами явно укажем, что это папка путем добавления обратного слеша.
        Путь должен быть обработан с использованием функционала `StorageApi.path_join`
        :param exist_ok: Установлен по умолчания для S3
        :return: Удалось ли создать директории

        Метод, реализующая функционал создания папок.
        """

        if self.storage == 'local':
            os.makedirs(path, exist_ok=exist_ok)
        elif self.storage == 's3':
            path = self.ensure_trailing_slash(path)

            self.s3.put_object(Bucket=self.bucket_name, Key=(path))

        return True

    def ensure_trailing_slash(self, folder: str) -> str:
        """
        :param folder: Путь до папки у которой нужно установить в конце слэш
        :return: Обработанный путь
        """

        if self.storage == 's3':
            if not folder.endswith('/'):
                folder += '/'

        return folder

    def path_join(self, *args) -> str:
        """
        :param args: Путь до объекта
        :return: Объединенный путь

        Реализует функционал `os.path.join`
        """

        if self.storage == 'local':
            return str(os.path.join(*args))
        else:
            return self.win_to_linux_path(str(os.path.join(*args)))

    def path_exists(self, path: str) -> bool:
        """
        :param path: Путь до папки/файла, существование которого надо проверить, не забудьте при использовании S3
        явно указать, что это папка, путем добавления обратного слеша.
        Путь должен быть обработан с использованием функционала `StorageApi.path_join`
        :return: Существует `path` или нет
        """

        if self.storage == 'local':
            return os.path.exists(path)
        else:
            try:
                # Попытка получения метаданных объекта
                self.s3.head_object(Bucket=self.bucket_name, Key=path)
            except ClientError as e:
                # Если объект не найден, возвращаем False
                if e.response['Error']['Code'] == '404':
                    return False
                # В случае других ошибок, возбуждаем исключение
                else:
                    raise
                # Если метаданные успешно получены, объект существует
            return True

    def rm_folder(self, folder: str) -> bool:
        """
        :param folder:
        :return: Папка удалена или нет
        """

        if self.storage == 'local':
            os.remove(folder)
        else:
            objects_to_delete = self.s3.list_objects(Bucket=self.bucket_name, Prefix=self.ensure_trailing_slash(folder))

            delete_keys = {'Objects': []}
            delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]

            self.s3.delete_objects(Bucket=self.bucket_name, Delete=delete_keys)

        return True

    def rm_file(self, files: list) -> bool:
        """
        :param files: Список файлов для удаления
        :return: Удалось ли удалить файл/файлы
        """

        if self.storage == 'local':
            for file in files:
                os.remove(file)
        else:
            forDeletion = [{'Key': self.win_to_linux_path(file)} for file in files]
            response = self.s3.delete_objects(Bucket=self.bucket_name, Delete={'Objects': forDeletion})
            if response.get('ResponseMetadata').get('HTTPStatusCode') != 200:
                return False

        return True

    def imwrite(self, path: str, image: np.ndarray) -> bool:
        """
        :param path: Куда сохраняем
        :param image: np.array изображение
        :return: Успешно ли сохранение
        """

        if self.storage == 'local':
            cv2.imwrite(path, image)
        elif self.storage == 's3':
            data_serial = cv2.imencode('.png', image)[1].tobytes()
            self.s3.put_object(Bucket=self.bucket_name, Body=data_serial, Key=path, ContentType='image/PNG')
        else:
            raise ValueError(f'Storage type {self.storage} not supported')

        return True

    @staticmethod
    def _get_mime(value: str) -> Union[str, None]:
        mt = mimetypes.guess_type(value)
        if mt:
            return mt[0]
        else:
            return None


if __name__ == '__main__':
    TEST_S3_FOLDER = 'test'


    def test_callback(progress: float):
        print(f'Test callback progress: {progress * 100}')


    Storage = StorageApi('s3')
    print(f'Размер бакета {round(Storage.get_bucket_size() / 1024 ** 2, 2)} Мб')
    print(f'Удалена ли data-test/: {Storage.rm_folder("data-test/")}')

    Storage.upload_large_file('../../DATA/videos/cars.mp4', f'{TEST_S3_FOLDER}/cars.mp4', test_callback)

    print(Storage.path_exists('abc/123/'))
    print(Storage.path_exists('test/Makefile'))

    imp = cv2.imread('../../DATA/videos/cars.jpg')
    Storage.imwrite(f'{TEST_S3_FOLDER}/np_image.png', imp)

    s3_user_folder = Storage.get_user_folder(1)
    user_f = Storage.create_user_folder(100)
    dd_mm_yy_f = Storage.create_dd_mm_yy_folder(user_f)
    current_time_f = Storage.create_current_time_folder(dd_mm_yy_f)
    json_file = Storage.save_data_to_specific_folder(current_time_f, {'test': [1, 2, 3]})
    print(f'user folder: {s3_user_folder}')
    print('user_f:', user_f)
    print('dd_mm_yy_f:', dd_mm_yy_f)
    print('current_time_f:', current_time_f)
    print('json_file:', json_file)
