import pytesseract as ocr
from PIL import Image
from multiprocessing import Process, Manager


class TesseractWrapper:

    def __init__(self, lang='rus', jobs=16):
        self.lang = lang
        self.jobs = jobs

    def __worker(self, matrix, in_sub_table, text_sub_table):
        ind_sub_table_ = 0
        for in_line in in_sub_table:
            for in_cell in in_line:
                img = matrix[in_cell.y_min:in_cell.y_max, in_cell.x_min:in_cell.x_max]
                text = ocr.image_to_string(Image.fromarray(img), lang=self.lang)
                text_sub_table[ind_sub_table_] = text
                ind_sub_table_ += 1

    def recognize_table(self, matrix, table):
        count_lines = len(table) // self.jobs + 1
        processes = []
        for line_ind, line in enumerate(table):
            text_sub_table = Manager().list([''] * count_lines * len(table[0]))
            in_sub_table = table[line_ind * count_lines:(line_ind + 1) * count_lines]
            p = Process(target=self.__worker, args=(matrix, in_sub_table, text_sub_table))
            p.start()
            processes.append({'process': p, 'sub_table': text_sub_table})

        line_ind = 0
        for p in processes:
            p['process'].join()
            cell_ind = 0
            for cell_text in p['sub_table']:
                if line_ind == len(table):
                    break
                table[line_ind][cell_ind].text = cell_text
                cell_ind += 1
                if cell_ind % len(table[0]) == 0:
                    cell_ind = 0
                    line_ind += 1
        return table
