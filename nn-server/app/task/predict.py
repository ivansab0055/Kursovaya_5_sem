try:
    from .preload_libs import *
except ImportError:
    from preload_libs import *


class JobTracker:
    def __init__(self, job: Job, num_files: int):
        """
        :param job: `rq.Job`
        :param num_files: Количество обрабатываемых файлов
        """

        self.job = job
        self.num_files = num_files
        self._start_time = time.time()  # Запоминаем время начала задачи

    def set_num_files(self, num_files: int) -> NoReturn:
        self.num_files = num_files

    def update_progress(self, progress: float) -> NoReturn:
        """
        Обновляет meta данные прогресса, а также eta, которая от него зависит
        :param progress: Текущий прогресс обработки запроса
        :return: `NoReturn`
        """

        self.set_meta(progress=progress)
        self.calc_eta(progress=progress)

    def calc_eta(self, progress: float) -> NoReturn:
        """
        Функция рассчитывает оставшееся время обработки
        :param progress: Текущий прогресс выполнения задачи
        :return: `NoReturn`
        """

        # Рассчитываем оставшееся время
        elapsed_time = time.time() - self._start_time  # Время, прошедшее с начала обработки
        if progress > 0:  # Избегаем деления на ноль
            estimated_total_time = elapsed_time / (progress / 100)  # Оценка общего времени
            eta = int(estimated_total_time - elapsed_time)  # Оставшееся время
            console_logger.debug(f'eta={eta}')
            self.set_meta(eta=eta)  # Обновляем метаданные с ETA

    def set_meta(self, **kwargs) -> NoReturn:
        """
        :param kwargs: Параметры для обновления meta в job
        Возможные параметры: progress, eta, video_no, videos_no, stage

        :return: `NoReturn`
        """

        params = ['progress', 'eta', 'video_no', 'videos_no', 'stage']

        # У нас нет задачи во время прямого тестирования predict.py
        if os.getenv('TEST_PREDICT') == '1':
            return

        if self.job is not None:
            for key in kwargs:
                if key in params:
                    self.job.meta[key] = kwargs[key]
                else:
                    raise ValueError(f'Incorrect parameters, must be one of {params}')

            self.job.save_meta()

    def finish_task(self,
                    output_files: Union[str, list, None] = None,
                    is_files_upload: Union[dict, None] = None,
                    error: bool = False,
                    ) -> NoReturn:
        """
        :param output_files: путь к файлам json
        :param is_files_upload: `dict` объект, показывающей, сохранены ли успешно все файлы, если хоть что-то False,
        то может быть ошибка:
        {'test-videos/cars_test.mp4': [
        {'video': True}, - Загружено ли выходное видео в S3
        {'image_1': True}, {'image_2': True}, {'image_3': True}, {'image_4': True}, - Загружены ли изображения в S3
        {'res-file': True} - Загружен ли json в S3
        ]
        }
        :param error: если задание завершено с ошибкой
        :return: `NoReturn`

        Прогресс автоматически устанавливается в 100
        """

        if os.getenv('TEST_PREDICT') == '1':
            console_logger.warning('`TEST_PREDICT` enabled')
            return

        if isinstance(output_files, str):
            output_files = [output_files]

        if output_files is None:
            output_files = []

        self.update_progress(100)

        with app.app_context():
            task = Task.find_by_id(self.job.meta['task_id'])

            try:
                task.finish_task(output_files, is_files_upload, error)
            except AttributeError as e:
                """
                - May be when Task table deleted in tests
                - When using tests with RQ, we cant get table
                """

                get_traceback.error(f'{e}')

    def load_vid_callback(self, progress: float, init_progress: int = 0) -> NoReturn:
        """
        :param progress: Прогресс, получаемый при вызове callback класса `ProgressPercentage`
        :param init_progress: Начальное значение прогресса
        :return: `NoReturn`

        Callback для загрузчика видео, чтобы обновлять прогресс
        """

        progress = PROGRESS_NN_PERCENT / self.num_files + progress * PROGRESS_LOAD_DST_PERCENT / self.num_files + init_progress  # 5 * 15 + 80
        self.update_progress(progress)
        console_logger.debug(f'[LOAD VIDEO]: progress: {progress}')


class VideoLoader:
    """Класс для загрузки видео с различных источников."""

    @staticmethod
    def read_video(path: str) -> tuple[cv2.VideoCapture, bool, ndarray | ndarray | Any, int, float, int, int]:
        """
        Чтение видеофайла
        :param path: Путь до обрабатываемого видео
        :return: Объект открытого видео, количество фреймов, прочитанный 1-й фрэйм, текущее изображение, fps, ширину видео, высоту видео
        """

        vidcap = cv2.VideoCapture(path)
        frame_read, image = vidcap.read()
        height, width, channels = image.shape
        length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = vidcap.get(cv2.CAP_PROP_FPS)  # В некоторых форматах может быть 29.97, 23.976 и т.д.
        h = int(vidcap.get(cv2.CAP_PROP_FOURCC))
        codec = chr(h & 0xff) + chr((h >> 8) & 0xff) + chr((h >> 16) & 0xff) + chr((h >> 24) & 0xff)
        console_logger.debug(f'Video frames: {length}; fps: {fps}; size: {width, height}; codec: {codec}')

        return vidcap, frame_read, image, length, fps, width, height


class VideoProcessor:
    """Класс для обработки видео и выполнения предсказаний."""

    def __init__(self,
                 files: List[str],
                 current_time_folders: List[str],
                 is_save_output: bool = True,
                 is_remove: bool = False,
                 sleep: int = 0,
                 ):
        """
        :param files: Путь до видео, в котором будем искать болезни
        :param current_time_folders: Путь (url) к папкам пользователя, где лежит текущий файл src и будет лежать dst
        :param is_save_output: Сохранять ли видео с bbox и label болезней (если необходимо сохранить в облако, то сначала видео сохраняется локально, а затем загружается)
        :param is_remove: Удалять ли файл, по которому делали предсказание после предсказания
        :param sleep: Timeout (требуется только для теста)
        :return: `NoReturn`

        Используем для распознавания одного видео
        :Тренировка в Collab: https://colab.research.google.com/github/Rishit-dagli/Design-and-Code-2020/blob/master/cats-vs-dogs.ipynb

        data.json
        ```
        {
            "detected": [
                "truck",
                "car"
            ],
            "source_of_infection": [
                ["C:\\Users\\pikro\\Kallosus\\NN server\\DATA\\output\\1\\15_06_24\\1718448777.6166196\\2_2_2_2_2_7_2_2_2_2_1718449067.6433728.png", 0.0],
               ...2-8...
                ,["C:\\Users\\pikro\\Kallosus\\NN server\\DATA\\output\\1\\15_06_24\\1718448777.6166196\\2_2_2_2_2_2_2_2_7_2_1718449067.9723752.png", 10.1]
            ],
            "num_detected": {
                "car": 1904,
                "truck": 43
            },
            "src": "https://downloader.disk.yandex.ru/disk/6d9e64e4ecd0511461c58cce5629c9905bbe7fffea723d53eacab41c6b4d842a/666dab6a/D8imih97WPavWgl8sJjnJNdJITA73Za1vuyl69h9XhzwtSoGS6t6HMlWb0KK1WRorD5Ek9MXhqvm2RKSlq2Fgg%3D%3D?uid=0&filename=cars.mp4&disposition=attachment&hash=KUQT1FlKV9L/1kZ%2BIMkY3s6AOjfsdCWiKeB8R3tfNfWfp2PtQWAosG/ljurs2k5nq/J6bpmRyOJonT3VoXnDag%3D%3D%3A&limit=0&content_type=video%2Fmp4&owner_uid=338375491&fsize=2618301&hid=3677194f6b9c093d7cd8a9e5fcee7247&media_type=video&tknv=v2",
            "dst": "C:\\Users\\pikro\\Kallosus\\NN server\\DATA\\output\\1\\15_06_24\\1718448777.6166196\\0_dst.avi"
        }
        ```
        """
        self.len_files = len(files)

        self.job = get_current_job()
        self.job_tracker = JobTracker(self.job, self.len_files)

        self.files = files
        self.current_time_folders = current_time_folders
        self.is_save_output = is_save_output
        self.is_remove = is_remove
        self.sleep = sleep
        self.progress = 0  # Текущий прогресс
        self._progress = 0  # Накапливает прогресс

        self.res_json_files = []  # Список файлов json
        self.is_files_upload = {}  # Сохраняем сюда информацию о том, загружены ли все необходимые файлы
        self.data = {}  # Данные для хранения предсказаний
        self.max_detected = {}  # Хранит ключ - количество определенных объектов, в значении кол-во определенных классов, само изображение `np`, классы, time code

        self.storage = Storage.get_storage()

        if self.sleep > 0:
            console_logger.debug(
                f'It looks like you are in development mode, each frame will be processed with a delay of {self.sleep} seconds')

        console_logger.debug(f'Starting task, UNIT_TEST: {os.getenv("UNIT_TEST")}')
        console_logger.debug(f'DATA_STORAGE: {os.getenv("DATA_STORAGE")}, Storage: {self.storage}')

    def process_videos(self) -> NoReturn:
        """
        Обрабатывает список видео с предсказаниями.

        :return `NoReturn`
        """

        if os.getenv('TEST_PREDICT') != '1':
            with app.app_context():
                task = Task.find_by_id(self.job.meta['task_id'])
                task.set_status('run')

        try:
            self.job_tracker.update_progress(0)

            # Обрабатываем видео по 1
            for i, path in enumerate(self.files):
                self.job_tracker.set_meta(video_no=i + 1, videos_no=self.len_files, stage='video-processing')

                self.process_single_video(current_vid_no=i,
                                          path=path,
                                          )

                self._progress += self.progress

            self.job_tracker.finish_task(output_files=self.res_json_files, is_files_upload=self.is_files_upload)
            console_logger.debug(f'Is all files upload to S3 {self.is_files_upload}')
            console_logger.debug('Task completed')
        except FileNotFoundError as e:
            get_traceback.error(f'{e} - Perhaps you need to run `CreateFoldersApi` first')
            self.job_tracker.finish_task(error=True)
        except InternalServerError as e:
            get_traceback.critical(f'{e}', print_full_exception=True)
            self.job_tracker.finish_task(error=True)

    def process_single_video(self,
                             current_vid_no: int,
                             path: str,
                             ) -> NoReturn:
        """
        Обрабатывает одно видео, делая предсказания и сохраняя результаты.
        :param current_vid_no: Номер текущего видео начиная с 0
        :param path: Расположение видео (путь/url)

        :return `NoReturn`
        """

        self.is_files_upload[path] = []

        # Чтение видео
        url = self.get_video_url(path)
        console_logger.debug(f'Process: {url}')
        vidcap, frame_read, image, length, fps, width, height = VideoLoader.read_video(url)

        # При сохранении локально преобразовывать пути к S3 типу не нужно
        if self.storage == 'local':
            current_time_folder = self.current_time_folders[current_vid_no]
            dst_folder = current_time_folder
        else:
            current_time_folder = StorageApi.win_to_linux_path(self.current_time_folders[current_vid_no])
            dst_folder = tmp_video_path

        console_logger.debug(f'Current time_folder: {current_time_folder}, dst_folder: {dst_folder}')

        # Инициализация сохранения выходного видео
        if self.is_save_output:
            dst_vid_name = f'{current_vid_no}_dst.mp4'
            dst = os.path.join(dst_folder, dst_vid_name)
            # Установите функцию записи выходного видео с помощью кодека
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            out = cv2.VideoWriter(dst, fourcc, fps, (width, height))
        else:
            dst = ''
            out = ''

        # Инициализируем данные для хранения предсказаний
        self.data = self.initialize_data(url, dst)

        # Начинаем поиск болезней на видео
        console_logger.debug(f'Start, write to dst={dst}...')
        self.detect_frames(vidcap, frame_read, image, length, fps, out)

        # Сохраняем обработанное видео
        if self.is_save_output:
            out.release()
            console_logger.debug('Resources released')

            self.upload_video(dst, current_time_folder, path)
            self.upload_images(current_time_folder, path)

        # Удаляем обрабатываемое видео
        if self.is_remove:
            os.remove(path)
            console_logger.debug(f'{path} removed')

        self.data['detected'] = list(self.data['detected'])  # Преобразуем в список, иначе не сможем сохранить в бд

        # Загружаем json файл с информацией о видео
        self.upload_info(current_time_folder, path)

    def get_video_url(self, path: str) -> str:
        """
        Получить ссылку на видео.

        :param path: Путь до видео

        :return реальный url/путь до видео
        """

        if self.storage == 's3':
            return Storage.get_download_link(path)
        elif path.startswith('http://') or path.startswith('https://'):
            return VideoLoader.get_video_link(path)

        return path

    @staticmethod
    def initialize_data(src: str, dst: str) -> dict:
        """
        Инициализация структуры данных для результатов.

        :param src: Расположение видео
        :param dst: Обработанное видео

        : return `dict`
        """

        data = {
            'detected': set(),  # Множество всех определенных классов
            'source_of_infection': [],  # Очаг заражения - путь до файлов с макс. кол-ом определенных классов
            'num_detected': {},  # Количество определенных элементов каждого класса
            'src': src,
            'dst': dst,
        }

        return data

    def detect_frames(self,
                      vidcap: cv2.VideoCapture,
                      frame_read: ndarray | ndarray | Any,
                      image: ndarray,
                      length: int,
                      fps: float,
                      out: Union[cv2.VideoWriter, None],
                      ) -> NoReturn:
        """Обработка фреймов видео и выполнение предсказаний.
        :param vidcap: Объект cv2.VideoCapture для захвата видео, позволяющий считывать кадры видеофайла.
        :param frame_read: Текущий считанный кадр (первый кадр), представляющий собой массив данных изображения.
        :param image: Массив данных изображения для первого считанного кадра.
        :param length: Общее количество кадров в видеофайле.
        :param fps: Частота кадров (кадры в секунду) в видеофайле, выраженная в виде плавающего числа.
        :param out: Объект cv2.VideoWriter для записи обработанных кадров в новый видеофайл.

        :return: `NoReturn`
        """

        count = 0  # Текущий кадр

        # Перебираем кадры и передаем каждый для прогнозирования
        while frame_read:
            # Выполняем обнаружение объекта
            output_file, _, labels = PREDICTOR.predict(image)

            if labels:
                self.data['detected'].update(labels)

                # Считаем сколько каждых классов обнаружено
                for c in labels:
                    self.data['num_detected'][c] = self.data['num_detected'].get(c, 0) + 1

                if (count + 1) % 2 != 0:  # Каждый нечетный кадр проверяем (через 1)
                    self.update_max_detected(labels, output_file, count / fps)

                console_logger.debug(
                    f'№{count + 1}/{length}: Target classes: {labels}, progress: {round(self.progress, 2)}%')

            # Записываем кадр с предсказаниями в видео
            if self.is_save_output:
                out.write(output_file)

            # Читаем следующий кадр
            frame_read, image = vidcap.read()
            count += 1

            progress = (count / length) * PROGRESS_NN_PERCENT / self.len_files + self._progress
            self.job_tracker.update_progress(progress)

            if self.sleep > 0:
                time.sleep(self.sleep)

        self.progress = int(self.progress)  # Делаем 80% для обработки NN
        console_logger.debug(f'Кадров прочитано: {count}, progress={self.progress}')

    def update_max_detected(self, labels: list, output_file: ndarray, time_code: float):
        """Обновление словаря максимальных предсказаний.
        :params labels:
        :params output_file:
        :params time_code:
        """

        n_max = 10
        keys = self.max_detected.keys()

        if len(keys) < n_max:
            self.max_detected[len(keys)] = (len(labels), output_file, labels, time_code)
        else:
            # Заменяем минимальное кол-во определенных объектов на новое, большее
            min_key = min(keys, key=lambda k: self.max_detected[k][0])

            if len(labels) > self.max_detected[min_key][0]:
                self.max_detected[min_key] = (len(labels), output_file, labels, time_code)

    def upload_video(self, dst: str, current_time_folder: str, path: str) -> NoReturn:
        """
        Загрузка обработанного видео в хранилище.
        :param dst: Локальный файл, который загружаем в облако
        :param current_time_folder: Папка, в которую сохраняем выходное видео
        :param path: Путь до обрабатываемого видео, может быть как локальным, так и облачным

        :return `NoReturn`
        """

        self.job_tracker.set_meta(stage='video-loading')

        if self.storage == 's3':
            remote_dst = Storage.path_join(current_time_folder, os.path.basename(dst))
            self.data['dst'] = remote_dst  # Записываем в dst путь до s3

            console_logger.debug(f'Starting upload {dst} to s3://{remote_dst}')
            is_dst_upload = Storage.upload_large_file(src=dst,
                                                      dst=remote_dst,
                                                      progress_callback=lambda
                                                          pr: self.job_tracker.load_vid_callback(pr, self._progress),
                                                      )
            self.is_files_upload[path].append({'video': is_dst_upload})
            os.remove(dst)
            console_logger.debug(f'Resources uploaded {is_dst_upload}, {dst} removed')

    def upload_images(self, current_time_folder: str, path: str) -> NoReturn:
        """
        Загрузка изображений в хранилище.
        :param current_time_folder: Папка, в которую сохраняем выходное видео
        :param path: Путь до обрабатываемого видео, может быть как локальным, так и облачным

        :return: `NoReturn`
        """

        self.job_tracker.set_meta(stage='images-loading')
        len_images = len(self.max_detected.keys())

        # Сохраняем изображения в папке пользователя в конкретный день (user_id, dd_mm_yy)
        for i, (key, value) in enumerate(self.max_detected.items()):
            img_path = Storage.path_join(current_time_folder, f"max_{i}_{time.time()}.png")
            is_file_uploaded = Storage.imwrite(img_path, value[1])
            self.data['source_of_infection'].append([img_path, value[3]])
            self.is_files_upload[path].append({f'image_{i + 1}': is_file_uploaded})

            # Рассчитываем прогресс загрузки: (1/10) * 5 + 95
            progress = (PROGRESS_LOAD_DST_PERCENT + PROGRESS_NN_PERCENT) / self.len_files + (
                    (i + 1) / len_images) * PROGRESS_LOAD_IMAGES_PERCENT / self.len_files + self._progress
            console_logger.debug(f'№{i + 1}/{len_images}: progress: {progress}')
            self.job_tracker.update_progress(progress)

            console_logger.debug(f'{img_path} write, progress={progress}')

    def upload_info(self, current_time_folder: str, path: str) -> NoReturn:
        """
        Загрузка информации об обработанном файле на сервер в json формате.
        :param current_time_folder: Папка, в которую сохраняем выходное видео
        :param path: Путь до обрабатываемого видео, может быть как локальным, так и облачным

        :return: `NoReturn`
        """

        self.job_tracker.set_meta(stage='info-loading')

        if app.config['DEBUG'] and Storage.get_storage() == 'local':
            console_logger.warning(f'You in debug docker mode, files will be saved locally')
            os.makedirs(current_time_folder, exist_ok=True)

        file = Storage.save_data_to_specific_folder(current_time_folder=current_time_folder, data=self.data)
        self.is_files_upload[path].append({f'res-file': True if file else False})
        self.res_json_files.append(file)


# Api для работы с очередью
def predict_on_video(files: list,
                     current_time_folders: list,
                     save_output: bool = True,
                     is_remove=False,
                     sleep: int = 0,
                     *args,
                     **kwargs,
                     ) -> NoReturn:
    """
    :param files: Путь до видео, в котором будем искать болезни
    :param current_time_folders: Путь (url) к папкам пользователя, где лежит текущий файл src и будет лежать dst
    :param save_output: Сохранять ли видео с bbox и label болезней (если необходимо сохранить в облако, то сначала видео сохраняется локально, а затем загружается)
    :param is_remove: Удалять ли файл, по которому делали предсказание после предсказания
    :param sleep: Timeout (требуется только для теста)
    :return: `NoReturn`
    """

    vid_processor = VideoProcessor(files, current_time_folders, save_output, is_remove, sleep)
    vid_processor.process_videos()


if __name__ == '__main__':
    os.environ['TEST_PREDICT'] = '1'

    how_test = input('Тестируем локально - 1, стримим Яндекс - 2, стримим Selectel - 3: ')

    if how_test == '1':
        print('Используем локальный файл')
        Storage.storage = 'local'
        Storage._auth()
        predict_on_video(['..\\..\\DATA\\videos\\apple_rust.mp4'],
                         ['..\\..\\DATA\\output\\test'],
                         )
    elif how_test == '2':
        print('Используем Яндекс файл')
        predict_on_video(['https://disk.yandex.ru/i/DmkPOSwcHLXqww'],
                         ['..\\..\\DATA\\output\\test'],
                         )
    elif how_test == '3':
        print('Используем Selectel файл')
        Storage.storage = 's3'
        Storage._auth()
        predict_on_video(['test-videos/cars_test.mp4'],
                         ['output/test'],
                         )

"""
В Docker:
cd task

from predict import predict_on_video

Storage.storage = 's3'
Storage._auth()
predict_on_video(['test-videos/cars_test.mp4'],
                 ['output/test'],
                 )
"""
