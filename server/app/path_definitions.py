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
    # `tempfile.gettempdir()` - файлы, удаляются при перезагрузке, поэтому используем папку var/tmp
    tmp_path = os.path.join('/', 'var', 'tmp', _tmp_folder_name)
else:  # platform in ['win', 'android']
    tmp_path = os.path.join(tempfile.gettempdir(), _tmp_folder_name)

if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)

log_dir = os.path.join(tmp_path, 'logs')

# папка не может быть удалена во время работы приложения
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

log_file_path = os.path.join(log_dir, f'logfile_{time.time()}.log')

_log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir)]
_log_files = sort_by_date(_log_files)
_files_num = len(_log_files)

if _files_num >= 3:
    # Здесь невозможно инициализировать ведение журнала, в противном случае возникает ошибка, которая делает невозможным
    # доступ к файлу логирования
    for file in _log_files[3:]:
        _log_files.remove(file)
        try:
            os.remove(file)  # он находится в папке tmp, поэтому для удаления мы используем небезопасное удаление
        except PermissionError:  # если запущено другое приложение, не дающее доступ к файлу логирования
            pass

_log_files.append(log_file_path)
log_files = [os.path.join(log_dir, file) for file in _log_files]  # list with full path to log files

# Путь до файлов среды
ENV_KALLOSUS_PROD = os.path.join(current_path, 'config', 'config_prod.py')
ENV_KALLOSUS_DEV = os.path.join(current_path, 'config', 'config_dev.py')
ENV_KALLOSUS_TEST = os.path.join(current_path, 'config', 'config_test.py')
