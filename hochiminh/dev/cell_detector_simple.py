import cv2
import numpy as np
import matplotlib.pyplot as plt

from hochiminh.image_processing.connected_components import ConnectedComponents
from hochiminh.image_processing.geometry import Image
from hochiminh.io.reader import ImageReader

path = 'data/test/ho_chi_minh/pdf/images/6.pdf/page-vertical.png'
image = Image(image_reader=ImageReader(path), image_writer=None, binarization=210)
if image.load():
    image, components = ConnectedComponents().transform(image)

cv2.imshow('', image.matrix)
cv2.waitKey(0)
key = list(image.description.zones.keys())[0]
min_x = image.description.zones[key].get_min_x()
min_y = image.description.zones[key].get_min_y()
max_x = image.description.zones[key].get_max_x()
max_y = image.description.zones[key].get_max_y()
components = components[min_y:max_y, min_x:max_x]

components[components == key] = 0
components[components > 0] = 255
components = np.uint8(components)

cv2.imshow('', components)
cv2.waitKey(0)


hor = np.sum(components, axis=1)
vert = np.sum(components, axis=0)

components[np.where(hor == 0), :] = 255
components[:, np.where(vert == 0)] = 255

plt.plot(hor)
plt.show()
plt.plot(vert)
plt.show()

cv2.imshow('', components)
cv2.waitKey(0)
