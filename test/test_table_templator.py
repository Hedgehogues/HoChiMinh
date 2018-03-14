from internal.extractor.image_processing.connected_components import ConnectedComponents
from internal.extractor.image_processing.cross_detector import CrossDetector
from internal.extractor.image_processing.lines_detector import SobelDirector
from internal.extractor.image_processing.hochiminh import HoChiMinh
from internal.extractor.image_processing.ocr import TesseractWrapper
from internal.io.reader import ImageReader

path = "../data/test/cell-predictor/"

templator = HoChiMinh(
    # reader=ImageFromPDFReader(
    #     PDFConverter(in_path=path + 'pdf/', out_path=path + 'pdf/images/', resolution=130)
    # ),
    reader=ImageReader(path='../data/test/cell-predictor/pdf/images/10.pdf/-1.ppm'),
    lines_detector=SobelDirector(),
    connected_components=ConnectedComponents(),
    cross_detector=CrossDetector(max_steps=20, detected_steps=18, line_width=8),
    ocr=TesseractWrapper(),
    binarization=210
)
for i in range(4):
    print(i+1)
    table = templator.next_document()
    # cv2.imwrite(path+"out_images/tb_"+str(i+1)+".png", templator.next_points() * 250)
