from collections import defaultdict
from operator import itemgetter

from sklearn.neighbors import KDTree

from hochiminh.image_processing.geometry import Image, Point, Cell


class HoChiMinh:
    """
        Алгоритм выделяет ячейки таблицы на картинке. Каждой ячейке соответствуют координаты и извлечённая из этой ячейки
        информация
    """

    """
        reader: ридер, читающий изображения
        lines_detector: детектор линий
        cross_detector: детектор, определяющий точки пересечения сторон таблицы
        connected_components: объект, детектирующий компоненты связности
        ocr: система, обрабатывающая ячейки таблицы

        binarization: порог бинаризации изображения

        # Получение уникальных точек
        kd_tree_leaf_size: размер листьев в KD-деревьях
        knn: число ближайших соседей
        opt_dist: дистанция, на которой точки считаются неотличимыми
                                                                     
        seed: инициализация генератора случайных чисел
    """
    def __init__(self,
                 reader, lines_detector, cross_detector, connected_components, ocr,
                 binarization=230,
                 kd_tree_leaf_size=40, knn=20, opt_dist=6,
                 seed=42, zoom_height=600
                 ):
        self.connected_components = connected_components
        self.cross_detector = cross_detector
        self.lines_detector = lines_detector
        self.ocr = ocr

        self.zoom_height = zoom_height

        self.leaf_size = kd_tree_leaf_size
        self.knn = knn
        self.opt_dist = opt_dist

        self.seed = seed

        self.__image = Image(image_reader=reader, image_writer=None, binarization=binarization)
        self.__unique_clusters = defaultdict()
        self.__x = []
        self.__y = []

    def __select_points(self, components):
        actual_points = []

        self.cross_detector.set_components(components)
        self.cross_detector.set_labels(self.__image.get_zone_labels())

        points = self.__image.description.points.values()
        for point in points:
            is_cross, shift = self.cross_detector.detect(start=point)
            if is_cross:
                actual_points.append(point + shift)

        return actual_points

    def __get_almost_unique_points(self, active_points, mean):
        unique_active_points = []
        distance, index = KDTree(active_points, leaf_size=self.leaf_size).query(active_points, k=self.knn)
        used_points = set()
        for ind in range(len(distance)):
            if ind in used_points:
                continue

            used_points.add(ind)

            nearest_points_ind = index[ind][distance[ind] < self.opt_dist]
            used_points = used_points.union(set(nearest_points_ind))

            nearest_points = [Point(x=active_points[ind][0], y=active_points[ind][1]) for ind in nearest_points_ind]
            unique_active_points.append(mean(nearest_points))
        return unique_active_points

    def __alignment_coords(self, coord, unique_active_points, setter):
        mean = [coord[0][0]]
        start = 0
        for ind in range(len(coord) - 1):
            if abs(coord[ind][0] - coord[ind + 1][0]) < self.opt_dist:
                delta = ind - start + 1
                mean[-1] = (mean[-1] * delta + coord[ind + 1][0]) / (delta + 1)
            else:
                start = ind + 1
                mean.append(coord[ind + 1][0])
        mean_ind = 0
        new_coords = [int(round(mean[mean_ind]))]
        unique_active_points[coord[0][1]] = setter(unique_active_points[coord[0][1]], int(round(mean[mean_ind])))
        for ind in range(len(coord) - 1):
            if abs(coord[ind][0] - coord[ind + 1][0]) >= self.opt_dist:
                mean_ind += 1
            new_coords.append(int(round(mean[mean_ind])))
            unique_active_points[coord[ind + 1][1]] = setter(unique_active_points[coord[ind + 1][1]], int(round(mean[mean_ind])))
        return new_coords, unique_active_points

    def __create_table(self):
        table = []
        for ind_y in range(len(self.__y)):
            if ind_y == 0:
                continue
            table.append([])
            for ind_x in range(len(self.__x)):
                if ind_x == 0:
                    continue
                cell = Cell(
                    x_min=self.__x[ind_x - 1], y_min=self.__y[ind_y - 1],
                    y_max=self.__y[ind_y], x_max=self.__x[ind_x],
                    prob=1.
                )
                table[-1].append(cell)
        return table

    """
        Получение каркаса таблицы

        Выходные параметры 
        sensitivity: степень освещённости изображения (от 0 до 1. 0 -- чёрный фон)
        width: ширина точки пересечения узла изображения
    """
    def get_table_template(self, sensitivity=0.1, width=3):
        image = self.__image.get_binary_matrix() * sensitivity
        for x_coord in self.__x:
            for y_coord in self.__y:
                start_y = y_coord - width
                finish_y = y_coord + width + 1
                start_x = x_coord - width
                finish_x = x_coord + width + 1
                image[start_y:finish_y, start_x:finish_x] = 255
        return image

    """
        Получить путь к картинке, которая была обработана последней
    """
    def get_path(self):
        return self.__image.description.src

    """
        Обработка картинок с таблицами

        Выходные параметры: таблица с ячейками (список списков Cell)
    """
    def process_image(self):

        if not self.__image.load():
            return None

        self.__unique_clusters = defaultdict()
        self.__x = []
        self.__y = []

        # TODO: перенести выделение компонент связности сюда

        self.__image = self.lines_detector.get_points(self.__image)

        if len(self.__image.description.points) == 0:
            return []

        self.__image, components = self.connected_components.transform(self.__image)
        if self.__image.get_zone_labels() == 0:
            return []

        # TODO: при разрывных границах смотри несколько первых кластеров. 9.pdf страница 1. Возможно, достаточно
        # TODO: посчитать размерность Минковского, вместо выделения компонент связности
        # TODO: (https://habrahabr.ru/post/208368/)
        # Выделение узловых точек
        active_points = self.__select_points(components)
        if len(active_points) == 0:
            return []

        # Процесс получения близких точек
        active_points_list = list(map(lambda x: next(iter(x)), active_points))
        unique_active_points = self.__get_almost_unique_points(active_points_list, Point.mean_points)

        # Среди близких выбираем одну
        for ind, point in enumerate(unique_active_points):
            self.__x.append([point.x, ind])
            self.__y.append([point.y, ind])
        self.__x = sorted(self.__x, key=itemgetter(0))
        self.__y = sorted(self.__y, key=itemgetter(0))
        self.__x, unique_active_points = self.__alignment_coords(self.__x, unique_active_points, lambda arg, x: Point(x=x, y=arg.y))
        self.__y, unique_active_points = self.__alignment_coords(self.__y, unique_active_points, lambda arg, y: Point(y=y, x=arg.x))
        self.__x = sorted(list(set(self.__x)))
        self.__y = sorted(list(set(self.__y)))

        self.ocr = None
        if self.ocr is not None:
            table = self.ocr.recognize_table(self.__image.matrix, self.__create_table())
        else:
            table = self.__create_table()

        return table
