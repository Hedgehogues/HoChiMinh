import unittest

from internal.image_processing.connected_components import ConnectedComponents
from internal.image_processing.cross_detector import CrossDetector
from internal.image_processing.lines_detector import SobelDirector
from internal.image_processing.hochiminh import HoChiMinh
from internal.image_processing.ocr import TesseractWrapper
from internal.image_processing.hochiminh import PDFParser
from internal.io.pdfconverter import PDFConverter
from internal.io.reader import ImagePDFReader


class TestPDFConverter(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.path = "../data/test/ho_chi_minh/"
        cls.parser = PDFParser(
            table_extractor=HoChiMinh(
                reader=ImagePDFReader(
                    PDFConverter(in_path=cls.path + 'pdf/', out_path=cls.path + 'pdf/images/', resolution=130)
                ),
                lines_detector=SobelDirector(),
                connected_components=ConnectedComponents(),
                cross_detector=CrossDetector(max_steps=20, detected_steps=18, line_width=8),
                ocr=TesseractWrapper(),
                binarization=210
            )
        )

    def test_extract_table(self):

        # The first pdf
        table = self.parser.extract_table()
        self.assertEqual(30, len(table))
        for line in table:
            self.assertEqual(9, len(line), self.path + '4.pdf has not processed')

        # The second pdf
        table = self.parser.extract_table()
        self.assertEqual(31, len(table))
        for line in table:
            self.assertEqual(9, len(line), self.path + '5.pdf has not processed')

        # The third pdf
        table = self.parser.extract_table()
        self.assertEqual(18, len(table))
        for line in table:
            self.assertEqual(5, len(line), self.path + '6.pdf has not processed')

        # Finish
        table = self.parser.extract_table()
        self.assertEqual(0, len(table))
        for line in table:
            self.assertEqual(0, len(line), 'Finishing is failure')


if __name__ == '__main__':
    unittest.main()
