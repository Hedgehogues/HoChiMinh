import cv2
import numpy as np

from hochiminh.image_processing.geometry import Rectangle, Point


class ConnectedComponents:
    def __init__(self, connectivity=4, min_area=1000, neighbourhood=2, side_size=100, bbox_size=30000):
        self.connectivity = connectivity
        self.min_area = min_area
        self.neighbourhood = neighbourhood
        self.side_size = side_size
        self.area_size = bbox_size

    @classmethod
    def __create_zone(cls, label, components):
        return Rectangle(
            min_x=components[2][label, cv2.CC_STAT_LEFT],
            min_y=components[2][label, cv2.CC_STAT_TOP],
            max_x=components[2][label, cv2.CC_STAT_LEFT] + components[2][label, cv2.CC_STAT_WIDTH],
            max_y=components[2][label, cv2.CC_STAT_TOP] + components[2][label, cv2.CC_STAT_HEIGHT],
            total_area=components[2][label, cv2.CC_STAT_AREA],
            label=label,
            centroid=Point(y=components[3][1], x=components[3][0]),
        )

    def __get_unique_labels(self, point, components):

        start_y = point.y - self.neighbourhood
        finish_y = point.y + self.neighbourhood + 1
        start_x = point.x - self.neighbourhood
        finish_x = point.x + self.neighbourhood + 1

        labels = np.unique(components[start_y:finish_y, start_x:finish_x])

        # TODO: возможно labels != 0 неэффективно работает
        return labels[labels != 0]

    @classmethod
    def __add_clusters(cls, labels, clusters):
        for label in labels:
            if label not in clusters:
                clusters[label] = 1
            else:
                clusters[label] += 1

    def __filter_table_zones(self, image):
        table_zone = {}
        for zone in image.description.zones.values():
            if zone.get_height() > self.side_size and zone.get_width() > self.side_size and \
               zone.bbox_area > self.area_size:
                    table_zone[zone.label] = zone
        image.description.zones = table_zone

        # TODO: выбрать несколько оптимальных кластеров
        # TODO: https://stackoverflow.com/questions/11513484/1d-number-array-clustering#comment65709086_11516590
        # TODO: https://journal.r-project.org/archive/2011-2/RJournal_2011-2_Wang+Song.pdf
        # TODO: http://weka.wikispaces.com/Discretizing+datasets
        # TODO: http://scikit-learn.org/stable/modules/clustering.html
        # TODO: https://macwright.org/2013/02/18/literate-jenks.html
        # TODO: https://en.wikipedia.org/wiki/Kernel_density_estimation
        # TODO: https://en.wikipedia.org/wiki/Jenks_natural_breaks_optimization

        return image

    def transform(self, image):
        # TODO: Что такое connectedComponentsWithStatsWithAlgorithm
        # TODO: поглядеть оставшиеся параметреы у connectedComponentsWithStats
        components = cv2.connectedComponentsWithStats(
            image=image.get_binary_matrix(),
            connectivity=self.connectivity
        )

        for label in range(1, len(components[2])):
            image.description.add_zone(index=label, zone=self.__create_zone(label, components))

        self.__filter_table_zones(image)

        return image, components[1]
