import cv2
from os import listdir
from os.path import isfile, join

import numpy as np


def write(in_files, out_files, out_csv, in_csv):
    l = listdir(in_path)
    files = [f for f in listdir(in_path) if isfile(join(in_files, f))]

    in_images = []
    out_images = []
    i = 0
    for file_ in files:
        in_image = cv2.imread(in_files + file_, cv2.IMREAD_GRAYSCALE)
        out_image = cv2.imread(out_files + file_, cv2.IMREAD_GRAYSCALE)
        in_images.append(in_image.flatten().astype('float32') / 255.)
        out_images.append(out_image.flatten().astype('float32') / 255.)
        i += 1
        if i % 1000 == 0 and i > 0:
            print(i)

    np.savetxt(fname=out_csv, X=out_image, delimiter=",")
    np.savetxt(fname=in_csv, X=in_images, delimiter=",")


in_path = '../rosatom_dataset/in/'
out_path = '../rosatom_dataset/out/'
in_csv = 'data/in.csv'
out_csv = 'data/out.csv'
write(in_path, out_path, in_csv, out_csv)
