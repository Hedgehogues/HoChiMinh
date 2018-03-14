import os
from shutil import rmtree

from pdf2image import convert_from_path


class PDFConverter:
    """
        Конвертер, реализующий преобразование pdf в изображения
    """

    """
        in_paths: путь к директории со всеми pdf, которые необходимо преобразовать в изображения
        out_paths: путь к директории, в которую все изображения будут складываться
        extension: расширение, с которым будут сохраняться изображения
        resolution: масштаб получаемого изображения
    """
    def __init__(self, in_path, out_path=None, resolution=100):
        self.in_paths = [
            in_path + path
            for path in os.listdir(in_path)
            if os.path.splitext(os.path.basename(path))[1] == '.pdf'
        ]
        self.out_path = out_path
        self.resolution = resolution

        self.__list_paths_to_images = []
        self.__last_image_path = 0
        self.__last_pdf_path = 0

    """
        Возвращает путь из пула конвертированных изображений к следующему изображению. По достижению конца списка будет
        возвращать пустые строки
    """
    def next_images(self):
        self.__last_image_path += 1
        if self.__last_image_path > len(self.__list_paths_to_images):
            return ''
        return self.__list_paths_to_images[self.__last_image_path - 1]

    """
        Конвертирует следующий pdf-файл из пула pdf-файлов. Если до этого был вызван метод convert_all(), завершается.

        При вызове создаётся дерево каталогов под соответствующие pdf-файлы. Если один из каталогов существует, то он
        предварительно очищается
    """
    def convert_next(self):
        if self.__last_pdf_path >= len(self.in_paths):
            return

        in_path = self.in_paths[self.__last_pdf_path]
        self.__last_pdf_path += 1

        out_directory = self.out_path + os.path.basename(in_path) + '/'
        if os.path.isdir(out_directory):
            rmtree(out_directory)
        os.makedirs(out_directory)
        count_images = len(convert_from_path(in_path, dpi=self.resolution, output_folder=out_directory))
        self.__list_paths_to_images += [
            out_directory + '-' + str(ind) + '.ppm'
            for ind in range(count_images)
        ]

    """
        Конвертирует все pdf-файлы из пула pdf-файлов. Если до этого вызвался метод convert_next(), конвертирует только
        не тронутые pdf-файлы из пула pdf-файлов.

        При вызове создаётся дерево каталогов под соответствующие pdf-файлы. Если один из каталогов существует, то он
        предварительно очищается
    """
    def convert_all(self):
        while self.__last_pdf_path < len(self.in_paths):
            self.convert_next()
