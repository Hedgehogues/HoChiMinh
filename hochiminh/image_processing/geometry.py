import math

import numpy as np
import cv2


class ImageDescription:
    def __init__(self, src='', matrix=None):
        self.src = src
        if matrix is not None:
            self.height = matrix.shape[0]
            self.width = matrix.shape[1]
        else:
            self.height = matrix.shape[0]
            self.width = matrix.shape[1]

        self.zones = {}
        self.points = {}
        self.max_point_index = -1
        self.max_zone_index = -1

    @classmethod
    def __add(cls, max_index, structure, element, index):
        if index is None:
            max_index += 1
            structure[max_index] = element
        elif index in structure:
            raise KeyError()
        else:
            max_index = max(max_index, index)
            structure[index] = element

        return max_index, structure

    def add_point(self, point, index=None):
        self.max_point_index, self.points = self.__add(self.max_point_index, self.points, point, index)

    def add_zone(self, zone, index=None):
        self.max_zone_index, self.zones = self.__add(self.max_zone_index, self.zones, zone, index)

    def set_matrix(self, matrix):
        self.set_size(height=matrix.shape[0], width=matrix.shape[1])

    def set_size(self, height, width):
        self.height = height
        self.width = width


class Image:

    def __init__(self, image_reader, image_writer, binarization=220):
        self.image_reader = image_reader
        self.image_writer = image_writer
        self.binarization = binarization

        self.matrix = None
        self.description = None

    def get_binary_matrix(self):
        return np.uint8(self.matrix < self.binarization) * 255

    def get_zone_labels(self):
        labels = set()
        for zone in self.description.zones.values():
            labels.add(zone.label)
        return labels

    def set_zoom(self, height, width=None):
        zoom = height / float(self.matrix.shape[0])
        if width is None:
            width = int(float(self.matrix.shape[1]) * zoom) + 1
        self.matrix = cv2.resize(self.matrix, (width, height), interpolation=cv2.INTER_CUBIC)

        for zone in self.description.zones:
            zone.set_zoom(zoom)
        for point in self.description.points:
            point.set_zoom(zoom)

        self.description.height = height
        self.description.width = width

    @classmethod
    def dump(cls):
        raise NotImplemented()

    def load(self):
        self.matrix = self.image_reader.read()
        if self.matrix is None:
            return False
        self.description = ImageDescription(src=self.image_reader.get_path(), matrix=self.matrix)
        return True


class Point:

    @staticmethod
    def mean_points(list_points):
        res_point = Point()
        for point in list_points:
            res_point.x += point.x
            res_point.y += point.y
        res_point.x = int(res_point.x / len(list_points))
        res_point.y = int(res_point.y / len(list_points))
        return res_point

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __eq__(self, p):
        return p.x == self.x and p.y == self.y

    def __abs__(self):
        return Point(x=abs(self.x), y=abs(self.y))

    def __mod__(self, scalar):
        return Point(x=self.x % scalar, y=self.y % scalar)

    def __add__(self, p):
        """Point(x1+x2, y1+y2)"""
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        """Point(x1-x2, y1-y2)"""
        return Point(self.x - p.x, self.y - p.y)

    def __mul__(self, scalar):
        """Point(x1*x2, y1*y2)"""
        return Point(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        """Point(x1/x2, y1/y2)"""
        return Point(self.x / scalar, self.y / scalar)

    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)

    def __iter__(self):
        yield (self.x, self.y)

    def set_zoom(self, zoom):
        self.x = int(self.x * zoom) + 1
        self.y = int(self.y * zoom) + 1

    def ort(self):
        return Point(x=self.x + 1, y=self.y + 1) % 2

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def distance_to(self, p):
        """Calculate the distance between two points."""
        return (self - p).length()

    def as_tuple(self):
        """(x, y)"""
        return (self.x, self.y)

    def clone(self):
        """Return a full copy of this point."""
        return Point(self.x, self.y)

    def integerize(self):
        """Convert co-ordinate values to integers."""
        self.x = int(self.x)
        self.y = int(self.y)

    def floatize(self):
        """Convert co-ordinate values to floats."""
        self.x = float(self.x)
        self.y = float(self.y)

    def move_to(self, x, y):
        """Reset x & y coordinates."""
        self.x = x
        self.y = y

    def slide(self, p):
        '''Move to new (x+dx,y+dy).

        Can anyone think up a better name for this function?
        slide? shift? delta? move_by?
        '''
        self.x = self.x + p.x
        self.y = self.y + p.y

    def slide_xy(self, dx, dy):
        '''Move to new (x+dx,y+dy).

        Can anyone think up a better name for this function?
        slide? shift? delta? move_by?
        '''
        self.x = self.x + dx
        self.y = self.y + dy

    def rotate(self, rad):
        """Rotate counter-clockwise by rad radians.

        Positive y goes *up,* as in traditional mathematics.

        Interestingly, you can use this in y-down computer graphics, if
        you just remember that it turns clockwise, rather than
        counter-clockwise.

        The new position is returned as a new Point.
        """
        s, c = [f(rad) for f in (math.sin, math.cos)]
        x, y = (c * self.x - s * self.y, s * self.x + c * self.y)
        return Point(x, y)

    def rotate_about(self, p, theta):
        """Rotate counter-clockwise around a point, by theta degrees.

        Positive y goes *up,* as in traditional mathematics.

        The new position is returned as a new Point.
        """
        result = self.clone()
        result.slide(-p.x, -p.y)
        result.rotate(theta)
        result.slide(p.x, p.y)
        return result


class Cell:
    def __init__(self, x_min=0, x_max=0, y_min=0, y_max=0, prob=0.0, text=''):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.prob = prob
        self.text = text


class Rectangle:
    """
        Описывает кластеризованные области, получаемые в результате выполнения cv2.connectedComponentsWithStats
    """

    """
        width: ширина прямоугольника, в который попадает область
        height: высота прямоугольника, в который попадает область
        total_area: точная площадь в пикселях
        label: номер кластера
        centroid: центроид прямоугольника, в который попадает область, описываемый объектом Point()
        left_top_angle: левый верхний угол прямоугольника, в который попадает область, описываемый объектом Point()
        bbox_area: площадь прямоугольника, в который попадает область (width * height)
    """
    def __init__(self, min_x=0, min_y=0, max_x=0, max_y=0, total_area=0, label=0, centroid=Point(0, 0)):
        self.total_area = total_area
        self.label = label
        self.centroid = centroid
        self.__min_x = min_x
        self.__max_x = max_x
        self.__min_y = min_y
        self.__max_y = max_y

        self.bbox_area = self.get_height() * self.get_width()

    def get_min_x(self):
        return self.__min_x

    def get_max_x(self):
        return self.__max_x

    def get_min_y(self):
        return self.__min_y

    def get_max_y(self):
        return self.__max_y

    def get_left_up(self):
        return Point(x=self.__min_x, y=self.__min_y)

    def get_left_down(self):
        return Point(x=self.__min_x, y=self.__max_y)

    def get_right_down(self):
        return Point(x=self.__max_x, y=self.__max_y)

    def get_right_up(self):
        return Point(x=self.__max_x, y=self.__min_y)

    def set_zoom(self, zoom):
        self.__min_y = int(self.__min_y * zoom) + 1
        self.__min_x = int(self.__min_x * zoom) + 1
        self.__max_y = int(self.__max_y * zoom) + 1
        self.__max_x = int(self.__max_x * zoom) + 1

    def square(self):
        return float((abs(self.__max_x - self.__min_x)) * (abs(self.__max_y - self.__min_y)))

    def __key(self):
        return self.__min_x, self.__min_y, self.__max_x, self.__max_y, self.total_area, self.bbox_area

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Rectangle):
            return (self.__min_x == other.__min_x and
                    self.__min_y == other.__min_y and
                    self.__max_x == other.__max_x and
                    self.__max_y == other.__max_y and
                    self.bbox_area == other.bbox_area and
                    self.total_area == other.total_area)
        return NotImplemented

    # TODO: Убрать x и y
    def __point_into_segment_x(self, point, segment):
        return (segment.min_x <= point) and (point <= segment.max_x - 1)

    def __segment_into_segment_x(self, segment1, segment2):
        return (segment2.min_x <= segment1.min_x) and (segment1.max_x <= segment2.max_x - 1)

    def __point_into_segment_y(self, point, segment):
        return (segment.min_y <= point) and (point <= segment.max_y)

    def __segment_into_segment_y(self, segment1, segment2):
        return (segment2.min_y <= segment1.min_y) and (segment1.max_y <= segment2.max_y)

    def rectangle_intersection(self, rect2):
        x = sorted([self.__min_x, self.__max_x, rect2.min_x, rect2.max_x])
        y = sorted([self.__min_y, self.__max_y, rect2.min_y, rect2.max_y])
        intersection_x = self.__point_into_segment_x(rect2.min_x, self) or self.__point_into_segment_x(rect2.max_x, self) or \
                         self.__point_into_segment_x(self.__min_x, rect2) or self.__point_into_segment_x(self.__max_x, rect2) or \
                         self.__segment_into_segment_x(self, rect2) or self.__segment_into_segment_x(rect2, self)
        intersection_y = self.__point_into_segment_y(rect2.min_y, self) or self.__point_into_segment_y(rect2.max_y, self) or \
                         self.__point_into_segment_y(self.__min_y, rect2) or self.__point_into_segment_y(self.__max_y, rect2) or \
                         self.__segment_into_segment_y(self, rect2) or self.__segment_into_segment_y(rect2, self)
        if intersection_x and intersection_y:
            return Rectangle(min_x=x[1], max_x=x[2], min_y=y[1], max_y=y[2])
        else:
            return None

    def sorensen_dice_measure(self, b):
        intersection = self.rectangle_intersection(b)
        if not (intersection is None):
            return 2. * intersection.square() / (self.square() + b.square())
        else:
            return 0.

    def get_height(self):
        return self.__max_y - self.__min_y + 1

    def get_width(self):
        return self.__max_x - self.__min_x + 1
