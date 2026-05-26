import subprocess

import cv2
import numpy as np

from common.controller import TouchController


def _get_adb_path():
    try:
        import adbutils
        return adbutils.adb_path()
    except Exception:
        return 'adb'


class AdbController(TouchController):
    def __init__(self):
        self._serial = ''
        self._adb_path = _get_adb_path()
        self._adb_device = None
        self.logger = None

    def _get_adb_device(self):
        if self._adb_device is None and self._serial:
            import adbutils
            self._adb_device = adbutils.adb.device(self._serial)
        return self._adb_device

    def set_logger(self, logger):
        self.logger = logger

    def connect(self, serial):
        self._serial = serial
        subprocess.run(
            ['adb', '-s', serial, 'wait-for-device'],
            capture_output=True, timeout=10
        )

    def _adb(self, *args, timeout=10):
        cmd = [self._adb_path, '-s', self._serial] + list(args)
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
        if result.returncode != 0:
            stderr = result.stderr.decode(errors='replace').strip()
            if stderr and self.logger:
                self.logger.warning('adb error: %s', stderr)
        return result

    def click(self, x, y):
        self._adb('shell', 'input', 'tap', str(x), str(y))

    def double_click(self, x, y):
        self.click(x, y)
        self.click(x, y)

    def long_click(self, x, y, duration=2):
        self._adb('shell', 'input', 'swipe', str(x), str(y), str(x), str(y),
                  str(int(duration * 1000)))

    def swipe(self, fx, fy, tx, ty, duration=None):
        ms = int((duration or 0.5) * 1000)
        self._adb('shell', 'input', 'swipe',
                  str(fx), str(fy), str(tx), str(ty), str(ms))

    def pinch_in(self, x, y, distance, duration=0.3):
        x1, y1 = x - distance, y
        x2, y2 = x + distance, y
        self.swipe(x1, y1, x, y, duration=duration / 2)
        self.swipe(x2, y2, x, y, duration=duration / 2)

    def press(self, key):
        self._adb('shell', 'input', 'keyevent', self._keycode(key))

    def _keycode(self, key):
        codes = {'home': '3', 'back': '4', 'menu': '82',
                 'enter': '66', 'delete': '67',
                 'volume_up': '24', 'volume_down': '25'}
        return codes.get(key, key)

    def screenshot(self):
        result = self._adb('exec-out', 'screencap', '-p', timeout=15)
        img_array = np.frombuffer(result.stdout, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        h, w = img.shape[:2]
        if h > w:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        return img

    def app_start(self, package, activity=None):
        if activity:
            self._adb('shell', 'am', 'start', '-n', f'{package}/{activity}')
        else:
            self._adb('shell', 'monkey', '-p', package, '-c',
                      'android.intent.category.LAUNCHER', '1')

    def app_stop(self, package):
        self._adb('shell', 'am', 'force-stop', package)

    def app_current(self):
        try:
            d = self._get_adb_device()
            if d:
                app = d.app_current()
                return {'package': app.package, 'activity': app.activity}
        except Exception:
            pass
        return {'package': '', 'activity': ''}

    def app_list_running(self):
        try:
            d = self._get_adb_device()
            if d:
                return d.list_packages()
        except Exception:
            pass
        return []

    def push(self, src, dst):
        self._adb('push', src, dst, timeout=30)

    @property
    def info(self):
        return {}

    @property
    def device_info(self):
        return {'serial': self._serial}
