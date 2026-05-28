import ctypes
import ctypes.wintypes
import threading

from PySide6.QtCore import Qt, QObject, QEvent, QPoint, Signal, QSize, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QColor
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QLabel, QApplication, QDialog, QCheckBox, QSystemTrayIcon, QMenu, QSplitter, QSplitterHandle

from common import app as app_module, config as app_config, process
from common.app import load_theme, save_theme, load_close_action, save_close_action
from gui.sidebar import Sidebar, DASHBOARD_FN, HOME_FN, HELP_FN, CONFIG_MGMT_FN
from gui.config_panel import ConfigPanel
from gui.dashboard_widget import DashboardWidget
from gui.home_widget import HomeWidget
from gui.styles import LIGHT_STYLE, DARK_STYLE
from gui.release_dialog import show_release
from modules.baas import bemfa

_SIDEBAR_DEFAULT = 240
_BORDER = 6


class _SidebarHandle(QSplitterHandle):
    """侧边栏 QSplitter 分隔把手：左拖收起，右拖展开；收起时点击把手还原。"""

    _ICON_SIZE = 10

    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.SizeHorCursor)
        self._pix_light = None
        self._pix_dark = None

    def _collapsed(self) -> bool:
        return self.splitter().sizes()[0] == 0

    def _dark(self) -> bool:
        return getattr(self.window(), '_dark_mode', False)

    def _arrow_pix(self, dark: bool) -> QPixmap:
        if dark:
            if self._pix_dark is not None:
                return self._pix_dark
            p = QPixmap(app_config.resource_path('assets/icon_white/right.png'))
            p = p.scaled(
                self._ICON_SIZE,
                self._ICON_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self._pix_dark = p
            return self._pix_dark
        else:
            if self._pix_light is not None:
                return self._pix_light
            p = QPixmap(app_config.resource_path('assets/icon/right.svg'))
            p = p.scaled(
                self._ICON_SIZE,
                self._ICON_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self._pix_light = p
            return self._pix_light

    def enterEvent(self, event):
        self.setCursor(
            Qt.PointingHandCursor if self._collapsed() else Qt.SizeHorCursor
        )
        super().enterEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._collapsed():
            sp = self.splitter()
            total = sum(sp.sizes())
            sp.setSizes([_SIDEBAR_DEFAULT, total - _SIDEBAR_DEFAULT])
            return
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        w = self.width()
        h = self.height()
        dark = self._dark()
        line_color = QColor('#3d4a4e') if dark else QColor('#dfe6e9')
        painter.fillRect(0, 0, 1, h, line_color)

        if self._collapsed():
            pix = self._arrow_pix(dark)
            if not pix.isNull():
                y = (h - pix.height()) // 2
                painter.drawPixmap(2, y, pix)


class _SidebarSplitter(QSplitter):

    def createHandle(self):
        return _SidebarHandle(self.orientation(), self)




class _BtnCursorFilter(QObject):

    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton):
            if event.type() == QEvent.Type.Enter:
                if obj.isEnabled():
                    obj.setCursor(Qt.PointingHandCursor)
            elif event.type() == QEvent.Type.Leave:
                obj.unsetCursor()
        return False


class _TitleBar(QWidget):

    def __init__(self, window: QMainWindow, parent=None):
        super().__init__(parent or window)
        self._window = window
        self._drag_pos = None
        self.setObjectName('title_bar')
        self.setFixedHeight(52)
        self.setCursor(Qt.ArrowCursor)

        hl = QHBoxLayout(self)
        hl.setContentsMargins(10, 4, 12, 4)
        hl.setSpacing(0)

        icon_lbl = QLabel()
        icon_lbl.setObjectName('title_icon')
        icon_lbl.setFixedSize(24, 24)
        icon_lbl.setAlignment(Qt.AlignCenter)
        _ico_pix = QPixmap(app_config.resource_path('assets/images/common/ba.ico'))
        if not _ico_pix.isNull():
            _sz = 22
            _src = _ico_pix.scaled(
                _sz, _sz,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            _rounded = QPixmap(_sz, _sz)
            _rounded.fill(Qt.transparent)
            _p = QPainter(_rounded)
            _p.setRenderHint(QPainter.Antialiasing)
            _path = QPainterPath()
            _path.addRoundedRect(0, 0, _sz, _sz, 5, 5)
            _p.setClipPath(_path)
            _p.drawPixmap(0, 0, _src)
            _p.end()
            icon_lbl.setPixmap(_rounded)
        hl.addWidget(icon_lbl)
        hl.addSpacing(8)

        app_lbl = QLabel(f'BAAS Pro  {app_module.version}')
        app_lbl.setObjectName('title_bar_label')
        hl.addWidget(app_lbl)

        self._sep_lbl = QLabel('  /  ')
        self._sep_lbl.setObjectName('title_bar_sep')
        self._sep_lbl.setVisible(False)
        hl.addWidget(self._sep_lbl)

        self._crumb_lbl = QLabel()
        self._crumb_lbl.setObjectName('title_bar_crumb')
        self._crumb_lbl.setVisible(False)
        hl.addWidget(self._crumb_lbl)

        hl.addStretch()
        hl.addSpacing(8)

        _icon_size = QSize(16, 16)

        def _icon(name):
            return QIcon(QPixmap(app_config.resource_path(f'assets/icon/{name}.png')))

        self._min_btn = QPushButton()
        self._min_btn.setObjectName('wc_min')
        self._min_btn.setFixedSize(38, 38)
        self._min_btn.setIcon(_icon('min'))
        self._min_btn.setIconSize(_icon_size)
        self._min_btn.setCursor(Qt.PointingHandCursor)
        self._min_btn.clicked.connect(window.showMinimized)
        min_btn = self._min_btn

        self._max_btn = QPushButton()
        self._max_btn.setObjectName('wc_max')
        self._max_btn.setFixedSize(38, 38)
        self._max_btn.setIcon(_icon('max'))
        self._max_btn.setIconSize(_icon_size)
        self._max_btn.setCursor(Qt.PointingHandCursor)
        self._max_btn.clicked.connect(self._toggle_max)

        self._close_btn = QPushButton()
        self._close_btn.setObjectName('wc_close')
        self._close_btn.setFixedSize(38, 38)
        self._close_btn.setIcon(_icon('close'))
        self._close_btn.setIconSize(_icon_size)
        self._close_btn.setCursor(Qt.PointingHandCursor)
        self._close_btn.clicked.connect(window.close)
        close_btn = self._close_btn

        hl.addSpacing(4)
        hl.addWidget(min_btn, alignment=Qt.AlignVCenter)
        hl.addSpacing(16)
        hl.addWidget(self._max_btn, alignment=Qt.AlignVCenter)
        hl.addSpacing(16)
        hl.addWidget(close_btn, alignment=Qt.AlignVCenter)

    def set_theme(self, dark: bool):
        base = 'assets/icon_white' if dark else 'assets/icon'
        _icon_size = QSize(16, 16)

        def _icon(name):
            return QIcon(QPixmap(app_config.resource_path(f'{base}/{name}.png')))

        self._min_btn.setIcon(_icon('min'))
        self._min_btn.setIconSize(_icon_size)
        self._max_btn.setIcon(_icon('max'))
        self._max_btn.setIconSize(_icon_size)
        self._close_btn.setIcon(_icon('close'))
        self._close_btn.setIconSize(_icon_size)

    def set_breadcrumb(self, text: str):
        if text:
            self._crumb_lbl.setText(text)
            self._crumb_lbl.setVisible(True)
            self._sep_lbl.setVisible(True)
        else:
            self._crumb_lbl.setVisible(False)
            self._sep_lbl.setVisible(False)

    def _toggle_max(self):
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            if self._window.isMaximized():
                self._window.showNormal()
                self._drag_pos = QPoint(self._window.width() // 2, 21)
            self._window.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._toggle_max()
        super().mouseDoubleClickEvent(event)


class MainWindow(QMainWindow):

    def __init__(self, migrate_errors=None):
        super().__init__()
        self._migrate_errors = migrate_errors or []
        self.setWindowTitle(f'BAAS Pro  {app_module.version}')
        self.setWindowIcon(QIcon(app_config.resource_path('assets/images/common/ba.ico')))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self._dark_mode = load_theme()
        self._btn_filter = _BtnCursorFilter(self)
        QApplication.instance().installEventFilter(self._btn_filter)
        self._geo_save_timer = QTimer(self)
        self._geo_save_timer.setSingleShot(True)
        self._geo_save_timer.setInterval(500)
        self._geo_save_timer.timeout.connect(self._save_geometry_now)
        self._setup_ui()
        self._setup_tray()
        self._apply_theme()
        self._restore_geometry()
        self._startup()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._title_bar = _TitleBar(self)
        root.addWidget(self._title_bar)

        self._splitter = _SidebarSplitter(Qt.Horizontal)
        self._splitter.setContentsMargins(0, 0, 0, 0)
        self._splitter.setHandleWidth(10)
        root.addWidget(self._splitter)

        self._sidebar = Sidebar()
        self._sidebar.setMinimumWidth(0)
        self._splitter.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        self._home_widget = HomeWidget()
        self._dashboard = DashboardWidget()
        self._config_panel = ConfigPanel()
        self._stack.addWidget(self._home_widget)
        self._stack.addWidget(self._dashboard)
        self._stack.addWidget(self._config_panel)
        self._splitter.addWidget(self._stack)

        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setCollapsible(0, True)
        self._splitter.setCollapsible(1, False)
        self._splitter.setSizes([_SIDEBAR_DEFAULT, 10000])
        self._splitter.splitterMoved.connect(self._on_splitter_moved)

        self._sidebar.menu_selected.connect(self._on_menu)
        self._dashboard.config_requested.connect(self._on_menu)
        self._dashboard.theme_toggle.connect(self._toggle_theme)
        self._home_widget.theme_set.connect(self._set_theme)
        self._home_widget.release_requested.connect(lambda: show_release(self))
        self._home_widget.configs_changed.connect(self._on_configs_changed)
        self._home_widget.reset_requested.connect(self._on_reset_geometry)

    def _restore_geometry(self):
        geo = app_module.load_geometry()
        if geo:
            self.resize(geo.get('w', 1280), geo.get('h', 800))
            self.move(geo.get('x', 100), geo.get('y', 100))
        else:
            self.resize(1280, 800)

    def _check_migrate_errors(self, errors):
        dlg = QDialog(self)
        dlg.setWindowTitle('配置文件迁移异常')
        dlg.setFixedWidth(400)
        dlg.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(12)

        title_lbl = QLabel('以下配置文件迁移失败')
        title_lbl.setStyleSheet('font-size: 15px; font-weight: bold;')
        layout.addWidget(title_lbl)

        desc_lbl = QLabel('请修复或删除对应文件后重启应用：')
        desc_lbl.setStyleSheet('font-size: 13px; color: gray;')
        layout.addWidget(desc_lbl)

        for con in errors:
            row = QLabel(f'• configs/{con}.json')
            row.setStyleSheet('font-size: 13px; padding: 2px 0;')
            layout.addWidget(row)

        layout.addSpacing(4)
        btn = QPushButton('知道了')
        btn.setFixedHeight(34)
        btn.setStyleSheet('background:#0984e3; color:white; border:none; border-radius:4px; padding:6px 18px; font-size:14px;')
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)

        dlg.exec()

    def _startup(self):
        auto_start = app_module.load_auto_start()
        for con in auto_start:
            try:
                process.m.start_process(con)
            except PermissionError:
                pass

        # 在后台线程启动巴法云远程控制（避免阻塞 Qt 事件循环）
        threading.Thread(
            target=self._init_bemfa,
            daemon=True,
            name='bemfa-init'
        ).start()

        target = auto_start[0] if auto_start else self._sidebar.first_account()
        if target:
            self._show_dashboard(target)
            self._sidebar.select_dashboard(target)
            self._title_bar.set_breadcrumb(f'{target}  /  总览')
        else:
            self._sidebar.select_home()

    def _init_bemfa(self):
        """后台线程：初始化巴法云管理器（不阻塞 UI）。"""
        try:
            bemfa.init_manager()
        except Exception:
            pass

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_win_style()
        self._apply_rounded_corners()
        if self._migrate_errors:
            errors = self._migrate_errors
            self._migrate_errors = []
            QTimer.singleShot(300, lambda: self._check_migrate_errors(errors))

    def _apply_win_style(self):
        try:
            hwnd = int(self.winId())
            GWL_STYLE = -16
            WS_THICKFRAME = 262144
            WS_CAPTION = 12582912
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style | WS_THICKFRAME | WS_CAPTION)
            ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 39)
        except Exception:
            pass

    def _toggle_theme(self):
        self._dark_mode = not self._dark_mode
        save_theme(self._dark_mode)
        self._apply_theme()

    def _set_theme(self, dark: bool):
        if self._dark_mode != dark:
            self._dark_mode = dark
            save_theme(self._dark_mode)
            self._apply_theme()

    def _apply_theme(self):
        self.setStyleSheet(DARK_STYLE if self._dark_mode else LIGHT_STYLE)
        self._sidebar.set_theme(self._dark_mode)
        self._title_bar.set_theme(self._dark_mode)
        self._dashboard.update_theme_icon(self._dark_mode)
        self._home_widget.update_theme_icon(self._dark_mode)

    def _apply_rounded_corners(self):
        try:
            hwnd = int(self.winId())
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
                4,
            )

            class MARGINS(ctypes.Structure):
                _fields_ = [
                    ('cxLeftWidth', ctypes.c_int),
                    ('cxRightWidth', ctypes.c_int),
                    ('cyTopHeight', ctypes.c_int),
                    ('cyBottomHeight', ctypes.c_int),
                ]

            ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(
                hwnd, ctypes.byref(MARGINS(1, 1, 1, 1))
            )
        except Exception:
            pass

    def _on_configs_changed(self):
        self._sidebar.refresh_accounts()
        # 配置变更后刷新巴法云连接映射
        try:
            bemfa.reload_manager()
        except Exception:
            pass

    def moveEvent(self, event):
        super().moveEvent(event)
        if not self.isMaximized():
            self._geo_save_timer.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.isMaximized():
            self._geo_save_timer.start()

    def _save_geometry_now(self):
        if not self.isMaximized():
            geo = self.geometry()
            app_module.save_geometry(geo.x(), geo.y(), geo.width(), geo.height())

    def _on_reset_geometry(self):
        self.showNormal()
        self.resize(1280, 800)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width() - 1280) // 2, (screen.height() - 800) // 2)

    def _on_menu(self, con: str, fn: str):
        if fn in (HOME_FN, HELP_FN, CONFIG_MGMT_FN):
            self._dashboard.stop()
            self._stack.setCurrentIndex(0)
            tab_idx = {
                HOME_FN: 0,
                HELP_FN: 1,
                CONFIG_MGMT_FN: 2,
            }[fn]
            self._home_widget.set_tab(tab_idx)
            crumb = {
                HOME_FN: '主页',
                HELP_FN: '帮助教程',
                CONFIG_MGMT_FN: '配置管理',
            }[fn]
            self._title_bar.set_breadcrumb(crumb)
            return

        if fn == DASHBOARD_FN:
            self._show_dashboard(con)
            self._title_bar.set_breadcrumb(f'{con}  /  总览')
            return

        self._dashboard.stop()
        self._stack.setCurrentIndex(2)
        self._config_panel.load(con, fn)
        self._sidebar.select_menu(fn)
        from gui.sidebar import FN_NAMES
        fn_display = FN_NAMES.get(fn, fn)
        self._title_bar.set_breadcrumb(f'{con}  /  {fn_display}')

    def _on_splitter_moved(self):
        self._splitter.handle(1).update()

    def _show_dashboard(self, con: str):
        self._stack.setCurrentIndex(1)
        self._dashboard.set_account(con)

    def nativeEvent(self, event_type, message):
        if event_type == b'windows_generic_MSG':
            try:
                msg = ctypes.wintypes.MSG.from_address(int(message))
                if msg.message == 131 and msg.wParam:
                    return True, 0
                if msg.message == 132:
                    x = ctypes.c_short(msg.lParam & 65535).value
                    y = ctypes.c_short((msg.lParam >> 16) & 65535).value
                    rect = ctypes.wintypes.RECT()
                    ctypes.windll.user32.GetWindowRect(int(self.winId()), ctypes.byref(rect))
                    b = max(4, round(_BORDER * self.devicePixelRatio()))
                    on_l = x < rect.left + b
                    on_r = x > rect.right - b
                    on_t = y < rect.top + b
                    on_b = y > rect.bottom - b
                    if on_t and on_l:
                        return True, 13
                    if on_t and on_r:
                        return True, 14
                    if on_b and on_l:
                        return True, 16
                    if on_b and on_r:
                        return True, 17
                    if on_l:
                        return True, 10
                    if on_r:
                        return True, 11
                    if on_t:
                        return True, 12
                    if on_b:
                        return True, 15
            except Exception:
                pass
        return super().nativeEvent(event_type, message)

    def _setup_tray(self):
        icon = QIcon(app_config.resource_path('assets/images/common/ba.ico'))
        self._tray = QSystemTrayIcon(icon, self)
        self._tray.setToolTip('BAAS Pro')

        menu = QMenu()
        show_act = menu.addAction('显示窗口')
        menu.addSeparator()
        quit_act = menu.addAction('退出程序')
        show_act.triggered.connect(self._restore_from_tray)
        quit_act.triggered.connect(self._quit_app)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._restore_from_tray()

    def _restore_from_tray(self):
        self.showNormal()
        self.activateWindow()
        self._tray.hide()

    def _quit_app(self):
        self._do_close()
        QApplication.instance().quit()

    def _do_close(self):
        self._dashboard.stop()
        self._sidebar._timer.stop()

        # 停止巴法云远程控制
        try:
            bemfa.shutdown_manager()
        except Exception:
            pass

        if not self.isMaximized():
            geo = self.geometry()
            app_module.save_geometry(geo.x(), geo.y(), geo.width(), geo.height())
        else:
            app_module.clear_geometry()

        for proc in list(process.m.processes.values()):
            if proc.is_alive():
                proc.kill()

    def closeEvent(self, event):
        action = load_close_action()
        if action == 'tray':
            event.ignore()
            self.hide()
            self._tray.show()
            return

        if action == 'quit':
            self._do_close()
            event.accept()
            return

        dlg = QDialog(self)
        dlg.setWindowTitle('请选择关闭方式')
        dlg.setFixedSize(360, 140)
        vl = QVBoxLayout(dlg)
        vl.setSpacing(14)
        vl.setContentsMargins(20, 20, 20, 18)

        remember = QCheckBox('记住我的选择，下次不再询问')
        remember.setStyleSheet('font-size:12px;')
        remember.setCursor(Qt.PointingHandCursor)
        vl.addWidget(remember)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.addStretch()
        tray_btn = QPushButton('隐藏到托盘')
        quit_btn = QPushButton('退出程序')
        tray_btn.setStyleSheet('background:#0984e3; color:white; border:none; border-radius:4px;')
        quit_btn.setStyleSheet('background:#d63031; color:white; border:none; border-radius:4px;')
        for b in (tray_btn, quit_btn):
            b.setFixedSize(110, 32)
            b.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(tray_btn)
        btn_row.addWidget(quit_btn)
        vl.addLayout(btn_row)

        chosen = [None]

        def _pick(act):
            chosen[0] = act
            dlg.accept()

        tray_btn.clicked.connect(lambda: _pick('tray'))
        quit_btn.clicked.connect(lambda: _pick('quit'))

        dlg.exec()

        if chosen[0] is None:
            event.ignore()
            return

        if remember.isChecked():
            save_close_action(chosen[0])

        if chosen[0] == 'tray':
            event.ignore()
            self.hide()
            self._tray.show()
        else:
            self._do_close()
            event.accept()
