import os
import socket
import subprocess
import sys
import time

import cv2
import numpy as np

from common.controller import TouchController


def _get_adb_path():
    try:
        import adbutils
        return adbutils.adb_path()
    except Exception:
        return 'adb'


def _get_resource_dir():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', 'minitouch')
    return os.path.join(os.path.dirname(__file__), '..', 'assets', 'minitouch')


class MinitouchController(TouchController):
    MINITOUCH_PATH = '/data/local/tmp/minitouch'
    MINITOUCH_PORT = 1311
    MINITOUCH_SOCKET = 'localabstract:minitouch'
    DEFAULT_SWIPE_DURATION = 200
    SWIPE_INTERVAL = 16
    SWIPE_SLOPE_IN = 1.0
    SWIPE_SLOPE_OUT = 1.0
    ABI_PROBE_ORDER = ['x86_64', 'x86', 'arm64-v8a', 'armeabi-v7a', 'armeabi']

    def __init__(self, resource_dir=None):
        self._serial = ''
        self._sock = None
        self._max_x = 0
        self._max_y = 0
        self._max_pressure = 50
        self.logger = None
        self._adb_path = _get_adb_path()
        self._adb_device = None
        self._resource_dir = resource_dir or _get_resource_dir()
        self._input_scale_x = 1.0
        self._input_scale_y = 1.0

    def set_logger(self, logger):
        self.logger = logger

    def set_screen_size(self, width, height):
        if self._max_x > 0 and width > 0:
            self._input_scale_x = self._max_x / width
        if self._max_y > 0 and height > 0:
            self._input_scale_y = self._max_y / height
        if self.logger:
            self.logger.info('minitouch input scale: %.3fx%.3f (max=%dx%d screen=%dx%d)',
                             self._input_scale_x, self._input_scale_y,
                             self._max_x, self._max_y, width, height)

    def _get_adb_device(self):
        if self._adb_device is None and self._serial:
            import adbutils
            self._adb_device = adbutils.adb.device(self._serial)
        return self._adb_device

    def connect(self, serial):
        self._serial = serial
        self._push_minitouch()
        self._start_minitouch()

    def _adb(self, *args, timeout=10):
        cmd = [self._adb_path, '-s', self._serial] + list(args)
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
        if result.returncode != 0 and self.logger:
            stderr = result.stderr.decode(errors='replace').strip()
            if stderr:
                self.logger.warning('adb error: %s', stderr)
        return result

    def _push_minitouch(self):
        if self.logger:
            self.logger.info('pushing minitouch binary...')

        result = self._adb('shell', 'test', '-x', self.MINITOUCH_PATH, timeout=5)
        if result.returncode == 0:
            if self.logger:
                self.logger.info('minitouch binary already exists on device')
            return

        device_abi = self._detect_abi()
        if self.logger:
            self.logger.info('device ABI: %s', device_abi)

        candidates = [device_abi] if device_abi else []
        candidates += [a for a in self.ABI_PROBE_ORDER if a not in candidates]

        for abi in candidates:
            local_path = os.path.join(self._resource_dir, abi, 'minitouch')
            if self.logger:
                self.logger.info('trying: %s', local_path)
            if not os.path.isfile(local_path):
                continue

            result = self._adb('push', local_path, self.MINITOUCH_PATH, timeout=30)
            if result.returncode != 0:
                continue

            self._adb('shell', 'chmod', '755', self.MINITOUCH_PATH, timeout=5)
            verify = self._adb('shell', 'test', '-x', self.MINITOUCH_PATH, timeout=5)
            if verify.returncode == 0:
                if self.logger:
                    self.logger.info('minitouch binary pushed successfully (%s)', abi)
                return

        raise RuntimeError(
            'Failed to push minitouch binary.\n'
            'Download minitouch for your device ABI from:\n'
            '  https://github.com/openstf/minitouch/releases\n'
            'Place the binary at: {}/{}/\n'
            'Detected ABI: {}'.format(
                self._resource_dir, '<abi>', device_abi or 'unknown'))

    def _detect_abi(self):
        result = self._adb('shell', 'getprop', 'ro.product.cpu.abi', timeout=5)
        if result.returncode == 0:
            abi = result.stdout.decode(errors='replace').strip()
            if abi:
                return abi
        result = self._adb('shell', 'getprop', 'ro.product.cpu.abi2', timeout=5)
        if result.returncode == 0:
            abi2 = result.stdout.decode(errors='replace').strip()
            if abi2:
                return abi2
        return ''

    def _start_minitouch(self):
        self.close()
        if self.logger:
            self.logger.info('starting minitouch daemon...')
        self._adb('shell', 'pkill', '-f', 'minitouch', timeout=5)
        time.sleep(0.5)
        self._adb('shell',
                  'nohup {0} > /dev/null 2>&1 &'.format(self.MINITOUCH_PATH),
                  timeout=5)
        time.sleep(0.5)
        self._adb('forward', '--remove',
                  'tcp:{0}'.format(self.MINITOUCH_PORT), timeout=5)
        self._adb('forward',
                  'tcp:{0}'.format(self.MINITOUCH_PORT),
                  self.MINITOUCH_SOCKET, timeout=5)
        time.sleep(0.2)
        self._sock = socket.create_connection(
            ('127.0.0.1', self.MINITOUCH_PORT), timeout=5)
        self._read_version_from_socket()

    def _read_version_from_socket(self):
        if not self._sock:
            return
        self._sock.settimeout(2.0)
        data = b''
        try:
            while b'^ ' not in data and b'\n^ ' not in data:
                chunk = self._sock.recv(1024)
                if not chunk:
                    break
                data += chunk
        except socket.timeout:
            pass
        text = data.decode(errors='replace')
        if self.logger:
            self.logger.info('minitouch: %s', text.replace('\n', ' ').strip())
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('^'):
                self._parse_version_line(line)

    def _parse_version_line(self, line):
        parts = line.split()
        if len(parts) >= 5 and parts[0] == '^':
            size_1 = int(parts[2])
            size_2 = int(parts[3])
            self._max_x = max(size_1, size_2)
            self._max_y = min(size_1, size_2)
            self._max_pressure = int(parts[4])
            if self._max_pressure <= 0:
                self._max_pressure = 50
            return True
        return False

    def _send(self, cmd):
        try:
            if self._sock:
                self._sock.sendall(cmd.encode())
        except (socket.error, OSError) as e:
            if self.logger:
                self.logger.warning('minitouch socket error: %s, restarting...', e)
            self._restart()

    def _restart(self):
        self._start_minitouch()
        if self.logger:
            self.logger.info('minitouch restarted')

    def _input_xy(self, x, y):
        return (int(x * self._input_scale_x), int(y * self._input_scale_y))

    def click(self, x, y):
        ix, iy = self._input_xy(x, y)
        self._touch_down(0, ix, iy, self._max_pressure)
        self._commit()
        time.sleep(0.05)
        self._touch_up(0)
        self._commit()

    def double_click(self, x, y):
        self.click(x, y)
        time.sleep(0.05)
        self.click(x, y)

    def long_click(self, x, y, duration=2):
        ix, iy = self._input_xy(x, y)
        self._touch_down(0, ix, iy, self._max_pressure)
        self._commit()
        time.sleep(duration)
        self._touch_up(0)
        self._commit()

    def swipe(self, fx, fy, tx, ty, duration=None):
        dur_ms = int((duration or 0) * 1000) if duration else self.DEFAULT_SWIPE_DURATION
        if dur_ms <= 0:
            dur_ms = self.DEFAULT_SWIPE_DURATION

        ifx, ify = self._input_xy(fx, fy)
        itx, ity = self._input_xy(tx, ty)
        self._touch_down(0, ifx, ify, self._max_pressure)
        self._commit()

        steps = max(1, dur_ms // self.SWIPE_INTERVAL)
        for i in range(1, steps + 1):
            t = i / steps
            ease = self._cubic_ease(t)
            cx = int(ifx + (itx - ifx) * ease)
            cy = int(ify + (ity - ify) * ease)
            self._touch_move(0, cx, cy, self._max_pressure)
            self._commit()
            time.sleep(self.SWIPE_INTERVAL / 1000.0)

        self._touch_move(0, itx, ity, self._max_pressure)
        self._commit()
        time.sleep(0.05)

        self._touch_up(0)
        self._commit()

    def pinch_in(self, x, y, distance, duration=0.3):
        steps = max(1, int(duration * 60))
        ix, iy = self._input_xy(x, y)
        idist = int(distance * self._input_scale_x)
        x1, y1 = ix - idist, iy
        x2, y2 = ix + idist, iy
        self._touch_down(0, x1, y1, self._max_pressure)
        self._touch_down(1, x2, y2, self._max_pressure)
        self._commit()
        for i in range(1, steps + 1):
            t = i / steps
            self._touch_move(0, int(x1 + idist * t), iy, self._max_pressure)
            self._touch_move(1, int(x2 - idist * t), iy, self._max_pressure)
            self._commit()
            time.sleep(duration / steps)
        self._touch_up(0)
        self._touch_up(1)
        self._commit()

    def _cubic_ease(self, t):
        if t <= 0:
            return 0.0
        if t >= 1:
            return 1.0
        p0 = 0.0
        p1 = self.SWIPE_SLOPE_IN
        p2 = self.SWIPE_SLOPE_OUT
        p3 = 1.0
        t2 = t * t
        t3 = t2 * t
        return (p0 * (2 * t3 - 3 * t2 + 1)
                + p1 * (t3 - 2 * t2 + t)
                + p2 * (t3 - t2)
                + p3 * (-2 * t3 + 3 * t2))

    def _touch_down(self, contact, x, y, pressure):
        self._send(f'd {contact} {x} {y} {pressure}\n')

    def _touch_move(self, contact, x, y, pressure):
        self._send(f'm {contact} {x} {y} {pressure}\n')

    def _touch_up(self, contact):
        self._send(f'u {contact}\n')

    def _commit(self):
        self._send('c\n')

    def press(self, key):
        keycodes = {'home': '3', 'back': '4', 'menu': '82',
                    'enter': '66', 'delete': '67',
                    'volume_up': '24', 'volume_down': '25'}
        kc = keycodes.get(key, key)
        self._adb('shell', 'input', 'keyevent', kc, timeout=5)

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

    def close(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
        self._adb('forward', '--remove',
                  'tcp:{0}'.format(self.MINITOUCH_PORT), timeout=5)
