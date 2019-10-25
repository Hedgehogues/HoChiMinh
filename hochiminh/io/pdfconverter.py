import os
from shutil import rmtree

from pdf2image import convert_from_path


class PDFConverter:
    """
        Transform pdf to image (ppm-format)


        Конвертер, реализующий преобразование pdf в изображения
    """

    """
        in_paths: path to the directory with all pdf, which must be converted to images
        out_paths: path to the directory into which all images will be added
        extension: extension with which images will be saved
        resolution: the scale of the resulting image (dpi)
    
    
        in_paths: путь к директории со всеми pdf, которые необходимо преобразовать в изображения
        out_paths: путь к директории, в которую все изображения будут складываться
        extension: расширение, с которым будут сохраняться изображения
        resolution: масштаб получаемого изображения (dpi)
    """
    def __init__(self, in_path, out_path=None, resolution=100):
        self.in_paths = sorted([
            in_path + path
            for path in os.listdir(in_path)
            if os.path.splitext(os.path.basename(path))[1] == '.pdf'
        ])
        self.out_path = out_path
        self.resolution = resolution

        self.__list_paths_to_images = []
        self.__last_image_path = 0
        self.__last_pdf_path = 0

    """
        Returns the path to the last image was read

        Возвращает путь к последнему прочитанному изображению
    """
    def get_path(self):
        return '' if self.__last_image_path == 0 else self.__list_paths_to_images[self.__last_image_path - 1]

    """
        Returns the path to the next image from the pool of converted images. When you reach the end of the list, will 
        be return blank lines.
        
        
        Возвращает путь к следующему изображению из пула конвертированных изображений. По достижению конца списка будет
        возвращать пустые строки.
    """
    def next_path_to_image(self):
        self.__last_image_path += 1
        if self.__last_image_path > len(self.__list_paths_to_images):
            return ''
        return self.__list_paths_to_images[self.__last_image_path - 1]

    """
        Returns the paths to the list of images from the pool of converted images related to the next document. If the 
        next_path_to_image () method was called before this, the list of paths of only the raw images will be returned.
        If all the images have been processed, an empty list will be returned.
    
    
        Возвращает пути к списку изображений из пула конвертированных изображений, относящихся к следующему документу.
        Если перед этим вызывался метод next_path_to_image(), то будет возвращён список путей лишь только необработанных
        изображений. Если все изображения были обработаны, то будет возвращён пустой список.
    """
    def next_paths_to_documents(self):
        paths_to_pages = []
        while True:
            paths_to_pages.append(self.next_path_to_image())
            if len(paths_to_pages[-1]) == 0:
                break
            last_pdf_file = os.path.basename(paths_to_pages[-1][:paths_to_pages[-1].rfind('/')])
            if len(paths_to_pages) > 1:
                penultimate_pdf_file = os.path.basename(paths_to_pages[-2][:paths_to_pages[-2].rfind('/')])
                if os.path.basename(last_pdf_file) != os.path.basename(penultimate_pdf_file):
                    self.__last_image_path -= 1
                    break
        return paths_to_pages[:-1]

    """
        Converts the following pdf-file from the pdf-file pool. If the convert_all () method was called before, it is
        terminated.

        When you call, the directory tree is created for the corresponding pdf-files. If one of the directories exists, 
        then it pre-cleaned.


        Конвертирует следующий pdf-файл из пула pdf-файлов. Если до этого был вызван метод convert_all(), завершается.

        При вызове создаётся дерево каталогов под соответствующие pdf-файлы. Если один из каталогов существует, то он
        предварительно очищается
    """
    def convert_next(self):
        if self.__last_pdf_path >= len(self.in_paths):
            return

        in_path = self.in_paths[self.__last_pdf_path]
        self.__last_pdf_path += 1

        output_folder = self.out_path + os.path.basename(in_path) + '/'
        if os.path.isdir(output_folder):
            rmtree(output_folder)
        os.makedirs(output_folder)
        count_images = len(convert_from_path(in_path, dpi=self.resolution, output_folder=output_folder))
        self.__list_paths_to_images += [
            output_folder + '-' + '0' * (len(str(count_images)) - len(str(ind + 1))) + str(ind + 1) + '.ppm'
            for ind in range(count_images)
        ]

    """
        Converts all pdf-files from a pool of pdf-files. If before this method called convert_next (), converts only 
        unaffected pdf-files from the pdf-file pool.

        When you call, the directory tree is created for the corresponding pdf-files. If one of the directories exists,
        then it is previously cleaned.
        
    
        Конвертирует все pdf-файлы из пула pdf-файлов. Если до этого вызвался метод convert_next(), конвертирует только
        не тронутые pdf-файлы из пула pdf-файлов.

        При вызове создаётся дерево каталогов под соответствующие pdf-файлы. Если один из каталогов существует, то он
        предварительно очищается.
    """
    def convert_all(self):
        while self.__last_pdf_path < len(self.in_paths):
            self.convert_next()
