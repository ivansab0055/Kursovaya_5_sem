import os

from config import DEBUG
from path_definitions import log_file_path

if not os.environ.get('LOG_PATH'):
    os.environ['LOG_PATH'] = log_file_path

os.environ['DEBUG'] = str(DEBUG)

if __name__ == '__main__':
    print(log_file_path)
