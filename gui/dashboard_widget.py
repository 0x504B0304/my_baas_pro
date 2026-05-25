import re
from datetime import datetime, timedelta

from PySide6.QtCore import QTimer, Qt, Signal, QRectF
from PySide6.QtGui import QTextCursor, QPainter, QPen, QColor, QTextCharFormat, QTextBlockFormat, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame, QScrollArea, QSizePolicy, QGroupBox

from common import config, process, app as app_module
from gui.widgets import SpinnerWidget, ToggleSwitchWidget, show_permission_error

_LEVEL_COLORS = {
    'INFO': '#27ae60',
    'ERROR': '#e74c3c',
    'CRITICAL': '#9b59b6',
    'WARNING': '#e67e22',
    'WARN': '#e67e22',
    'DEBUG': '#636e72',
}

_LOG_PLAIN_RE = re.compile(
    r'^(?:v[\d.]+\s+)?(INFO|ERROR|CRITICAL|WARNING|WARN|DEBUG)(\s+\d{2}-\d{2} \d{2}:\d{2}:\d{2}[^\S\r\n]*│?[^\S\r\n]*)',
    re.IGNORECASE,
)

TEXT_MAP = {
    'cn_activity': '国服-通用活动',
    'jp_activity': '日服-通用活动',
    'intl_activity': '国际服-通用活动',
}


def compute_schedule(con: str) -> dict:
    try:
        bc = config.load_ba_config(con)
    except Exception:
        return {'running': [], 'queue': [], 'waiting': [], 'closed': []}

    run_task = process.m.run_task(con)
    running = []
    queue = []
    waiting = []
    closed = []

    for ba_task, task_conf in bc.items():
        if ba_task == 'baas':
            continue
        if not (isinstance(task_conf, dict) and 'base' in task_conf):
            continue
        base = task_conf['base']

        text = TEXT_MAP.get(
            ba_task,
            base.get('text', ba_task),
        )
        next_str = base.get('next', '')
        end_str = base.get('end', '')

        try:
            if next_str:
                next_time = datetime.strptime(next_str, '%Y-%m-%d %H:%M:%S')
            else:
                next_time = datetime.now()
        except ValueError:
            next_time = datetime.now() - timedelta(days=1)

        try:
            if end_str:
                end_time = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
            else:
                end_time = datetime.now() + timedelta(days=1)
        except ValueError:
            end_time = datetime.now() + timedelta(days=1)

        task = {'task': ba_task, 'text': text, 'next': next_str, 'index': base.get('index', 0)}

        if run_task == ba_task:
            running.append(task)
            continue

        if not base.get('enable', False) and end_str != '' and end_time < datetime.now():
            closed.append(task)
            continue

        if next_time > datetime.now():
            waiting.append(task)
            continue

        queue.append(task)

    def _dt(t):
        if t['next']:
            return datetime.strptime(t['next'], '%Y-%m-%d %H:%M:%S')
        return datetime.now()

    waiting.sort(key=lambda t: (_dt(t), t['index']))
    queue.sort(key=lambda t: (t['index'], _dt(t)))

    return {'running': running, 'queue': queue, 'waiting': waiting, 'closed': closed}


def _fmt_remaining(next_str: str) -> str:
    try:
        secs = int(
            (datetime.strptime(next_str, '%Y-%m-%d %H:%M:%S') - datetime.now()).total_seconds()
        )
    except Exception:
        return ''

    if secs <= 0:
        return '即将运行'
    if secs >= 86400:
        return f'{secs // 86400}天后'
    if secs >= 3600:
        return f'{secs // 3600}h{secs % 3600 // 60}m后'
    if secs >= 60:
        return f'{secs // 60}m{secs % 60}s后'
    return f'{secs}s后'


_SpinnerWidget = SpinnerWidget

_HDR_COLORS = {
    'running': '#27ae60',
    'queue': '#0984e3',
    'waiting': '#e17055',
    'closed': '#95a5a6',
}

_BTN_COLORS = {
    'reset': '#e17055',
    'close': '#d63031',
    'open': '#00b894',
}


class _TaskPanel(QWidget):
    task_action = Signal(str, str)
    settings_requested = Signal(str)

    def __init__(self, state_key: str, title: str, row_actions: list, small: bool = False, parent=None):
        super().__init__(parent)
        self._state_key = state_key
        self._base_title = title
        self._row_actions = row_actions

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 6)
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName('task_card')
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 1)
        card_layout.setSpacing(0)

        color = _HDR_COLORS.get(state_key, '#636e72')
        hdr_bar = QWidget()
        hdr_bar.setFixedHeight(34)
        hdr_bar.setStyleSheet(f'background:{color}; border-radius:4px 4px 0 0;')

        hdr_hl = QHBoxLayout(hdr_bar)
        hdr_hl.setContentsMargins(14, 0, 14, 0)

        self._hdr = QLabel(title)
        self._hdr.setStyleSheet('color:white; font-weight:bold; font-size:14px; background:transparent;')

        hdr_hl.addWidget(self._hdr)
        hdr_hl.addStretch()

        card_layout.addWidget(hdr_bar)

        body_widget = QWidget()
        self._body_layout = QVBoxLayout(body_widget)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(0)

        self._empty_lbl = QLabel('无任务')
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._empty_lbl.setStyleSheet('color:#b2bec3; padding:12px; font-size:13px; background:transparent;')

        self._body_layout.addWidget(self._empty_lbl)
        self._body_layout.addStretch()

        body_scroll = QScrollArea()
        body_scroll.setWidgetResizable(True)
        body_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        body_scroll.setStyleSheet('QScrollArea { border: none; }')
        body_scroll.setWidget(body_widget)

        if small:
            body_scroll.setFixedHeight(68)
        else:
            body_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card_layout.addWidget(body_scroll)
        outer.addWidget(card)

    def update_tasks(self, tasks: list):
        while self._body_layout.count() > 2:
            item = self._body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._hdr.setText(f'{self._base_title}  ({len(tasks)})')
        self._empty_lbl.setVisible(len(tasks) == 0)

        for i, task in enumerate(tasks):
            self._body_layout.insertWidget(i, self._make_row(task))

    def _make_row(self, task: dict) -> QWidget:
        row = QWidget()
        row.setObjectName('task_row')
        row.setStyleSheet('#task_row { border-bottom:1px solid rgba(0,0,0,0.06); background:transparent; }')

        hl = QHBoxLayout(row)
        hl.setContentsMargins(14, 9, 10, 9)
        hl.setSpacing(6)

        info = QVBoxLayout()
        info.setSpacing(3)

        name = task.get('text') or task.get('task', '')
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet('font-size:14px; border:none; background:transparent;')
        name_lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        name_lbl.setMinimumWidth(0)
        info.addWidget(name_lbl)

        next_str = task.get('next', '')
        if next_str and self._state_key != 'closed':
            if self._state_key == 'waiting':
                ts_text = _fmt_remaining(next_str) or next_str
            else:
                ts_text = next_str

            ts_lbl = QLabel(ts_text)
            ts_lbl.setStyleSheet('font-size:12px; color:#95a5a6; border:none; background:transparent;')
            info.addWidget(ts_lbl)

        hl.addLayout(info, 1)

        task_key = task.get('task', '')

        _action_obj = {
            'close': 'action_close_btn',
            'open': 'action_open_btn',
            'reset': 'action_reset_btn',
        }

        for btn_label, action_key in self._row_actions:
            btn = QPushButton(btn_label)
            btn.setFixedSize(56, 24)
            btn.setObjectName(_action_obj.get(action_key, 'settings_shortcut_btn'))
            btn.clicked.connect(lambda checked=False, t=task_key, a=action_key: self.task_action.emit(t, a))
            hl.addWidget(btn)

        s_btn = QPushButton('设置')
        s_btn.setFixedSize(56, 24)
        s_btn.setObjectName('settings_shortcut_btn')
        s_btn.setToolTip('跳转到功能设置')
        s_btn.clicked.connect(lambda checked=False, t=task_key: self.settings_requested.emit(t))
        hl.addWidget(s_btn)

        return row


class _LogStrip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('log_strip')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._text = QTextEdit()
        self._text.setObjectName('log_text')
        self._text.setReadOnly(True)
        layout.addWidget(self._text, stretch=1)

        self._placeholder = QLabel('日志已暂停，启用后将实时显示运行日志')
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet('color: #b2bec3; font-size: 13px;')
        self._placeholder.setVisible(False)
        layout.addWidget(self._placeholder, stretch=1)

        self._con = None
        self._index = 0
        self._show = True
        self._expecting_close_bar = False
        self._last_was_close_bar = False
        self._auto_scroll = True

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._poll)

        from PySide6.QtGui import QPalette, QFont, QFontInfo, QTextBlockFormat

        for _name in ('Sarasa Mono SC', 'Cascadia Mono', 'Consolas'):
            _f = QFont(_name, 10)
            if QFontInfo(_f).family().lower().replace(' ', '') == _name.lower().replace(' ', ''):
                self._mono = _f
                break
        else:
            self._mono = QFont('Consolas', 10)

        self._mono.setStyleHint(QFont.StyleHint.Monospace)
        self._text.document().setDefaultFont(self._mono)

        self._blk_tight = QTextBlockFormat()
        self._blk_tight.setTopMargin(0)
        self._blk_tight.setBottomMargin(0)
        self._blk_tight.setLineHeight(3, 4)

        cursor0 = self._text.textCursor()
        cursor0.setBlockFormat(self._blk_tight)
        self._text.setTextCursor(cursor0)

        pal = self._text.palette()
        pal.setColor(QPalette.ColorRole.Text, QColor('#2d3436'))
        self._text.setPalette(pal)

    def set_account(self, con: str):
        if self._con != con:
            self._con = con
            self._index = 0
            self._text.clear()
        if self._show:
            self._timer.start()
            return

    def stop(self):
        self._timer.stop()

    def clear_log(self):
        import os
        import datetime as dt
        self._text.clear()
        self._expecting_close_bar = False
        self._last_was_close_bar = False
        if not self._con:
            self._index = 0
            return
        date = dt.datetime.now().strftime('%Y-%m-%d')
        log_fn = os.path.join(config.resource_path('runtime/logs'), f'{date}_{self._con}.log')
        try:
            os.remove(log_fn)
            self._index = 0
            return
        except Exception:
            pass

        try:
            with open(log_fn, 'r', encoding='utf-8', errors='replace') as f:
                f.seek(0, 2)
                self._index = f.tell()
        except Exception:
            self._index = 0

    def set_show(self, show: bool):
        self._show = show
        self._text.setVisible(show)
        self._placeholder.setVisible(not show)
        if show:
            if self._con:
                self._timer.start()
                return
        else:
            self._timer.stop()
            self._text.clear()
            self._index = 0

    def _poll(self):
        import os
        import datetime as dt
        if not self._con:
            return
        date = dt.datetime.now().strftime('%Y-%m-%d')
        log_fn = os.path.join(config.resource_path('runtime/logs'), f'{date}_{self._con}.log')
        if not os.path.exists(log_fn):
            return

        try:
            with open(log_fn, 'r', encoding='utf-8', errors='replace') as f:
                if self._index == 0:
                    f.seek(0, 2)
                    self._index = max(f.tell() - 30720, 0)
                f.seek(self._index)
                chunk = f.read()
                self._index = f.tell()
        except Exception:
            return

        sb = self._text.verticalScrollBar()
        saved_pos = sb.value()
        for line in chunk.splitlines(keepends=True):
            self._render_plain_line(line)
        if not self._auto_scroll:
            sb.setValue(saved_pos)
            return

    def set_auto_scroll(self, enabled: bool):
        self._auto_scroll = enabled

    def _fmt(self, color=None, bold=False) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setFont(self._mono)
        if color:
            f.setForeground(QColor(color))
        if bold:
            f.setFontWeight(QFont.Weight.Bold)
        return f

    def _render_plain_line(self, line: str):
        raw = line.rstrip('\r\n')
        stripped = raw.strip()

        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.setBlockFormat(self._blk_tight)

        m = _LOG_PLAIN_RE.match(line)

        if not m:
            if stripped and all(c == '═' for c in stripped):
                if self._last_was_close_bar:
                    self._last_was_close_bar = False
                    self._expecting_close_bar = False
                else:
                    cursor.insertText(stripped + '\n', self._fmt('#b2bec3'))
                    if self._auto_scroll:
                        self._text.setTextCursor(cursor)
                        self._text.ensureCursorVisible()
                    if self._expecting_close_bar:
                        self._expecting_close_bar = False
                        self._last_was_close_bar = True
                return

            if len(raw) - len(raw.lstrip()) >= 5:
                blk_c = QTextBlockFormat()
                blk_c.setAlignment(Qt.AlignCenter)
                cursor.mergeBlockFormat(blk_c)
                cursor.insertText(stripped, self._fmt('#0984e3', bold=True))
                blk_l = QTextBlockFormat()
                blk_l.setAlignment(Qt.AlignLeft)
                cursor.insertBlock(blk_l)
                self._text.setTextCursor(cursor)
                if self._auto_scroll:
                    self._text.ensureCursorVisible()
                self._expecting_close_bar = True
                self._last_was_close_bar = False
                return

            self._expecting_close_bar = False
            self._last_was_close_bar = False
            plain = re.sub(r'^v[\d.]+\s+', '', line)
            cursor.insertText(plain, self._fmt())
            self._text.setTextCursor(cursor)
            if self._auto_scroll:
                self._text.ensureCursorVisible()
            return

        after_ver = re.sub(r'^v[\d.]+\s+', '', line)
        lvl_start = after_ver.find(m.group(1))
        lvl_end = lvl_start + len(m.group(1))
        ts_end = lvl_start + len(m.group(1)) + len(m.group(2))
        msg = after_ver[ts_end:]

        if not msg.strip():
            return

        self._expecting_close_bar = False
        self._last_was_close_bar = False
        level = m.group(1).upper()

        cursor.insertText(after_ver[:lvl_end],
                          self._fmt(_LEVEL_COLORS.get(level, '#636e72'), bold=True))
        cursor.insertText(after_ver[lvl_end:ts_end],
                          self._fmt('#0598bc'))
        cursor.insertText(msg, self._fmt())

        self._text.setTextCursor(cursor)
        if self._auto_scroll:
            self._text.ensureCursorVisible()


class DashboardWidget(QWidget):
    config_requested = Signal(str, str)
    theme_toggle = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._con = None
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(3000)
        self._refresh_timer.timeout.connect(self._refresh)
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 0, 12, 8)
        root.setSpacing(0)

        body = QWidget()
        body_hl = QHBoxLayout(body)
        body_hl.setContentsMargins(0, 0, 0, 0)
        body_hl.setSpacing(10)
        root.addWidget(body)

        left_widget = QWidget()
        left_widget.setFixedWidth(255)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        sched_bar = QWidget()
        sched_bar.setObjectName('sched_frame')
        sched_bar.setFixedHeight(46)
        sched_hl = QHBoxLayout(sched_bar)
        sched_hl.setContentsMargins(8, 6, 10, 6)
        sched_hl.setSpacing(6)

        self._spinner = _SpinnerWidget()
        sched_hl.addWidget(self._spinner)

        self._running_lbl = QLabel('闲置中')
        self._running_lbl.setStyleSheet('font-size:14px; color:#95a5a6;')
        sched_hl.addWidget(self._running_lbl)

        sched_hl.addStretch()

        self._sched_setting_btn = QPushButton('设置')
        self._sched_setting_btn.setObjectName('settings_shortcut_btn')
        self._sched_setting_btn.setFixedSize(56, 24)
        self._sched_setting_btn.setStyleSheet('QPushButton { margin-left: 1px; }')
        self._sched_setting_btn.setCursor(Qt.PointingHandCursor)
        self._sched_setting_btn.setVisible(False)
        self._sched_setting_btn.clicked.connect(self._on_sched_setting)
        sched_hl.addWidget(self._sched_setting_btn)
        sched_hl.addSpacing(4)

        self._start_btn = QPushButton('启动')
        self._start_btn.setObjectName('start_btn')
        self._stop_btn = QPushButton('停止')
        self._stop_btn.setObjectName('stop_btn')
        self._stop_btn.setVisible(False)
        self._start_btn.clicked.connect(self._start)
        self._stop_btn.clicked.connect(self._stop)
        sched_hl.addWidget(self._start_btn)
        sched_hl.addWidget(self._stop_btn)

        left_layout.addWidget(sched_bar)

        self._p_queue = _TaskPanel('queue', '队列中', [('关闭', 'close')])
        self._p_wait = _TaskPanel('waiting', '等待中', [('重置', 'reset'), ('关闭', 'close')])
        self._p_closed = _TaskPanel('closed', '已关闭', [('开启', 'open')])

        for p, s in zip((self._p_queue, self._p_wait, self._p_closed), (3.5, 3.5, 2)):
            left_layout.addWidget(p, stretch=s)
            p.task_action.connect(self._on_task_action)
            p.settings_requested.connect(self._on_settings_requested)

        body_hl.addWidget(left_widget)

        log_frame = QFrame()
        log_frame.setObjectName('log_frame')
        log_vl = QVBoxLayout(log_frame)
        log_vl.setContentsMargins(0, 0, 0, 2)
        log_vl.setSpacing(0)

        log_hdr = QWidget()
        log_hdr.setObjectName('log_hdr')
        log_hdr.setFixedHeight(44)
        log_hdr_hl = QHBoxLayout(log_hdr)
        log_hdr_hl.setContentsMargins(14, 0, 10, 0)
        log_hdr_hl.setSpacing(0)

        log_lbl = QLabel('日志')
        log_lbl.setStyleSheet('font-weight:bold; font-size:14px;')
        log_hdr_hl.addWidget(log_lbl)

        log_hdr_hl.addStretch()

        self._log_clear_btn = QPushButton('清空')
        self._log_clear_btn.setObjectName('log_ctrl_btn')
        self._log_clear_btn.setFixedHeight(24)
        self._log_clear_btn.setCursor(Qt.PointingHandCursor)
        self._log_clear_btn.clicked.connect(self._on_clear_log)
        log_hdr_hl.addWidget(self._log_clear_btn)
        log_hdr_hl.addSpacing(10)

        self._scroll_toggle_lbl = QLabel('滚动')
        self._scroll_toggle_lbl.setStyleSheet('font-size:13px; color:#636e72;')
        log_hdr_hl.addWidget(self._scroll_toggle_lbl)
        log_hdr_hl.addSpacing(6)

        self._scroll_toggle = ToggleSwitchWidget()
        self._scroll_toggle.setChecked(True)
        self._scroll_toggle.toggled.connect(self._on_toggle_scroll)
        log_hdr_hl.addWidget(self._scroll_toggle)
        log_hdr_hl.addSpacing(10)

        log_toggle_lbl = QLabel('日志')
        log_toggle_lbl.setStyleSheet('font-size:13px; color:#636e72;')
        log_hdr_hl.addWidget(log_toggle_lbl)
        log_hdr_hl.addSpacing(6)

        self._log_toggle = ToggleSwitchWidget()
        self._log_toggle.toggled.connect(self._on_toggle_log)
        log_hdr_hl.addWidget(self._log_toggle)

        log_vl.addWidget(log_hdr)

        log_hdr_sep = QFrame()
        log_hdr_sep.setObjectName('log_hdr_sep')
        log_hdr_sep.setFixedHeight(1)
        log_vl.addWidget(log_hdr_sep)

        self._log = _LogStrip()
        log_vl.addWidget(self._log, stretch=1)

        self._apply_log_show(app_module.load_log_show())

        log_outer = QVBoxLayout()
        log_outer.setContentsMargins(0, 0, 0, 6)
        log_outer.setSpacing(0)
        log_outer.addWidget(log_frame)
        body_hl.addLayout(log_outer, stretch=1)

    def _apply_log_show(self, show: bool):
        self._log.set_show(show)
        self._log_toggle.toggled.disconnect(self._on_toggle_log)
        self._log_toggle.setChecked(show)
        self._log_toggle.toggled.connect(self._on_toggle_log)
        self._log_clear_btn.setVisible(show)
        self._scroll_toggle_lbl.setVisible(show)
        self._scroll_toggle.setVisible(show)

    def _on_clear_log(self):
        self._log.clear_log()

    def _on_toggle_scroll(self, checked: bool):
        self._log.set_auto_scroll(checked)

    def _on_toggle_log(self, checked: bool):
        app_module.save_log_show(checked)
        process.m.set_log_enabled(checked)
        self._apply_log_show(checked)

    def update_theme_icon(self, dark: bool):
        pass

    def set_account(self, con: str):
        self._con = con
        self._log.set_account(con)
        self._refresh_timer.start()
        self._refresh()

    def stop(self):
        self._refresh_timer.stop()
        self._log.stop()

    def _start(self):
        if not self._con:
            return
        try:
            process.m.start_process(self._con)
        except PermissionError as e:
            show_permission_error(self, str(e))
            return
        self._refresh()

    def _stop(self):
        if not self._con:
            return
        process.m.stop_process(self._con)
        self._refresh()

    def _on_settings_requested(self, task_key: str):
        if self._con:
            self.config_requested.emit(self._con, task_key)
            return

    def _on_sched_setting(self):
        if self._con and getattr(self, '_current_running_key', ''):
            self.config_requested.emit(self._con, self._current_running_key)
            return

    def _on_task_action(self, task_key: str, action: str):
        if not self._con:
            return
        try:
            data = config.load_ba_config(self._con)
        except Exception:
            return
        task_conf = data.get(task_key)
        if not (isinstance(task_conf, dict) and 'base' in task_conf):
            return
        if action == 'close':
            task_conf['base']['enable'] = False
        elif action == 'open':
            task_conf['base']['enable'] = True
        elif action == 'reset':
            task_conf['base']['next'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data[task_key] = task_conf
        try:
            config.save_ba_config(self._con, data)
        except Exception:
            pass
        self._refresh()

    def _refresh(self):
        if not self._con:
            return
        running = process.m.state_process(self._con) and not process.m.error_task(self._con)

        if running:
            self._start_btn.setVisible(False)
            self._stop_btn.setVisible(True)
        else:
            self._start_btn.setVisible(True)
            self._stop_btn.setVisible(False)

        s = compute_schedule(self._con)

        want_interval = 1000 if running or s['queue'] else 3000
        if self._refresh_timer.interval() != want_interval:
            self._refresh_timer.setInterval(want_interval)
            self._refresh_timer.start()

        if s['running']:
            item = s['running'][0]
            name = item.get('text') or item.get('task', '')
            self._current_running_key = item.get('task', '')
            self._spinner.set_running(True)
            self._running_lbl.setText(name)
            self._running_lbl.setStyleSheet('font-size:14px; color:#27ae60; font-weight:bold;')
            self._sched_setting_btn.setVisible(True)
        elif running and s['queue']:
            self._current_running_key = ''
            self._spinner.set_running(True)
            self._running_lbl.setText('启动中...')
            self._running_lbl.setStyleSheet('font-size:14px; color:#e67e22; font-weight:bold;')
            self._sched_setting_btn.setVisible(False)
        elif running:
            self._current_running_key = ''
            self._spinner.set_running(True)
            self._running_lbl.setText('等待中...')
            self._running_lbl.setStyleSheet('font-size:14px; color:#e67e22; font-weight:bold;')
            self._sched_setting_btn.setVisible(False)
        else:
            self._current_running_key = ''
            self._spinner.set_running(False)
            self._sched_setting_btn.setVisible(False)
            error_key = process.m.error_task(self._con)
            if error_key:
                self._current_running_key = error_key
                all_tasks = s['queue'] + s['waiting'] + s['closed']
                task_text = next(
                    (t['text'] for t in all_tasks if t['task'] == error_key),
                    TEXT_MAP.get(error_key, error_key),
                )
                self._spinner.set_error(True)
                self._running_lbl.setText(task_text)
                self._running_lbl.setStyleSheet('font-size:14px; color:#d63031; font-weight:bold;')
                self._sched_setting_btn.setVisible(True)
            else:
                self._spinner.set_error(False)
                self._running_lbl.setText('闲置中')
                self._running_lbl.setStyleSheet('font-size:14px; color:#95a5a6;')

        self._p_queue.update_tasks(s['queue'])
        self._p_wait.update_tasks(s['waiting'])
        self._p_closed.update_tasks(s['closed'])
