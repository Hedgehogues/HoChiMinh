import unittest

from internal.image_processing.connected_components import ConnectedComponents
from internal.image_processing.cross_detector import CrossDetector
from internal.image_processing.lines_detector import SobelDirector
from internal.image_processing.hochiminh import HoChiMinh
from internal.image_processing.ocr import TesseractWrapper
from internal.image_processing.hochiminh import PDFParser
from internal.io.pdfconverter import PDFConverter
from internal.io.reader import ImageFromPDFReader


class TestPDFConverter(unittest.TestCase):

    @classmethod
    def setUp(cls):
        path = "../data/test/ho_chi_minh/"
        cls.parser = PDFParser(
            table_extractor=HoChiMinh(
                reader=ImageFromPDFReader(
                    PDFConverter(in_path=path + 'pdf/', out_path=path + 'pdf/images/', resolution=130)
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
            self.assertEqual(9, len(line))

        # The second pdf
        table = self.parser.extract_table()
        self.assertEqual(31, len(table))
        for line in table:
            self.assertEqual(9, len(line))


if __name__ == '__main__':
    unittest.main()
