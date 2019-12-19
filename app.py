import os
import shutil

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException

from hochiminh.image_processing.connected_components import ConnectedComponents
from hochiminh.image_processing.cross_detector import CrossDetector
from hochiminh.image_processing.hochiminh import HoChiMinh
from hochiminh.image_processing.lines_detector import SobelDirector
from hochiminh.image_processing.ocr import TesseractWrapper
from hochiminh.io.pdfconverter import PDFConverter
from hochiminh.io.reader import ImagePDFReader
from hochiminh.pdf_parser import PDFParser

from multiprocessing import Lock


class StatusService:
    def __init__(self):
        self.status = False
        self.__mutex = Lock()

    def start(self):
        self.__mutex.acquire()
        if self.status:
            return False
        self.status = True
        self.__mutex.release()
        return True

    def finish(self):
        self.__mutex.acquire()
        if not self.status:
            return False
        self.status = False
        self.__mutex.release()
        return True


status = StatusService()
app = FastAPI()

in_path = 'data/uploaded/'
out_path = 'data/uploaded/images/'
chunk_size = 10000
PORT = 8000


dscr = 'get status of processing'
@app.get("/status", description=dscr, status_code=200)
def read_item():
    if status.status:
        return {'status': 'processing'}
    return {'status': 'free'}


dscr = 'pdf parsing'
@app.post("/parse/pdf", description=dscr, status_code=200)
def parse_pdf(f: UploadFile = File(...)):
    if f.content_type != 'application/pdf':
        if not status.finish():
            raise HTTPException(status_code=500, detail='status error')
        raise HTTPException(status_code=415, detail='you must upload pdf file')
    if not status.start():
        if not status.finish():
            raise HTTPException(status_code=500, detail='status error')
        raise HTTPException(status_code=409, detail='processing')
    p = in_path+'file.pdf'
    with open(p, 'wb') as fd:
        for chunk in iter(lambda: f.file.read(chunk_size), b''):
            fd.write(chunk)

    parser = PDFParser(
        table_extractor=HoChiMinh(
            reader=ImagePDFReader(
                PDFConverter(in_path=in_path, out_path=out_path, resolution=130)
            ),
            lines_detector=SobelDirector(),
            connected_components=ConnectedComponents(),
            cross_detector=CrossDetector(max_steps=20, detected_steps=18, line_width=8),
            ocr=TesseractWrapper(),
            binarization=210
        )
    )
    table = parser.extract_table()
    os.remove(p)
    shutil.rmtree(out_path)
    if not status.finish():
        raise HTTPException(status_code=500, detail='status error')
    return {'cells': table}


uvicorn.run(app, host="0.0.0.0", port=PORT)
