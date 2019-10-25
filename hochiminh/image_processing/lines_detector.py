from scipy import ndimage

import cv2
import numpy as np
import scipy.stats as st

from hochiminh.image_processing.geometry import Point


class HoughTransformerCanny:
    """
        Преобразование Хафа для детекции вертикальных и горизонтальных прямых. Используется фильтр Кани для
        детекции границ
    """

    """
        theta_hough, rho_hough: шаги для пространства параметров преобразования Хафа (theta - угол, r - радиус)
        sensitivity_hough: порог срабатывания детектора преобразования Хафа
        eps_rad: отклонение прямой от вертикали/горизонтали
        up_edge, down_edge: верхний и нижний пороги для детекции границ при помощи фильтра Canny
        kernel_edge: размер ядра для детекции границ в фильтре Canny
    """
    def __init__(self,
                 theta_hough=np.pi / 180, rho_hough=1,
                 sensitivity_hough=120,
                 eps_rad=0.05,
                 up_edge=250, down_edge=10, kernel_edge=3):
        self.theta_hough, self.rho_hough = theta_hough, rho_hough
        self.sensitivity_hough = sensitivity_hough
        self.eps_rad = eps_rad
        self.up_edge = up_edge
        self.down_edge = down_edge
        self.kernel_edge = kernel_edge

    def __get_lines(self, image):
        edge = cv2.Canny(image, self.down_edge, self.up_edge, apertureSize=self.kernel_edge)
        lines = cv2.HoughLines(edge, self.rho_hough, self.theta_hough, self.sensitivity_hough)
        vertical = []
        horizontal = []
        for item in lines:
            rho, theta = item[0]
            if (-self.eps_rad <= theta) and theta <= self.eps_rad:
                vertical.append(int(rho))
            elif (np.pi / 2 - self.eps_rad <= theta) and theta <= np.pi / 2 + self.eps_rad:
                horizontal.append(int(rho))

        return horizontal, vertical

    @classmethod
    def __get_points(cls, horizontal, vertical):
        points = []
        for point_h in horizontal:
            for point_v in vertical:
                points.append(Point(y=point_h, x=point_v))

        return points

    """
        Получение всех точек пересечений вертикальных и горизонтальных прямых

        image: входное изображение

        Выходное значение: список объектов Point()
    """
    def get_points(self, image):
        horizontal, vertical = self.__get_lines(image.matrix)
        for point in self.__get_points(horizontal, vertical):
            image.description.add_point(point)
        return image


class SobelDirector:
    """
        Преобразование Хафа для детекции вертикальных и горизонтальных прямых. Используется фильтр Собеля для
        детекции границ с выбором оптимального направления в каждом квадрате
    """

    """
        eps_rad: отклонение прямой от вертикали/горизонтали
        kernel_edge: размер ядра для детекции границ в фильтре Canny
        kernel_filter: ядро медианного фильтра
        height: высота изображения, к которой приводится входное изображение. Если height is None, то изменение 
        размера не производится
        confidence_interval: доверительный интервал
        min_side_intensity: минимальная возможная суммарная интенсивность стороны 
        
        Замечание: если границы окажутся слишком тонкими, то медианный фильтр их не возьмёт
        Замечание: 
    """

    def __init__(self, eps_rad=0.1, kernel_edge=5, strength=20, kernel_filter=5, height=1000, level_confidence=0.90,
                 min_side_intensity=50000):
        self.eps_rad = eps_rad
        self.kernel_edge = kernel_edge
        self.kernel_filter = kernel_filter
        self.height = height
        self.level = level_confidence
        self.min_side_intensity = min_side_intensity

        self.input_height = 0
        self.strength = strength

    def __resize_image(self, image):
        self.input_height = image.shape[0]
        if self.height is not None:
            zoom = self.height / float(image.shape[0])
            width = int(float(image.shape[1]) * zoom) + 1
            image = cv2.resize(image, (width, self.height), interpolation=cv2.INTER_CUBIC)
        return image

    def __get_unique_lines(self, lines):
        unique_lines = []
        diff = np.diff(lines)
        start = 0
        lines_number = 1
        for diff_number in range(len(diff)):
            if diff[diff_number] > 3:
                unique_lines.append(int((lines[start] + lines[lines_number - 1]) / 2))
                start = lines_number
            lines_number += 1
        unique_lines.append(int((lines[start] + lines[-1]) / 2))
        return unique_lines

    def get_input_zoom(self, image):
        if self.height is not None:
            zoom = self.input_height / float(image.shape[0])
        else:
            zoom = 1
        return zoom

    def __get_lines(self, in_image):
        image = self.__resize_image(in_image)

        sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=self.kernel_edge)
        sobelx[np.abs(sobelx) < self.strength] = 0
        sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=self.kernel_edge)
        sobely[np.abs(sobely) < self.strength] = 0
        sobel_direct = np.arctan2(sobely, sobelx)

        vertical_edge = np.uint8(np.abs(sobel_direct) > np.pi - self.eps_rad) * 255
        horisontal_edge = np.uint8(
            (np.abs(sobel_direct) > np.pi / 2 - self.eps_rad) &
            (np.abs(sobel_direct) < np.pi / 2 + self.eps_rad)
        ) * 255

        horisontal_edge = ndimage.median_filter(horisontal_edge, size=self.kernel_filter)
        vertical_edge = ndimage.median_filter(vertical_edge, size=self.kernel_filter)

        h_lines_intensity = np.convolve(np.sum(horisontal_edge, axis=1), [0.75, 1, 0.75])
        v_lines_intensity = np.convolve(np.sum(vertical_edge, axis=0), [0.75, 1, 0.5])

        if h_lines_intensity.max() < self.min_side_intensity or v_lines_intensity.max() < self.min_side_intensity:
            return [], []

        h_threshold = st.t.interval(self.level, len(h_lines_intensity) - 1, loc=np.mean(h_lines_intensity),
                                    scale=st.sem(h_lines_intensity))[1]
        v_threshold = st.t.interval(self.level, len(v_lines_intensity) - 1, loc=np.mean(v_lines_intensity),
                                    scale=st.sem(v_lines_intensity))[1]

        zoom = self.get_input_zoom(image)

        h_coord_lines = np.uint(np.round(np.where(h_lines_intensity > h_threshold)[0] * zoom))
        v_coord_lines = np.uint(np.round(np.where(v_lines_intensity > v_threshold)[0] * zoom))

        horizontal = self.__get_unique_lines(h_coord_lines)
        vertical = self.__get_unique_lines(v_coord_lines)

        return horizontal, vertical

    @classmethod
    def __get_points(cls, horizontal, vertical):
        points = []
        for point_h in horizontal:
            for point_v in vertical:
                points.append(Point(y=int(point_h), x=int(point_v)))

        return points

    """
        Получение всех точек пересечений вертикальных и горизонтальных прямых

        image: входное изображение

        Выходное значение: список объектов Point()
    """
    def get_points(self, image):
        horizontal, vertical = self.__get_lines(image.matrix)
        for point in self.__get_points(horizontal, vertical):
            image.description.add_point(point)

        return image
