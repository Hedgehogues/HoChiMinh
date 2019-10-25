import ctypes

import cv2
import numpy as np

image = cv2.imread('data/test/ho_chi_minh/pdf/images/8.pdf/-1.ppm', cv2.IMREAD_GRAYSCALE)
# image = cv2.imread('data/test/ho_chi_minh/pdf/images/17.pdf/-1.ppm', cv2.IMREAD_GRAYSCALE)
# cv2.imshow('', image)
# cv2.waitKeyEx(0)

outdata = np.zeros(image.shape, dtype=np.double)
lib = ctypes.cdll.LoadLibrary('./internal/dev/main.so')
fun = lib.cfun

shift = ctypes.c_double(0.5)
p = ctypes.c_double(1)
border = ctypes.c_uint8(3)
mean_pow = ctypes.c_double(1)
var_pow = ctypes.c_double(1)

fun(ctypes.c_void_p(image.ctypes.data), ctypes.c_int(outdata.shape[0]), ctypes.c_int(outdata.shape[1]),
    border, mean_pow, var_pow, shift, p, ctypes.c_void_p(outdata.ctypes.data))

outdata = np.uint8(255 * (outdata - outdata.min(axis=0)) / (outdata.max(axis=0) - outdata.min(axis=0)))

cv2.imshow('', outdata)
cv2.waitKeyEx(0)
