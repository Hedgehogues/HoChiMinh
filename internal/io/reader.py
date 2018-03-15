import cv2


class ImagePDFReader:
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
        Returns the path to the last image was read

        Возвращает путь к последнему прочитанному изображению
    """
    def get_path(self):
        return self.converter.get_path()

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
