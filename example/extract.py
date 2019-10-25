from hochiminh import pdf_parser
from hochiminh.image_processing import hochiminh
from hochiminh.image_processing.connected_components import ConnectedComponents
from hochiminh.image_processing.cross_detector import CrossDetector
from hochiminh.image_processing.lines_detector import SobelDirector
from hochiminh.image_processing.ocr import TesseractWrapper
from hochiminh.io import pdfconverter, reader

path = "../data/test/ho_chi_minh/"
parser = pdf_parser.PDFParser(
    table_extractor=hochiminh.HoChiMinh(
        reader=reader.ImagePDFReader(
            pdfconverter.PDFConverter(in_path=path + 'pdf/', out_path=path + 'pdf/images/', resolution=130)
        ),
        lines_detector=SobelDirector(),
        connected_components=ConnectedComponents(),
        cross_detector=CrossDetector(max_steps=20, detected_steps=18, line_width=8),
        ocr=TesseractWrapper(),
        binarization=210
    )
)

tabels = parser.extract_table()
for tabel in tabels:
    print('--------------- Table ---------------')
    for cell in tabel:
        print(cell.__dict__)
