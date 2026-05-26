import time
import numpy as np
from abc import ABC, abstractmethod

from common.controller_scale import ScaleProxy


class TouchController(ABC):
    @abstractmethod
    def connect(self, serial):
        ...

    @abstractmethod
    def click(self, x, y):
        ...

    @abstractmethod
    def double_click(self, x, y):
        ...

    @abstractmethod
    def long_click(self, x, y, duration=2):
        ...

    @abstractmethod
    def swipe(self, fx, fy, tx, ty, duration=None):
        ...

    @abstractmethod
    def pinch_in(self, x, y, distance, duration=0.3):
        ...

    @abstractmethod
    def press(self, key):
        ...

    @abstractmethod
    def screenshot(self):
        ...

    @abstractmethod
    def app_start(self, package, activity=None):
        ...

    @abstractmethod
    def app_stop(self, package):
        ...

    @abstractmethod
    def app_current(self):
        ...

    @abstractmethod
    def app_list_running(self):
        ...

    @abstractmethod
    def push(self, src, dst):
        ...

    @property
    @abstractmethod
    def info(self):
        ...

    @property
    @abstractmethod
    def device_info(self):
        ...


class Controller:
    REF_WIDTH = 1280
    REF_HEIGHT = 720

    def __init__(self, backend):
        self.backend = backend
        self.scale_proxy = None
        self.logger = None

    def set_logger(self, logger):
        self.logger = logger
        if hasattr(self.backend, 'set_logger'):
            self.backend.set_logger(logger)

    def connect(self, serial):
        self.backend.connect(serial)

    def init_scale_proxy(self):
        raw_img = self.backend.screenshot()
        h, w = raw_img.shape[:2]
        if h > w:
            w, h = h, w
        if w < self.REF_WIDTH or h < self.REF_HEIGHT:
            raise RuntimeError(
                '模拟器分辨率至少为1280 x 720！当前分辨率为:{} x {}'.format(w, h))
        if abs(w / h - self.REF_WIDTH / self.REF_HEIGHT) > 0.05:
            raise RuntimeError(
                '模拟器分辨率必须为16:9比例！当前分辨率为:{} x {}'.format(w, h))
        self.scale_proxy = ScaleProxy(w, h)
        if hasattr(self.backend, 'set_screen_size'):
            self.backend.set_screen_size(w, h)
        if self.logger:
            self.logger.info('Controller init: %dx%d, view=%dx%d, scale=%.2fx%.2f',
                             w, h, self.scale_proxy.view_width,
                             self.scale_proxy.view_height,
                             self.scale_proxy.scale_x, self.scale_proxy.scale_y)
        return self.scale_proxy

    def _to_device(self, x, y):
        if self.scale_proxy is None:
            return (int(x), int(y))
        return self.scale_proxy.to_device(x, y)

    def click(self, x, y, wait=True, count=1, rate=0):
        if wait and hasattr(self, '_wait_loading'):
            self._wait_loading()
        dx, dy = self._to_device(x, y)
        for i in range(count):
            if self.logger:
                self.logger.info('click (%s,%s)', x, y)
            if rate > 0:
                time.sleep(rate)
            self.backend.click(dx, dy)

    def double_click(self, x, y, wait=True, count=1, rate=0):
        if wait and hasattr(self, '_wait_loading'):
            self._wait_loading()
        dx, dy = self._to_device(x, y)
        for i in range(count):
            if self.logger:
                self.logger.info('double_click (%s,%s)', x, y)
            if rate > 0:
                time.sleep(rate)
            self.backend.double_click(dx, dy)

    def long_click(self, x, y, duration=2):
        dx, dy = self._to_device(x, y)
        if self.logger:
            self.logger.info('long_click (%s,%s) duration:%s', x, y, duration)
        self.backend.long_click(dx, dy, duration)

    def swipe(self, fx, fy, tx, ty, duration=None):
        dfx, dfy = self._to_device(fx, fy)
        dtx, dty = self._to_device(tx, ty)
        if self.logger:
            self.logger.info('swipe %s %s %s %s duration:%s', fx, fy, tx, ty, duration)
        self.backend.swipe(dfx, dfy, dtx, dty, duration=duration)

    def pinch_in(self, x, y, distance, duration=0.3):
        dx, dy = self._to_device(x, y)
        dd = int(distance * self.scale_proxy.scale_x) if self.scale_proxy else distance
        if self.logger:
            self.logger.info('pinch_in (%s,%s) distance:%s duration:%s', x, y, distance, duration)
        self.backend.pinch_in(dx, dy, dd, duration)

    def press(self, key):
        if self.logger:
            self.logger.info('press %s', key)
        self.backend.press(key)

    def screenshot(self, raw=False):
        img = self.backend.screenshot()
        if raw or self.scale_proxy is None:
            return img
        return self.scale_proxy.resize_screenshot(img)

    def app_start(self, package, activity=None):
        self.backend.app_start(package, activity)

    def app_stop(self, package):
        self.backend.app_stop(package)

    def app_current(self):
        return self.backend.app_current()

    def app_list_running(self):
        return self.backend.app_list_running()

    def push(self, src, dst):
        self.backend.push(src, dst)

    @property
    def info(self):
        return self.backend.info

    @property
    def device_info(self):
        return self.backend.device_info


def create_controller(controller_type='u2'):
    if controller_type == 'adb':
        from common.controller_adb import AdbController
        return Controller(AdbController())
    elif controller_type == 'minitouch':
        from common.controller_minitouch import MinitouchController
        return Controller(MinitouchController())
    elif controller_type == 'maatouch':
        from common.controller_maatouch import MaatouchController
        return Controller(MaatouchController())
    else:
        from common.controller_u2 import U2Controller
        return Controller(U2Controller())
