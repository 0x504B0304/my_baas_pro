import time

import cv2
import numpy as np
import uiautomator2 as u2

from common.controller import TouchController


class U2Controller(TouchController):
    def __init__(self):
        self._d = None
        self.logger = None

    def set_logger(self, logger):
        self.logger = logger

    def connect(self, serial):
        self._d = u2.connect(serial)

    def click(self, x, y):
        self._d.click(x, y)

    def double_click(self, x, y):
        self._d.double_click(x, y)

    def long_click(self, x, y, duration=2):
        self._d.long_click(x, y, duration)

    def swipe(self, fx, fy, tx, ty, duration=None):
        self._d.swipe(fx, fy, tx, ty, duration=duration)

    def pinch_in(self, x, y, distance, duration=0.3):
        steps = max(1, int(duration * 60))
        x1, y1 = x - distance, y
        x2, y2 = x + distance, y
        self._d.touch.down(x1, y1, 0)
        self._d.touch.down(x2, y2, 1)
        for i in range(1, steps + 1):
            t = i / steps
            self._d.touch.move(int(x1 + distance * t), y1, 0)
            self._d.touch.move(int(x2 - distance * t), y2, 1)
            time.sleep(duration / steps)
        self._d.touch.move(x, y, 0)
        self._d.touch.move(x, y, 1)
        self._d.touch.up(0)
        self._d.touch.up(1)

    def press(self, key):
        self._d.press(key)

    def screenshot(self):
        img = cv2.cvtColor(
            np.array(self._d.screenshot()), cv2.COLOR_RGB2BGR
        )
        h, w = img.shape[:2]
        if h > w:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        return img

    def app_start(self, package, activity=None):
        self._d.app_start(package, activity)

    def app_stop(self, package):
        self._d.app_stop(package)

    def app_current(self):
        return self._d.app_current()

    def app_list_running(self):
        return self._d.app_list_running()

    def push(self, src, dst):
        self._d.push(src, dst)

    @property
    def info(self):
        return self._d.info

    @property
    def device_info(self):
        return self._d.device_info
