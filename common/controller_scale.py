import cv2
import numpy as np


class ScaleProxy:
    REF_WIDTH = 1280
    REF_HEIGHT = 720
    REF_RATIO = REF_WIDTH / REF_HEIGHT
    ASPECT_TOLERANCE = 0.05

    def __init__(self, raw_width, raw_height):
        self.raw_width = raw_width
        self.raw_height = raw_height
        self.scale_x = raw_width / self.REF_WIDTH
        self.scale_y = raw_height / self.REF_HEIGHT
        self.view_width, self.view_height = self._calc_view_size()

    def _calc_view_size(self):
        cur_ratio = self.raw_width / self.raw_height
        if cur_ratio >= self.REF_RATIO:
            scale_width = int(cur_ratio * self.REF_HEIGHT)
            return scale_width, self.REF_HEIGHT
        else:
            scale_height = int(self.REF_WIDTH / cur_ratio)
            return self.REF_WIDTH, scale_height

    def resize_screenshot(self, raw_img):
        return cv2.resize(raw_img, (self.view_width, self.view_height),
                          interpolation=cv2.INTER_AREA)

    def to_device(self, x, y):
        return (int(x * self.scale_x), int(y * self.scale_y))

    def is_identity(self):
        return self.raw_width == self.REF_WIDTH and self.raw_height == self.REF_HEIGHT
