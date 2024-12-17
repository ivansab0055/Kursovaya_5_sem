import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import ultralytics
from PIL import Image
from ultralytics import YOLO

try:
    matplotlib.use('TkAgg')
except ImportError:
    pass

from typing import Union, NoReturn
import os
import time

import env_register  # noqa
from path_definitions import model_folder
from kallosus_packages.over_logging import Logger, GetTraceback
from torch import __version__ as torch_ver
from torchvision import __version__ as torch_vision_ver
import gdown

console_logger = Logger(__file__)
get_traceback = GetTraceback(__file__)

ultralytics.checks()

console_logger.info(f'ultralytics: {ultralytics.__version__}; torch: {torch_ver}; torchvision: {torch_vision_ver}')


class DiseasesDetection:
    def __init__(self, save: bool = False, threshold: float = 0.5, line_width: int = 2):
        """
        :param save: Флаг, сохранять ли выход
        :param threshold: Порог срабатывания
        :param line_width: Толщина линии обводки
        """

        # Определяем основные объекта переменные класса
        # Путь до модели
        self.__model_path = os.path.join(model_folder, 'pd_yolov9e.pt')

        if not os.path.exists(self.__model_path):
            try:
                src_model_url = 'https://drive.google.com/file/d/14F-5czkxv2C1x-UPgoDyFYk6ycx-B7i6/view?usp=sharing'
                console_logger.debug(f'Downloading model from {src_model_url} to {self.__model_path}')
                gdown.download(src_model_url,
                               output=self.__model_path,
                               fuzzy=True,
                               )
            except Exception as e:
                get_traceback.critical(f'{self.__model_path} does not exists, when downloading model occur error: {e}',
                                       print_full_exception=True)
                raise FileNotFoundError(f'{self.__model_path} does not exists, when downloading model occur error: {e}')

        # Названия классов
        self.__names_path = os.path.join(model_folder, 'classes.names')

        if not os.path.exists(self.__names_path):
            raise FileNotFoundError(f'{self.__names_path} does not exists')

        self._save = save
        self._threshold = threshold
        self._line_width = line_width

        self.model = None
        self.class_names_dict = {}

    def get_model(self) -> str:
        """
        :return: Путь до модели
        """

        return self.__model_path

    def load(self) -> NoReturn:
        """
        :return: `NoReturn`
        Загружаем модель
        """

        console_logger.debug('Loading model...')

        # Загрузите сохраненную модель и создайте функцию обнаружения
        if os.path.exists(self.__model_path):
            self.model = YOLO(self.__model_path)
        else:
            raise FileNotFoundError(f'{self.__model_path} does not exists')
        console_logger.debug('Model loaded')

        # Открываем файл и считываем его содержимое
        with open(self.__names_path, 'r') as file:
            lines = file.readlines()

        # Преобразуем содержимое файла в словарь
        for idx, line in enumerate(lines):
            self.class_names_dict[idx] = line.strip()

        console_logger.debug(f'Названия классов загружены: {self.class_names_dict}')

    @staticmethod
    def load_image_into_numpy_array(path: str) -> np.ndarray:
        img = Image.open(path)
        img_arr = np.array(img)

        return img_arr

    def predict(self, image: Union[str, np.ndarray], show: bool = False) -> tuple[np.ndarray, list[int], list[str]]:
        """
        :param image: Путь до изображения
        :param show: Показывать ли изображение с bbox
        :return: картинка с bbox и обнаруженные на ней болезни списком в виде индексов и меток
        """

        if not self.model:
            console_logger.info('`self.model` не определена, загружаем модель')
            self.load()

        if isinstance(image, str):
            image_np = self.load_image_into_numpy_array(image)
        else:
            image_np = image

        detections = self.model.predict(image_np, conf=self._threshold)[0]
        class_indices = []
        class_labels = []
        text_thickness = 2
        font_scale = 1

        # Проходимся по detections
        for data in detections.boxes.data.tolist():
            confidence = data[4]

            # Отфильтруем слабые обнаружения
            if float(confidence) < self._threshold:
                continue

            # Рисуем рамку
            xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
            conf = round(data[4], 2)
            class_id = int(data[5])
            class_label = self.class_names_dict[class_id]
            class_indices.append(class_id)
            class_labels.append(class_label)
            text = f"{class_label}, {conf}%"

            # Нарисовать текст над рамкой
            cv2.rectangle(image_np, (xmin, ymin), (xmax, ymax), (0, 255, 0), self._line_width)
            cv2.putText(image_np, text, (xmin + 5, ymin - 15), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0),
                        text_thickness)

        if show:
            plt.figure()
            plt.imshow(image_np)
            console_logger.debug('Done')
            plt.show()

        if self._save:
            path = f'{"__".join(list(map(str, class_indices)))}__{time.time()}.jpg'
            cv2.imwrite(path, image_np)

        return image_np, class_indices, class_labels


PREDICTOR = DiseasesDetection()

if __name__ == '__main__':
    # image = np.random.randint(0, 256, (640, 640, 3), dtype=np.uint8)
    img, indices, labels = PREDICTOR.predict('../../DATA/videos/apple_rust.jpeg', show=True)
    print(labels)
