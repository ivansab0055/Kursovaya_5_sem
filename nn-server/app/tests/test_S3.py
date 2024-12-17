import os
from typing import NoReturn

import cv2
import numpy as np
from kallosus_packages.over_logging import Logger

from storage.S3 import StorageApi
from tests.BaseCase import BaseCase
from utils.loader import VideoImageLoader

console_logger = Logger(__file__)

Storage = StorageApi('s3')


class TestS3(BaseCase):
    def test_successfully_load_json_file(self) -> NoReturn:
        file = 'test-data/test.json'
        is_save = Storage.save_json(file, {'key': [1, 2, '3']})
        if_exists = Storage.path_exists(file)

        self.assertEqual(True, is_save)
        self.assertEqual(True, if_exists)

    def test_successfully_rm_json_file(self) -> NoReturn:
        file = 'test-data/test.json'
        is_rm = Storage.rm_file([file])
        if_exists = Storage.path_exists(file)

        self.assertEqual(True, is_rm)
        self.assertEqual(False, if_exists)

    def test_rm_not_exist_file(self) -> NoReturn:
        """
        :return:
        Если файла не существует, все равно вернет True
        """

        file = 'test-data/test.json'
        is_rm = Storage.rm_file([file])
        if_exists = Storage.path_exists(file)

        self.assertEqual(True, is_rm)
        self.assertEqual(False, if_exists)

    def test_successfully_load_large_file(self) -> NoReturn:
        src = self.test_video
        if src.startswith('https') or src.startswith('http'):
            src = VideoImageLoader().download(src)

        dst = 'test-data/test.mp4'
        is_upload = Storage.upload_large_file(src, dst)
        if_exists = Storage.path_exists(dst)

        self.assertEqual(True, is_upload)
        self.assertEqual(True, if_exists)

        is_rm = Storage.rm_file([dst])
        self.assertEqual(True, is_rm)

        if self.test_video != src:
            os.remove(src)
            console_logger.debug(f'{src} removed')

    def test_load_not_exist_video(self) -> NoReturn:
        src = 'fake'
        dst = 'test-data/test.mp4'
        is_upload = Storage.upload_large_file(src, dst)
        if_exists = Storage.path_exists(dst)

        self.assertEqual(False, is_upload)
        self.assertEqual(False, if_exists)

    def test_get_download_vid_link(self) -> NoReturn:
        url = Storage.get_download_link('test-videos/cars_test.mp4')
        cap = cv2.VideoCapture(url)

        # Проверяем, что видеопоток открыт
        self.assertEqual(True, cap.isOpened())
        ret, frame = cap.read()
        self.assertEqual(np.ndarray, type(frame))

    def test_get_download_nonexistent_vid_link(self) -> NoReturn:
        url = Storage.get_download_link('fake/cars_test.mp4')
        cap = cv2.VideoCapture(url)

        # Проверяем, что видеопоток открыт
        self.assertEqual(False, cap.isOpened())

    def test_get_long_download_video_link(self) -> NoReturn:
        url = Storage.get_download_link('test-videos/cars_test.mp4', 8 * 24 * 60 * 60)
        cap = cv2.VideoCapture(url)

        # Проверяем, что видеопоток открыт
        self.assertEqual(False, cap.isOpened())

    def test_rm_folder(self) -> NoReturn:
        path = Storage.create_user_folder(1)

        is_exists = Storage.path_exists(path)
        is_rm = Storage.rm_folder(path)

        self.assertEqual(True, is_exists)
        self.assertEqual(True, is_rm)
