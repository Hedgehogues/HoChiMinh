import os
import unittest

from shutil import rmtree

from hochiminh.io.pdfconverter import PDFConverter


class TestPDFConverter(unittest.TestCase):

    @classmethod
    def setUp(cls):
        path = '../data/test/pdf-converter/'

        cls.in_path = path + 'pdf/'
        cls.out_path = path + 'out_images/'
        cls.extension = 'ppm'

        cls.next_image_answ_path = sorted(
            [
                cls.out_path + '2.pdf/-1.ppm',
                cls.out_path + '2.pdf/-2.ppm',
                cls.out_path + '2.pdf/-3.ppm',
                cls.out_path + '5.pdf/-1.ppm',
                cls.out_path + '5.pdf/-2.ppm',
                cls.out_path + '5.pdf/-3.ppm',
                cls.out_path + '5.pdf/-4.ppm',
            ]
        )
        cls.pdf_converter = PDFConverter(in_path=cls.in_path, out_path=cls.out_path, resolution=120)

    def __convert_all_match_images(self, folder_name, count_files):
        image_list = sorted(os.listdir(self.out_path + folder_name + '/'))
        self.assertListEqual(['-' + str(ind + 1) + '.' + self.extension for ind in range(count_files)], image_list)

    def test_convert_all(self):
        self.pdf_converter.convert_all()
        listdir = sorted(os.listdir(self.out_path))
        self.assertListEqual(['2.pdf', '5.pdf'], listdir)
        self.__convert_all_match_images('2.pdf', 3)
        self.__convert_all_match_images('5.pdf', 4)

        if os.path.isdir(self.out_path):
            rmtree(self.out_path)
        else:
            self.assertFalse('There is not folder with images')

    def test_next_document(self):
        self.pdf_converter.convert_all()

        paths = self.pdf_converter.next_paths_to_documents()
        self.assertEqual(3, len(paths))
        self.assertListEqual(self.next_image_answ_path[:3], sorted(paths))

        paths = self.pdf_converter.next_paths_to_documents()
        self.assertEqual(4, len(paths))
        self.assertListEqual(self.next_image_answ_path[3:], sorted(paths))

        if os.path.isdir(self.out_path):
            rmtree(self.out_path)
        else:
            self.assertFalse('There is not folder with images')

    def test_next_image(self):
        self.pdf_converter.convert_all()
        ind = 0
        paths = []
        while True:
            path = self.pdf_converter.next_path_to_image()
            if len(path) == 0:
                break
            paths.append(path)
            ind += 1
        self.assertListEqual(sorted(self.next_image_answ_path), sorted(paths))
        self.assertEqual(3 + 4, ind)

        if os.path.isdir(self.out_path):
            rmtree(self.out_path)
        else:
            self.assertFalse('There is not folder with images')


if __name__ == '__main__':
    unittest.main()
