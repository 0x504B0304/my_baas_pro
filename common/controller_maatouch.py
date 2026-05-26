import os
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


class MaatouchController(TouchController):
    MAATOUCH_PATH = '/data/local/tmp/maatouch'
    MAATOUCH_CLASS = 'com.shxyke.MaaTouch.App'
    DEFAULT_SWIPE_DURATION = 200
    SWIPE_INTERVAL = 16
    SWIPE_SLOPE_IN = 1.0
    SWIPE_SLOPE_OUT = 1.0

    def __init__(self, resource_dir=None):
        self._serial = ''
        self._proc = None
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
            self.logger.info('maatouch input scale: %.3fx%.3f (max=%dx%d screen=%dx%d)',
                             self._input_scale_x, self._input_scale_y,
                             self._max_x, self._max_y, width, height)

    def _get_adb_device(self):
        if self._adb_device is None and self._serial:
            import adbutils
            self._adb_device = adbutils.adb.device(self._serial)
        return self._adb_device

    def connect(self, serial):
        self._serial = serial
        self._push_maatouch()
        self._start_maatouch()

    def _adb(self, *args, timeout=10):
        cmd = [self._adb_path, '-s', self._serial] + list(args)
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
        if result.returncode != 0 and self.logger:
            stderr = result.stderr.decode(errors='replace').strip()
            if stderr:
                self.logger.warning('adb error: %s', stderr)
        return result

    def _push_maatouch(self):
        if self.logger:
            self.logger.info('pushing maatouch JAR...')

        result = self._adb('shell', 'test', '-f', self.MAATOUCH_PATH, timeout=5)
        if result.returncode == 0:
            if self.logger:
                self.logger.info('maatouch JAR already exists on device')
            return

        local_path = os.path.join(self._resource_dir, 'maatouch', 'minitouch')
        if not os.path.isfile(local_path):
            raise RuntimeError(
                'maatouch JAR not found at {}\n'
                'Copy MaaTouch JAR from MAA project: '
                'resource/minitouch/maatouch/minitouch'.format(local_path))

        result = self._adb('push', local_path, self.MAATOUCH_PATH, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(
                'Failed to push maatouch JAR to device. '
                'stderr: {}'.format(result.stderr.decode(errors='replace')))

        self._adb('shell', 'chmod', '755', self.MAATOUCH_PATH, timeout=5)
        verify = self._adb('shell', 'test', '-f', self.MAATOUCH_PATH, timeout=5)
        if verify.returncode != 0:
            raise RuntimeError('maatouch JAR push verification failed')

        if self.logger:
            self.logger.info('maatouch JAR pushed successfully')

    def _start_maatouch(self):
        if self.logger:
            self.logger.info('starting maatouch daemon...')
        self._adb('shell', 'pkill', '-f', self.MAATOUCH_CLASS, timeout=5)
        time.sleep(0.5)
        launch_cmd = (
            'export CLASSPATH=' + self.MAATOUCH_PATH + '; '
            'app_process /data/local/tmp ' + self.MAATOUCH_CLASS
        )
        self._proc = subprocess.Popen(
            [self._adb_path, '-s', self._serial, 'shell', launch_cmd],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self._read_version_from_stdout()

    def _read_version_from_stdout(self):
        if not self._proc or not self._proc.stdout:
            return
        start = time.time()
        while True:
            if time.time() - start > 5.0:
                if self.logger:
                    self.logger.warning('maatouch version read timeout')
                break
            line = self._readline_from_proc()
            if not line:
                time.sleep(0.01)
                continue
            if self.logger:
                self.logger.info('maatouch: %s', line)
            if self._parse_version_line(line):
                return

    def _readline_from_proc(self):
        line = ''
        try:
            while True:
                ch = self._proc.stdout.read(1)
                if not ch:
                    return line
                c = ch.decode(errors='replace')
                if c == '\n':
                    return line
                line += c
        except Exception:
            return line

    def _parse_version_line(self, line):
        parts = line.strip().split()
        if len(parts) >= 5 and parts[0] == '^':
            size_1 = int(parts[2])
            size_2 = int(parts[3])
            self._max_x = max(size_1, size_2)
            self._max_y = min(size_1, size_2)
            self._max_pressure = int(parts[4])
            return True
        return False

    def _send(self, cmd):
        try:
            if self._proc and self._proc.stdin:
                self._proc.stdin.write(cmd.encode())
                self._proc.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            if self.logger:
                self.logger.warning('maatouch PIPE write error: %s, restarting...', e)
            self._restart()

    def _restart(self):
        self.close()
        time.sleep(0.5)
        self._start_maatouch()
        if self.logger:
            self.logger.info('maatouch restarted')

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
        if self._proc:
            try:
                self._proc.stdin.close()
            except Exception:
                pass
            try:
                self._proc.terminate()
            except Exception:
                pass
            self._proc = None
