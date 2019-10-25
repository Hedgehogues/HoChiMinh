from hochiminh.image_processing.connected_components import ConnectedComponents
from hochiminh.image_processing.cross_detector import CrossDetector
from hochiminh.image_processing.hochiminh import HoChiMinh
from hochiminh.image_processing.lines_detector import SobelDirector
from hochiminh.image_processing.ocr import TesseractWrapper
from hochiminh.io.pdfconverter import PDFConverter
from hochiminh.io.reader import ImagePDFReader


class PDFParserAPI:

    def __init__(self, in_path, out_path, resolution=130, max_steps=20, detected_steps=18, line_width=8,
                 binarization=200):
        self.parser = PDFParser(
            table_extractor=HoChiMinh(
                reader=ImagePDFReader(
                    PDFConverter(in_path=in_path, out_path=out_path, resolution=resolution)
                ),
                lines_detector=SobelDirector(),
                connected_components=ConnectedComponents(),
                cross_detector=CrossDetector(max_steps=max_steps, detected_steps=detected_steps, line_width=line_width),
                ocr=TesseractWrapper(),
                binarization=binarization
            )
        )

    def extract_table(self):
        return self.parser.extract_table()


class PDFParser:

    def __init__(self, table_extractor):
        self.table_extractor = table_extractor
        self.table = []

    def extract_table(self):

        prev_base_path = ''
        while True:
            table_per_page = self.table_extractor.process_image()
            if table_per_page is None:
                table = self.table
                self.table = []
                break

            path_to_img = self.table_extractor.get_path()
            base_path = path_to_img[:str.rfind(path_to_img, '/') + 1]
            if base_path == prev_base_path or prev_base_path == '':
                prev_base_path = base_path
                self.table += table_per_page
            else:
                table = self.table
                self.table = table_per_page
                break

        return table
