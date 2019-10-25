import numpy as np

from hochiminh.image_processing.geometry import Point


class CrossDetector:
    def __init__(self, max_steps=12, line_width=2, detected_steps=11):
        self.max_steps = max_steps
        self.line_width = line_width
        self.detected_steps = detected_steps

        self.directs = [Point(x=0, y=1), Point(x=1, y=0), Point(x=-1, y=0), Point(x=0, y=-1)]
        self.the_same_directs = [abs(direct) == Point(x=0, y=1) for direct in self.directs]
        self.components = None
        self.labels = set()

    def __border_cond(self, coord):
        if self.components is None:
            return False

        return not (
            (coord.x >= 0) and (coord.x < len(self.components[0])) and
            (coord.y >= 0) and (coord.y < len(self.components))
        )

    def __iter_direct(self, start, direct):
        step = 0
        not_null_steps = 0
        while self.max_steps >= step:
            coord = start + direct * step
            if self.__border_cond(coord):
                break
            if self.components[coord.y][coord.x] in self.labels:
                not_null_steps += 1
            if self.components[coord.y][coord.x] == 0 and not_null_steps > 0:
                break
            step += 1
        return not_null_steps

    def __is_detect(self, direct):
        return direct > self.detected_steps

    def __detect_directs(self, start):
        if self.components is None:
            return

        opt_direct_steps = []
        shift = Point()
        for direct in self.directs:
            opt_step = 0
            opt_shift = 0
            for step_width in range(-self.line_width, self.line_width + 1):
                new_step = self.__iter_direct(start + abs(direct.ort()) * step_width, direct)
                if opt_step < new_step:
                    opt_step = new_step
                    opt_shift = abs(direct.ort()) * step_width
                if self.__is_detect(opt_step):
                    break
            if self.__is_detect(opt_step):
                shift += opt_shift if shift.x == 0 and opt_shift.x != 0 else Point(0, 0)
                shift += opt_shift if shift.y == 0 and opt_shift.y != 0 else Point(0, 0)
            opt_direct_steps.append(opt_step)
        detected_directs = [self.__is_detect(opt_step) for opt_step in opt_direct_steps]
        return detected_directs, shift

    def set_components(self, components):
        self.components = components

    def set_labels(self, labels):
        self.labels = labels

    def detect(self, start):
        detected_directs, shift = self.__detect_directs(start)
        count_directs = np.sum(np.uint8(detected_directs))
        if count_directs > 2:
            return True, shift
        if count_directs < 2:
            return False, shift
        is_cross = sum(map(lambda arg: arg[0] ^ arg[1], zip(detected_directs, self.the_same_directs))) == 2
        return is_cross, shift
