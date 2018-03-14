import os
import unittest
from internal.pdfconverter import PDFConverter


class TestPDFConverter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        path = '../data/test/pdf-converter/'

        cls.next_image_answ_path = sorted(
            [
                '../data/test/pdf-converter/out_images/2.pdf/-1.ppm',
                '../data/test/pdf-converter/out_images/2.pdf/-2.ppm',
                '../data/test/pdf-converter/out_images/2.pdf/-3.ppm',
                '../data/test/pdf-converter/out_images/5.pdf/-1.ppm',
                '../data/test/pdf-converter/out_images/5.pdf/-2.ppm',
                '../data/test/pdf-converter/out_images/5.pdf/-3.ppm',
                '../data/test/pdf-converter/out_images/5.pdf/-4.ppm',
            ]
        )

        cls.in_path = path + 'pdf/'
        cls.out_path = path + 'out_images/'
        cls.extension = 'ppm'
        cls.pdf_converter = PDFConverter(in_path=cls.in_path, out_path=cls.out_path, extension=cls.extension)

    def __convert_all_match_images(self, folder_name, count_files):
        image_list = sorted(os.listdir(self.out_path + folder_name + '/'))
        self.assertListEqual(['page-' + str(ind) + '.' + self.extension for ind in range(count_files)], image_list)

    def test_convert_all(self):
        self.pdf_converter.convert_all()
        listdir = sorted(os.listdir(self.out_path))
        self.assertListEqual(['1.pdf', '6.pdf'], listdir)
        self.__convert_all_match_images('1.pdf', 5)
        self.__convert_all_match_images('6.pdf', 4)

    def test_next_image(self):
        self.pdf_converter.convert_all()
        ind = 0
        paths = []
        while True:
            paths.append(self.pdf_converter.next_images())
            ind += 1
            if len(paths[-1]) == 0:
                break
        self.assertEqual(self.next_image_answ_path, sorted(paths)[1:])
        self.assertEqual(10, ind)


if __name__ == '__main__':
    unittest.main()
