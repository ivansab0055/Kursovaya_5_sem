import os
import pathlib
import sys
import tempfile
import time

from kallosus_packages.file import sort_by_date
from kallosus_packages.utils import platform

if hasattr(sys, '_MEIPASS'):
    meipass = sys._MEIPASS
    current_path = meipass
else:
    meipass = None
    current_path = str(pathlib.Path(__file__).parent.absolute())

_tmp_folder_name = 'KallosusTmp'

if platform in ['linux', 'macosx']:
    # `tempfile.gettempdir()` - файлы, удаляются при перезагрузке, поэтому используем способ ниже
    tmp_path = os.path.join('/', 'var', 'tmp', _tmp_folder_name)
else:  # platform in ['win', 'android']
    tmp_path = os.path.join(tempfile.gettempdir(), _tmp_folder_name)

if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)

tmp_video_path = os.path.join(tmp_path, 'videos')

if not os.path.exists(tmp_video_path):
    os.makedirs(tmp_video_path)

# Начинаем настройку логирования
log_dir = os.path.join(tmp_path, 'logs')

# папка не может быть удалена во время работы приложения
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

log_file_path = os.path.join(log_dir, f'logfile_{time.time()}.log')

_log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir)]
_log_files = sort_by_date(_log_files)
_files_num = len(_log_files)

if _files_num >= 3:
    # Здесь невозможно инициализировать ведение журнала, в противном случае возникает ошибка,
    # которая делает невозможным доступ к файлу
    for file in _log_files[3:]:
        _log_files.remove(file)
        try:
            os.remove(file)  # он находится в папке tmp, поэтому для удаления мы используем небезопасное удаление
        except PermissionError:  # если запущено другое приложение, блокирующее удаление логов
            pass

_log_files.append(log_file_path)
log_files = [os.path.join(log_dir, file) for file in _log_files]  # list with full path to log files

# Заканчиваем настройку логирования

# Путь до модели
model_folder = os.path.join(current_path, 'model')

# Путь до тестового .env
tests_env_file = os.path.join(current_path, 'tests', '.env')

# Путь до файлов среды
ENV_KALLOSUS_PROD = os.path.join(current_path, 'config', 'config_prod.py')
ENV_KALLOSUS_DEV = os.path.join(current_path, 'config', 'config_dev.py')
ENV_KALLOSUS_TEST = os.path.join(current_path, 'config', 'config_test.py')
