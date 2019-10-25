import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from copy import deepcopy

from os import listdir
from os.path import isfile, join

from multiprocessing import Process
from numpy.random import randint, choice


class DatasetGenerator:

    def __init__(self, in_path, out_path):
        self.font_size = [11, 23]
        self.font_path = 'data/fonts/'
        self.fonts = ["1.ttf", "2.ttf", "3.ttf", "4.ttf", "5.ttf", "6.ttf", "7.ttf"]
        self.letters = list(range(ord('А'), ord('Я') + 1)) + \
            list(range(ord('а'), ord('я') + 1)) + \
            list(range(ord('0'), ord('9') + 1)) + \
            list(range(ord('a'), ord('z') + 1)) + \
            list(range(ord('A'), ord('Z') + 1))
        self.letters = [chr(letter) for letter in self.letters]
        self.erode_kernel = [1, 5]
        self.erode_iterate = [1, 5]
        self.dilate_kernel = [1, 5]
        self.dilate_iterate = [1, 5]
        self.gauss_kernel = [1, 5]
        self.gauss_sigma = [0, 4]
        self.seq_len = [1, 8]
        self.sep = [' ', '\n']
        self.seqs = [1, 10]
        self.intensity = [128, 255]
        self.in_path = in_path
        self.out_path = out_path

    def sample(self, inds, id):
        num = inds[0]
        print('Process', id, 'was started')
        i = 0
        while num < inds[-1]:
            image = Image.fromarray(np.zeros((160, 160), dtype=np.uint8))
            draw = ImageDraw.Draw(image)

            seq = ''
            for _ in np.arange(randint(self.seqs[0], self.seqs[1])):
                seq_len = randint(self.seq_len[0], self.seq_len[1])
                seq += ''.join([choice(self.letters) for _ in np.arange(seq_len)])
                seq += choice(self.sep)

            font_type = self.font_path + choice(self.fonts)
            font_size = randint(self.font_size[0], self.font_size[1])
            font = ImageFont.truetype(font_type, font_size)
            intensity = randint(self.intensity[0], self.intensity[1])
            draw.text((0, 0), seq, intensity, font=font)
            in_image = np.array(deepcopy(image))
            in_image[in_image > 0] = 255

            etalon_image = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
            etalon_draw = ImageDraw.Draw(etalon_image)
            etalon_font = ImageFont.truetype(font_type, font_size)
            etalon_draw.text((0, 0), seq, 255, font=etalon_font)
            cv2.imwrite(self.in_path + str(num) + '.tif', np.array(etalon_image))
            noise_type = randint(0, 9)
            if noise_type == 0:
                pass
            elif noise_type == 1:
                sigma = randint(0, 3)
                image = cv2.GaussianBlur(np.array(image), (3, 3), sigma)
            elif noise_type == 2:
                image = cv2.medianBlur(np.array(image), 3)
            elif noise_type == 3:
                image = cv2.dilate(np.array(image), np.ones((3, 3), np.uint8), iterations=1)
            elif noise_type == 5:
                if font_size > 20:
                    image = cv2.dilate(np.array(image), np.ones((3, 3), np.uint8), iterations=1)
                else:
                    continue
            elif noise_type == 6:
                if font_size > 22:
                    image = cv2.dilate(np.array(image), np.ones((3, 3), np.uint8), iterations=1)
                    image = cv2.GaussianBlur(np.array(image), (3, 3), 0)
                else:
                    continue
            elif noise_type == 7:
                if font_size > 22:
                    image = cv2.GaussianBlur(np.array(image), (3, 3), 0)
                    image = cv2.dilate(np.array(image), np.ones((3, 3), np.uint8), iterations=1)
                else:
                    continue
            elif noise_type == 8:
                if font_size > 22:
                    image = cv2.erode(np.array(image), np.ones((2, 2), np.uint8), iterations=1)
                else:
                    continue
            cv2.imwrite(self.out_path + str(num) + '.tif', np.array(image))
            if i > 0 and i % 500 == 0:
                print('#', id, '. Step:', i)
            num += 1
            i += 1


def extract_non_zero_image(in_image, out_image, max_size, border=0):
    vert = np.where(np.sum(out_image, axis=1) > 0)[0]
    hor = np.where(np.sum(out_image, axis=0) > 0)[0]
    min_y = max(0, np.min(vert) - border)
    min_x = max(0, np.min(hor) - border)
    in_empty_image = np.zeros(max_size, np.uint8)
    out_empty_image = np.zeros(max_size, np.uint8)
    max_y = min(min_y + max_size[0], len(in_image))
    max_x = min(min_x + max_size[1], len(in_image[0]))
    in_empty_image[:max_y - min_y, :max_x - min_x] = in_image[min_y:max_y, min_x:max_x]
    out_empty_image[:max_y - min_y, :max_x - min_x] = out_image[min_y:max_y, min_x:max_x]
    return in_empty_image, out_empty_image


if __name__ == "__main__":
    in_path = '../rosatom_dataset/in/'
    out_path = '../rosatom_dataset/out/'
    n = 20000
    i = 0
    pr_count = 8
    DS = DatasetGenerator(in_path, out_path)
    step = n // pr_count + 15
    process = []
    for pr_num in range(pr_count):
        inds = range(min(step * pr_num, n), min(step * (pr_num + 1), n))
        p = Process(target=DS.sample, args=(inds, pr_num))
        p.start()
        process.append(p)
    for p in process:
        p.join()
