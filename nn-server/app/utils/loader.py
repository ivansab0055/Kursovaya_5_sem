import datetime
import os
import urllib.parse as urllib_parse

import requests

from path_definitions import tmp_path

available_formats = ['.jpg', 'jpeg', '.png', '.mp4', '.avi']
disk_domains = ['disk.yandex.ru', 'selstorage.ru']


class VideoImageLoader:
    """
    Класс загрузчик, позволяет загружать файлы из интернета (облака)
    """

    def get_video_link(self, url: str) -> str:
        """
        param url: URL
        Selectel: https://15a4a98a-e257-4b1f-af84-83d732daeb14.selstorage.ru/test-videos/cars.mp4
        :return: Обработанная ссылка, позволяющая скачивать/стримить файл
        """

        if disk_domains[0] in url:  # Если загрузка с диска
            valid_url = self._yandex_disk_link(url)
        elif any(url.endswith(i) for i in available_formats):  # Если просто файл
            valid_url = url
        else:
            raise AttributeError(
                f'Cant download this file, available formats are {available_formats} or available disk domains: {disk_domains}')

        return valid_url

    @staticmethod
    def _yandex_disk_link(public_key: str) -> str:
        """
        :param public_key: его URL-адрес похож на https://disk.yandex.ru/d/cp0jEVVHlYAjxA
        :return: ссылка для скачивания
        """

        yandex_download_api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'

        # Получение загрузочной ссылки
        final_url = yandex_download_api + urllib_parse.urlencode(dict(public_key=public_key))
        response = requests.get(final_url)

        # return 'href' <url>, 'method': 'GET', 'templated'
        download_url = response.json()['href']

        return download_url

    def download(self, url: str) -> str:
        """
        :param url: URL
        :return: путь до загруженного файла
        """

        download_url = self.get_video_link(url)
        path = os.path.join(tmp_path, datetime.datetime.now().strftime('%Y_%m_%d_%H-%M-%S.%f') + '.jpg')

        response = requests.get(download_url, stream=True)
        with open(path, 'wb') as output:
            output.write(response.content)

        return path


if __name__ == '__main__':
    import cv2

    video_url = "https://disk.yandex.ru/i/EwFWUZUbzomEbQ"
    video_url = VideoImageLoader().get_video_link(video_url)
    print(video_url)

    # Открываем видеопоток
    cap = cv2.VideoCapture(video_url)

    # Проверяем, что видеопоток открыт
    if not cap.isOpened():
        print("Ошибка открытия видеопотока")
        exit()

    # Чтение и обработка кадров покадрово
    while True:
        # Читаем кадр из видеопотока
        ret, frame = cap.read()
        if not ret:
            print("Конец видео")
            break

        # Показываем обработанный кадр
        cv2.imshow('Processed Frame', frame)

        # Проверяем, была ли нажата клавиша "q" для выхода из цикла
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Освобождаем ресурсы
    cap.release()
    cv2.destroyAllWindows()
