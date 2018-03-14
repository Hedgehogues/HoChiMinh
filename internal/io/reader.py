import cv2


class ImageFromPDFReader:
    """
        Постраничное читение изображений, подготовленных pdf-конвертором.
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


class DocumentFromPDFReader:
    """
        Подокументное читение изображений, подготовленных pdf-конвертором
    """

    """
        converter: конвертер, у которого есть метод convert_all() для выполнения конвертации всех pdf в изображения и
                   метод next_image(), возвращающий следующее изображение
    """
    def __init__(self, converter):
        self.converter = converter
        self.converter.convert_all()

        self.paths = []
        self.last_path = 0

    """
        Метод возвращает следующее изображение из пула
    """
    def read(self):
        if len(self.paths) == self.last_path:
            self.paths = self.converter.next_paths_to_documents()
            self.last_path = 0
        else:
            self.last_path += 1

        return cv2.imread(self.paths[self.last_path], cv2.IMREAD_GRAYSCALE)


class ImageReader:
    def __init__(self, path):
        self.path = path

    def read(self):
        return cv2.imread(self.path, cv2.IMREAD_GRAYSCALE)
