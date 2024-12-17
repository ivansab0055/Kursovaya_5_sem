import os
import time
from typing import Any, List, NoReturn, Union

import cv2
import env_register  # noqa
from app import KallosusNNApplication
from database.models import Task
from dotenv import load_dotenv
from kallosus_packages.over_logging import GetTraceback, Logger
from numpy import ndarray
from path_definitions import tests_env_file, tmp_video_path
from resources.errors import InternalServerError
from rq import get_current_job
from rq.job import Job
from storage.S3 import StorageApi
from utils.loader import VideoImageLoader

from task.disiases_detection import PREDICTOR

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)

VideoLoader = VideoImageLoader()
console_logger.debug(f'FileDownloader initialized')

load_dotenv(tests_env_file)
console_logger.debug(f'env loaded')

app = KallosusNNApplication().create_app()
PREDICTOR.load()

Storage = StorageApi()
console_logger.info(f'StorageApi loaded')

PROGRESS_NN_PERCENT = 80  # Сколько процентов progress bar занимает обработка видео нейронной сетью
PROGRESS_LOAD_DST_PERCENT = 15  # Сколько процентов progress bar занимает загрузка видео
PROGRESS_LOAD_IMAGES_PERCENT = 5  # Сколько процентов progress bar занимает загрузка изображений
