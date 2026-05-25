from PySide6.QtCore import QTimer, Qt, QRectF, Signal, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from PySide6.QtWidgets import QWidget, QMessageBox


def show_permission_error(parent: str, msg: str):
    """弹出权限不足提示框，确认按钮为蓝色。"""
    box = QMessageBox(parent)
    box.setWindowTitle('权限不足')
    box.setText(msg)
    box.setIcon(QMessageBox.Icon.Critical)
    btn = box.addButton('确认', QMessageBox.ButtonRole.AcceptRole)
    btn.setStyleSheet(
        'QPushButton { background-color: #1677ff; color: white; border: none; border-radius: 4px; padding: 6px 20px; font-size: 13px; }'
        'QPushButton:hover { background-color: #4096ff; }'
        'QPushButton:pressed { background-color: #0958d9; }'
    )
    box.exec()


class SpinnerWidget(QWidget):
    """旋转进度圆圈，running=True 时动画，False 时隐藏。"""

    def __init__(self, size=14, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._running = False
        self._error = False
        self._size = size
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._tick)
        self.setFixedSize(size, size)

    def set_running(self, running: bool):
        if self._running == running:
            return
        self._running = running
        self._error = False
        if running:
            self._timer.start()
        else:
            self._timer.stop()
            self._angle = 0
        self.update()

    def set_error(self, error: bool):
        if self._error == error:
            return
        self._error = error
        self._running = False
        self._timer.stop()
        self._angle = 0
        self.update()

    def _tick(self):
        self._angle = (self._angle + 15) % 360
        self.update()

    def paintEvent(self, event):
        s = self._size
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(1, 1, s - 2, s - 2)
        if self._running:
            pen = QPen(QColor('#d0d0d0'), 2)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawEllipse(r)
            pen = QPen(QColor('#27ae60'), 2)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawArc(r, int((90 - self._angle) * 16), -1760)
        elif self._error:
            pen = QPen(QColor('#d63031'), 2)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            pad = self._size * 0.25
            p.drawLine(
                QRectF(pad, pad, self._size - pad * 2, self._size - pad * 2).topLeft(),
                QRectF(pad, pad, self._size - pad * 2, self._size - pad * 2).bottomRight(),
            )
            p.drawLine(
                QRectF(pad, pad, self._size - pad * 2, self._size - pad * 2).topRight(),
                QRectF(pad, pad, self._size - pad * 2, self._size - pad * 2).bottomLeft(),
            )
        else:
            pen = QPen(QColor('#b2bec3'), 2)
            p.setPen(pen)
            p.drawEllipse(r)
        p.end()


class ToggleSwitchWidget(QWidget):
    """滑动开关组件，类似 iOS/Android 样式。"""

    toggled = Signal(bool)

    _TRACK_W = 36
    _TRACK_H = 20
    _KNOB_R = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = False
        self._knob_x = float(self._KNOB_R + 2)
        self._anim_val = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(12)
        self._timer.timeout.connect(self._anim_tick)
        self._anim_dir = 0
        self.setFixedSize(self._TRACK_W + 2, self._TRACK_H + 2)
        self.setCursor(Qt.PointingHandCursor)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool):
        if self._checked == checked:
            return
        self._checked = checked
        self._anim_dir = 1 if checked else -1
        self._timer.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._checked = not self._checked
            self._anim_dir = 1 if self._checked else -1
            self._timer.start()
            self.toggled.emit(self._checked)
        super().mousePressEvent(event)

    def _anim_tick(self):
        step = 0.12
        self._anim_val = max(0.0, min(1.0, self._anim_val + self._anim_dir * step))
        if self._anim_val <= 0.0 or self._anim_val >= 1.0:
            self._timer.stop()
        self.update()

    def paintEvent(self, event):
        tw = self._TRACK_W
        th = self._TRACK_H
        kr = self._KNOB_R
        ox, oy = (1, 1)

        x_off = (tw - 2 - kr * 2) * self._anim_val
        knob_cx = ox + kr + 2 + x_off
        knob_cy = oy + th / 2

        t = self._anim_val
        r = int(178 + (-139) * t)
        g = int(190 + (-16) * t)
        b = int(195 + (-99) * t)
        track_color = QColor(r, g, b)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(track_color))
        p.drawRoundedRect(QRectF(ox, oy, tw, th), th / 2, th / 2)

        shadow_pen = QPen(QColor(0, 0, 0, 30), 1.5)
        p.setPen(shadow_pen)
        p.setBrush(QBrush(QColor('#ffffff')))
        p.drawEllipse(QRectF(knob_cx - kr, knob_cy - kr, kr * 2, kr * 2))

        p.end()
