# Требуется для пакета kollosus https://gitlab.com/kallosus/py_packages/-/blob/master/kallosus_packages/over_logging/__init__.py?ref_type=heads
import os

from config import DEBUG
from path_definitions import log_file_path

if not os.environ.get('LOG_PATH'):
    os.environ['LOG_PATH'] = log_file_path

if not os.getenv('DATA_STORAGE'):
    os.environ['DATA_STORAGE'] = 's3'

os.environ['DEBUG'] = str(DEBUG)
