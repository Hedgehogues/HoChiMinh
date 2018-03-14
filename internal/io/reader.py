import cv2
import pandas as pd


class ImageFromPDFReader:
    """
        Ридер, умеющий работать с pdf-конвертором.
        Постранично читает изображения, подготовленные pdf-конвертором.
    """

    """
        converter: конвертер, у которого есть метод convert_all() для выполнения конвертации всех pdf в изображения и
                   метод next_image(), возвращающий следующее изображение
    """
    def __init__(self, converter):
        self.converter = converter
        self.converter.convert_all()

    """
        Метод возвращает следующее изображение из пула
    """
    def read(self):
        return cv2.imread(self.converter.next_path_to_image(), cv2.IMREAD_GRAYSCALE)


class ImageReader:
    def __init__(self, path):
        self.path = path

    def read(self):
        return cv2.imread(self.path, cv2.IMREAD_GRAYSCALE)


class XlsxReader:
    """
        Извлечение данных из файлов в pandas.DataFrame
    """

    """
        Конструктор

        paths: список путей к файлам

        В случае, если передан не список или один из путей не является строкой, будет сгенерировано исключение
        ValueError
    """
    def __init__(self, paths):
        if type(paths) != list:
            raise ValueError('Unexpected type of paths')
        for path in paths:
            if type(path) != str:
                raise ValueError('Path is not string')
        self.paths = paths
        self.cur_index = 0

    """
        Прочтение текущего файла и запись данных в pandas.DataFrame. Функция для текущего файла может быть вызвана
        сколько угодно раз, пока не вызвана функция next_file()

        Если все файлы были обработаны, то будет сгенерировано исключение EOFError
    """
    def read(self):
        if self.is_finish():
            raise EOFError('All files has processed')
        return pd.read_excel(self.paths[self.cur_index])

    """
        Взять для чтения следующий файл

        Если все файлы были прочитаны, то будет сгенерировано исключение EOFError
    """
    def next(self):
        if self.is_finish():
            return
        self.cur_index += 1

    def is_finish(self):
        return False if self.cur_index < len(self.paths) else True
