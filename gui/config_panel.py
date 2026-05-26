import json
import re

from PySide6.QtCore import Qt, QTimer, QObject, QEvent
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor, QPixmap, QFont, QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QFrame, QGroupBox,
    QLabel, QCheckBox, QLineEdit, QPushButton, QComboBox, QDoubleSpinBox,
    QListWidget, QListWidgetItem, QTextEdit, QSizePolicy, QStackedWidget
)

from common import config

_CTRL_W = 345
_TIME_RE = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')

from PySide6.QtCore import Signal as _Signal

_SP_W = 70
_SEL_W = 200
_ROW_H = 36
_DEL_W = _ROW_H
_ROW_GAP = 25


class _MultiCheckWidget(QWidget):
    """多选按钮网格 — 替代 QListWidget MultiSelection，每项为可切换的 QPushButton。"""

    itemSelectionChanged = _Signal()

    class _Item:
        """兼容 QListWidgetItem.data() 接口，供 _get_value 统一处理。"""

        def __init__(self, value):
            self._value = value

        def data(self, _role):
            return self._value

    def __init__(self, items: list, selected: list, cols: int, parent=None):
        """
        items:    [(display_text, value), ...]
        selected: [value, ...] 初始已选值列表
        cols:     每行按钮数
        """
        super().__init__(parent)
        self._items = items
        self._buttons = {}

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 2, 0, 2)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)

        for col in range(cols):
            grid.setColumnStretch(col, 1)

        for i, (text, value) in enumerate(items):
            btn = QPushButton(str(text))
            btn.setCheckable(True)
            btn.setChecked(value in selected)
            btn.setObjectName('multi_check_btn')
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.toggled.connect(lambda checked, self=self: self.itemSelectionChanged.emit())
            self._buttons[value] = btn
            grid.addWidget(btn, i // cols, i % cols)

    def selectedItems(self):
        return [self._Item(v) for _, v in self._items if self._buttons[v].isChecked()]


_FOCUS_SS_COMBO = 'QComboBox::drop-down { border-top-color:#4E4C97; border-right-color:#4E4C97; border-bottom-color:#4E4C97; border-left-color:#4E4C97; }'

_FOCUS_SS_COMBO_POPUP = 'QComboBox { border-top-color:#4E4C97; border-left-color:#4E4C97; border-bottom-color:#4E4C97; }QComboBox::drop-down { border-top-color:#4E4C97; border-right-color:#4E4C97; border-bottom-color:#4E4C97; border-left-color:#4E4C97; }'

_FOCUS_SS_SPIN = 'QDoubleSpinBox::up-button { border-top-color:#4E4C97; border-right-color:#4E4C97; }QDoubleSpinBox::down-button { border-bottom-color:#4E4C97; border-right-color:#4E4C97; }'


class _ComboViewFilter(QObject):
    """安装在 QComboBox.view() 上：弹出时保持全边框聚焦色；关闭时复位高亮项和边框。"""

    def __init__(self, combo):
        super().__init__(combo)
        self._combo = combo

    def eventFilter(self, obj, event):
        t = event.type()
        if t == QEvent.Type.Hide:
            combo = self._combo

            def _on_hidden():
                idx = combo.currentIndex()
                combo.view().setCurrentIndex(combo.model().index(idx, 0))
                if not combo.hasFocus():
                    combo.setStyleSheet('')

            QTimer.singleShot(0, _on_hidden)
        return False


class _FocusBorderFilter(QObject):
    """聚焦/失焦时同步右侧子控件（drop-down / up-down button）边框颜色。"""

    def eventFilter(self, obj, event):
        t = event.type()
        if t == QEvent.Type.FocusIn:
            if isinstance(obj, QComboBox):
                obj.setStyleSheet(_FOCUS_SS_COMBO_POPUP)
                obj.repaint()
            elif isinstance(obj, QDoubleSpinBox):
                obj.setStyleSheet(_FOCUS_SS_SPIN)
        elif t == QEvent.Type.FocusOut:
            if not isinstance(obj, QComboBox):
                obj.setStyleSheet('')
        return False


_focus_border_filter = _FocusBorderFilter()


def _install_combo_filters(combo: 'QComboBox'):
    combo.installEventFilter(_focus_border_filter)
    combo.view().installEventFilter(_ComboViewFilter(combo))


class _SpinCursorFilter(QObject):
    """鼠标悬停在 SpinBox 按钮区域时显示小手光标。"""

    def eventFilter(self, obj, event):
        t = event.type()
        if t == QEvent.Type.MouseMove:
            if event.pos().x() > obj.width() - 26:
                obj.setCursor(Qt.PointingHandCursor)
            else:
                obj.unsetCursor()
        elif t == QEvent.Type.Leave:
            obj.unsetCursor()
        return False


_SEL = Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard


class _JsonHighlighter(QSyntaxHighlighter):
    _KEY_RE = re.compile(r'"(?:[^"\\]|\\.)*"\s*(?=:)')
    _STR_RE = re.compile(r'"(?:[^"\\]|\\.)*"')
    _NUM_RE = re.compile(r'(?<!["\w])-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?(?!["\w])')
    _KW_RE = re.compile(r'\b(true|false|null)\b')

    def __init__(self, doc):
        super().__init__(doc)

        def _fmt(color, bold=False):
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if bold:
                f.setFontWeight(QFont.Weight.Bold)
            return f

        self._fmts = {
            'key': _fmt('#6c5ce7', bold=True),
            'str': _fmt('#00b894'),
            'num': _fmt('#0984e3'),
            'kw': _fmt('#e17055'),
        }

    def highlightBlock(self, text: str):
        for m in self._STR_RE.finditer(text):
            self.setFormat(m.start(), len(m.group()), self._fmts['str'])
        for m in self._KEY_RE.finditer(text):
            self.setFormat(m.start(), len(m.group()), self._fmts['key'])
        for m in self._NUM_RE.finditer(text):
            self.setFormat(m.start(), len(m.group()), self._fmts['num'])
        for m in self._KW_RE.finditer(text):
            self.setFormat(m.start(), len(m.group()), self._fmts['kw'])


def _make_check_pixmap(size: int = 15) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor('white'), 2.0)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    s = size / 16.0
    path = QPainterPath()
    path.moveTo(2.5 * s, 8.5 * s)
    path.lineTo(6.5 * s, 12.5 * s)
    path.lineTo(13.5 * s, 4.5 * s)
    p.drawPath(path)
    p.end()
    return pix


def _fmt_desc(text: str) -> str:
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'</?br\s*/?>', '\n', text, flags=re.IGNORECASE)

    def _tr_to_line(m):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', m.group(0), flags=re.IGNORECASE | re.DOTALL)
        cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        return '  '.join(c for c in cells if c) + '\n'

    text = re.sub(r'<tr[^>]*>.*?</tr>', _tr_to_line, text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    lines = [l.strip() for l in text.splitlines()]
    text = '\n'.join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


class _ListEntryEditor(QWidget):
    """通用"多条目列表"编辑器：表头 + 数据行，每行末有删除按钮，底部有添加按钮。"""

    changed = _Signal()

    def __init__(self, field_schemas: list, initial_data: list, on_change, parent=None):
        super().__init__(parent)
        self._field_schemas = field_schemas
        self._on_change = on_change

        header = QWidget()
        header.setObjectName('list_header')
        hdr_hl = QHBoxLayout(header)
        hdr_hl.setContentsMargins(0, 0, 0, 4)
        hdr_hl.setSpacing(_ROW_GAP)
        for key, schema in field_schemas:
            lbl = QLabel(schema.get('name', key))
            lbl.setObjectName('list_header_lbl')
            ftype = schema.get('type')
            if ftype == 'num':
                lbl.setFixedWidth(_SP_W)
                lbl.setAlignment(Qt.AlignCenter)
            else:
                lbl.setFixedWidth(_SEL_W)
            hdr_hl.addWidget(lbl)
        hdr_hl.addSpacing(_DEL_W)
        hdr_hl.addStretch()

        self._rows_vl = QVBoxLayout()
        self._rows_vl.setContentsMargins(0, 0, 0, 4)
        self._rows_vl.setSpacing(4)

        add_btn = QPushButton('＋ 添加')
        add_btn.setObjectName('list_add_btn')
        add_btn.clicked.connect(lambda: self._add_row({}))

        vl = QVBoxLayout(self)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(2)
        vl.addWidget(header)
        vl.addLayout(self._rows_vl)
        vl.addSpacing(4)
        vl.addWidget(add_btn, alignment=Qt.AlignLeft)

        self._loading = True
        for entry in (initial_data or []):
            self._add_row(entry)
        self._loading = False

    def _add_row(self, entry: dict):
        row = QWidget()
        row.setObjectName('list_row')
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 2, 0, 2)
        hl.setSpacing(_ROW_GAP)

        widgets = {}
        for key, schema in self._field_schemas:
            ftype = schema.get('type')
            items = schema.get('items', [])
            opts = schema.get('opts', {})
            value = entry.get(key)

            if ftype == 'sel' and isinstance(items, list):
                w = QComboBox()
                w.setFixedSize(_SEL_W, _ROW_H)
                w.setCursor(Qt.PointingHandCursor)
                w.view().setCursor(Qt.PointingHandCursor)
                for it in items:
                    w.addItem(it['name'], it['value'])
                if value is not None:
                    idx = w.findData(value)
                    if idx >= 0:
                        w.setCurrentIndex(idx)
                w.currentIndexChanged.connect(lambda: self._emit())
                _install_combo_filters(w)
                hl.addWidget(w)
            elif ftype == 'num':
                w = QDoubleSpinBox()
                w.setDecimals(0)
                w.setMinimum(float(opts.get('min', 0)))
                w.setMaximum(float(opts.get('max', 9999)))
                w.setSingleStep(float(opts.get('step', 1)))
                w.setFixedSize(_SP_W, _ROW_H)
                w.setAlignment(Qt.AlignCenter)
                w.setCursor(Qt.PointingHandCursor)
                if value is not None:
                    w.setValue(float(value))
                w.valueChanged.connect(lambda: self._emit())
                w.installEventFilter(_focus_border_filter)
                hl.addWidget(w)
            else:
                continue

            widgets[key] = w

        del_btn = QPushButton('✕')
        del_btn.setFixedSize(_DEL_W, _ROW_H)
        del_btn.setObjectName('list_del_btn')
        del_btn.clicked.connect(lambda row=row: self._del_row(row))
        hl.addWidget(del_btn)
        hl.addStretch()

        row._entry_widgets = widgets
        self._rows_vl.addWidget(row)
        if not self._loading:
            self._emit()

    def _del_row(self, row):
        self._rows_vl.removeWidget(row)
        row.deleteLater()
        self._emit()

    def _emit(self):
        self.changed.emit()
        self._on_change()

    @property
    def _list_value(self):
        result = []
        for i in range(self._rows_vl.count()):
            item = self._rows_vl.itemAt(i)
            if not item or not item.widget():
                continue
            row = item.widget()
            entry = {}
            for key, w in row._entry_widgets.items():
                if isinstance(w, QComboBox):
                    entry[key] = w.currentData()
                elif isinstance(w, QDoubleSpinBox):
                    entry[key] = int(w.value())
            result.append(entry)
        return result


def _build_desc_widget(field_desc: str) -> 'QWidget':
    from PySide6.QtWidgets import QGridLayout

    lines = field_desc.splitlines()
    table_lines = [l for l in lines if re.match(r'^\d+图', l.strip()) and '  ' in l]

    if not table_lines:
        lbl = QLabel(field_desc)
        lbl.setObjectName('field_desc')
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(_SEL)
        return lbl

    container = QWidget()
    vl = QVBoxLayout(container)
    vl.setContentsMargins(0, 0, 0, 0)
    vl.setSpacing(2)

    grid_widget = None
    grid = None
    grid_row = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r'^\d+图', stripped) and '  ' in line:
            if grid is None:
                grid_widget = QWidget()
                grid = QGridLayout(grid_widget)
                grid.setContentsMargins(0, 0, 0, 0)
                grid.setHorizontalSpacing(12)
                grid.setVerticalSpacing(1)
                vl.addWidget(grid_widget)

            cells = [c.strip() for c in re.split(r' {2,}', stripped) if c.strip()]
            for col, cell in enumerate(cells):
                cell_lbl = QLabel(cell)
                cell_lbl.setObjectName('field_desc')
                cell_lbl.setTextInteractionFlags(_SEL)
                grid.addWidget(cell_lbl, grid_row, col)
            grid_row += 1
        else:
            lbl = QLabel(stripped)
            lbl.setObjectName('field_desc')
            lbl.setWordWrap(True)
            lbl.setTextInteractionFlags(_SEL)
            vl.addWidget(lbl)

    return container


def _confirm_reset(parent: QWidget, fn: str) -> bool:
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel

    dlg = QDialog(parent)
    dlg.setWindowTitle('确认还原')
    dlg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
    dlg.setFixedWidth(320)

    vl = QVBoxLayout(dlg)
    vl.setContentsMargins(24, 20, 24, 16)
    vl.setSpacing(16)

    from gui.sidebar import FN_NAMES
    fn_display = FN_NAMES.get(fn, fn)

    lbl = QLabel(f'将把 <b>{fn_display}</b> 的设置还原为默认值<br>是否确认？')
    lbl.setWordWrap(True)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet('font-size: 13px;')
    vl.addWidget(lbl)

    btn_hl = QHBoxLayout()
    btn_hl.setSpacing(12)
    btn_no = QPushButton('取消')
    btn_yes = QPushButton('确认')
    btn_no.setObjectName('reset_confirm_no')
    btn_yes.setObjectName('reset_confirm_yes')
    btn_yes.setFixedSize(80, 32)
    btn_no.setFixedSize(80, 32)
    btn_no.clicked.connect(dlg.reject)
    btn_yes.clicked.connect(dlg.accept)
    btn_hl.addWidget(btn_yes)
    btn_hl.addWidget(btn_no)
    vl.addLayout(btn_hl)

    dlg.adjustSize()
    dlg.setFixedSize(dlg.size())
    return dlg.exec() == QDialog.DialogCode.Accepted


class ConfigPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._con = None
        self._fn = None
        self._render_schema = {}
        self._widgets = {}

        self._spin_cursor = _SpinCursorFilter(self)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(600)
        self._save_timer.timeout.connect(self._do_save)

        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.setInterval(500)

        self._setup_ui()
        self._load_render_schema()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(0)

        self._content_stack = QStackedWidget()

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._form_widget = QWidget()
        self._form_layout = QVBoxLayout(self._form_widget)
        self._form_layout.setContentsMargins(0, 4, 8, 8)
        self._form_layout.setSpacing(10)
        self._form_layout.addStretch()
        self._scroll.setWidget(self._form_widget)
        self._content_stack.addWidget(self._scroll)

        self._json_editor = QTextEdit()
        self._json_editor.setObjectName('json_editor')
        self._json_editor.setFont(QFont('Consolas', 16))
        self._json_editor.setAcceptRichText(False)
        self._json_highlighter = _JsonHighlighter(self._json_editor.document())
        self._json_editor.textChanged.connect(self._on_json_changed)
        self._content_stack.addWidget(self._json_editor)

        root.addWidget(self._content_stack)

        self._mode_btn = QPushButton('JSON', self)
        self._mode_btn.setObjectName('mode_toggle_btn')
        self._mode_btn.setFixedSize(64, 26)
        self._mode_btn.setCursor(Qt.PointingHandCursor)
        self._mode_btn.clicked.connect(self._toggle_mode)

        self._reset_btn = QPushButton('还原', self)
        self._reset_btn.setObjectName('reset_config_btn')
        self._reset_btn.setFixedSize(52, 26)
        self._reset_btn.setCursor(Qt.PointingHandCursor)
        self._reset_btn.clicked.connect(self._on_reset)

        self._toast = QFrame(self)
        self._toast.setObjectName('toast_label')
        self._toast.setFrameShape(QFrame.Shape.NoFrame)
        toast_hl = QHBoxLayout(self._toast)
        toast_hl.setContentsMargins(12, 7, 16, 7)
        toast_hl.setSpacing(8)
        _ico = QLabel()
        _ico.setPixmap(_make_check_pixmap(15))
        _ico.setFixedSize(15, 15)
        _ico.setStyleSheet('background:transparent;')
        toast_hl.addWidget(_ico)
        _txt = QLabel('已保存')
        _txt.setStyleSheet('color:white; font-size:13px; font-weight:bold; background:transparent;')
        toast_hl.addWidget(_txt)
        self._toast.setVisible(False)
        self._toast_timer.timeout.connect(lambda: self._toast.setVisible(False))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_mode_btn()

    def _reposition_mode_btn(self):
        right_margin = 30
        y = 10 + (22 - self._mode_btn.height()) // 2 + 8

        x_mode = self.width() - right_margin - self._mode_btn.width()
        self._mode_btn.move(x_mode, y)
        self._mode_btn.raise_()

        x_reset = x_mode - 6 - self._reset_btn.width()
        self._reset_btn.move(x_reset, y)
        self._reset_btn.raise_()

    def _show_toast(self):
        top = self.window()
        if self._toast.parent() is not top:
            self._toast.setParent(top)
        sh = self._toast.sizeHint()
        self._toast.setFixedSize(sh.width(), sh.height())
        self._toast.move((top.width() - sh.width()) // 2, 8)
        self._toast.raise_()
        self._toast.setVisible(True)
        self._toast_timer.start()

    def _load_render_schema(self):
        try:
            with open(config.get_froze_path('web/static/render.json'), 'r', encoding='utf-8') as f:
                self._render_schema = json.load(f)
        except Exception:
            self._render_schema = {}

    def _visual_to_json(self) -> str:
        try:
            data = config.load_ba_config(self._con)
        except Exception:
            data = {}
        section_data = dict(data.get(self._fn, {}))
        for key, widget in self._widgets.items():
            value = self._get_value(key, widget)
            parts = key.split('.', 1)
            if len(parts) == 2:
                sect, field = parts
                if not isinstance(section_data.get(sect), dict):
                    section_data[sect] = {}
                section_data[sect][field] = value
            else:
                section_data[key] = value
        return json.dumps(section_data, ensure_ascii=False, indent=2)

    def _toggle_mode(self):
        if self._content_stack.currentIndex() == 0:
            self._json_editor.blockSignals(True)
            self._json_editor.setPlainText(self._visual_to_json())
            self._json_editor.blockSignals(False)
            self._json_editor.setStyleSheet('')
            self._content_stack.setCurrentIndex(1)
            self._mode_btn.setText('可视化')
            return

        text = self._json_editor.toPlainText().strip()
        try:
            new_data = json.loads(text)
        except json.JSONDecodeError:
            return

        try:
            data = config.load_ba_config(self._con)
            if data.get(self._fn) != new_data:
                data[self._fn] = new_data
                config.save_ba_config(self._con, data)
        except Exception:
            pass

        self._content_stack.setCurrentIndex(0)
        self._mode_btn.setText('JSON')
        self.load(self._con, self._fn)

    def _on_json_changed(self):
        text = self._json_editor.toPlainText().strip()
        try:
            json.loads(text)
            self._json_editor.setStyleSheet('')
            self._save_timer.start()
        except json.JSONDecodeError:
            self._json_editor.setStyleSheet('border: 1px solid #e74c3c;')

    def load(self, con: str, fn: str):
        self._con = con
        self._fn = fn
        self._widgets.clear()

        while self._form_layout.count() > 1:
            item = self._form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self._content_stack.currentIndex() == 1:
            try:
                section_data = config.load_ba_config(con).get(fn, {})
                self._json_editor.blockSignals(True)
                self._json_editor.setPlainText(
                    json.dumps(section_data, ensure_ascii=False, indent=2)
                )
                self._json_editor.blockSignals(False)
                self._json_editor.setStyleSheet('')
            except Exception:
                pass
            return

        schema = self._render_schema.get(fn, {})

        try:
            section_data = config.load_ba_config(con).get(fn, {})
        except Exception:
            section_data = {}

        current_vl = None

        for key, field_schema in schema.items():
            if not isinstance(field_schema, dict):
                continue

            field_type = field_schema.get('type')
            field_name = field_schema.get('name', key)
            field_desc = _fmt_desc(field_schema.get('desc', ''))

            if field_type is None and '.' not in key:
                grp = QGroupBox(field_name)
                current_vl = QVBoxLayout()
                current_vl.setContentsMargins(8, 8, 8, 8)
                current_vl.setSpacing(10)
                grp.setLayout(current_vl)
                self._form_layout.insertWidget(self._form_layout.count() - 1, grp)
                continue

            if field_type == 'skip' or (isinstance(field_schema, str) and field_schema == 'skip'):
                continue

            if key.endswith('.text'):
                continue

            parts = key.split('.', 1)
            if len(parts) == 2:
                sect, field = parts
                sect_val = section_data.get(sect) if isinstance(section_data, dict) else None
                if isinstance(sect_val, dict):
                    value = sect_val.get(field)
                elif isinstance(sect_val, list):
                    if sect not in self._widgets and current_vl is not None:
                        field_schemas = [(k.split('.', 1)[1], v) for k, v in schema.items()
                                          if k.startswith(sect + '.') and isinstance(v, dict) and v.get('type')]
                        editor = _ListEntryEditor(field_schemas, sect_val, self._save_timer.start)
                        current_vl.addWidget(editor)
                        self._widgets[sect] = editor
                    continue
                else:
                    value = None
            else:
                value = section_data.get(key) if isinstance(section_data, dict) else None

            if key == 'base.link_task':
                from gui.sidebar import FN_NAMES
                dyn_items = [{'name': '不关联', 'value': ''}]
                dyn_items += [{'name': name, 'value': fn}
                              for fn, name in FN_NAMES.items()
                              if fn not in (self._fn, 'baas', 'env_check', 'fhx')]
                field_schema = {**field_schema, 'items': dyn_items}

            widget = self._build_widget(field_type, field_schema, value)
            if widget is None:
                continue
            self._widgets[key] = widget

            if current_vl is None:
                grp = QGroupBox('设置')
                current_vl = QVBoxLayout()
                current_vl.setContentsMargins(8, 8, 8, 8)
                current_vl.setSpacing(10)
                grp.setLayout(current_vl)
                self._form_layout.insertWidget(self._form_layout.count() - 1, grp)

            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(12)

            label_w = QWidget()
            lvl = QVBoxLayout(label_w)
            lvl.setContentsMargins(0, 2, 0, 2)
            lvl.setSpacing(2)

            name_lbl = QLabel(field_name)
            name_lbl.setWordWrap(True)
            name_lbl.setTextInteractionFlags(_SEL)
            lvl.addWidget(name_lbl)

            if field_desc:
                lvl.addWidget(_build_desc_widget(field_desc))

            row.addWidget(label_w, 1, Qt.AlignTop)
            row.addWidget(widget, 0, Qt.AlignTop)
            current_vl.addLayout(row)

    def _build_widget(self, field_type, field_schema, value):
        def _schedule():
            self._save_timer.start()

        if field_type == 'bool':
            w = QCheckBox()
            w.setFixedWidth(_CTRL_W)
            w.setCursor(Qt.PointingHandCursor)
            w.setChecked(bool(value) if value is not None else False)
            w.stateChanged.connect(_schedule)
            return w

        if field_type == 'txt':
            w = QLineEdit()
            w.setFixedWidth(_CTRL_W)
            w.setText(str(value) if value is not None else '')
            w.textChanged.connect(_schedule)
            return w

        if field_type == 'num':
            opts = field_schema.get('opts', {})
            w = QDoubleSpinBox()
            w.setFixedWidth(_CTRL_W)
            w.setMinimum(float(opts.get('min', -9999999)))
            w.setMaximum(float(opts.get('max', 9999999)))
            step = float(opts.get('step', 1))
            w.setSingleStep(step)
            w.setDecimals(len(str(step).rstrip('0').split('.')[-1]) if step < 1 else 0)
            w.setValue(float(value) if value is not None else 0)
            w.valueChanged.connect(_schedule)
            w.setMouseTracking(True)
            w.installEventFilter(self._spin_cursor)
            w.installEventFilter(_focus_border_filter)
            return w

        if field_type == 'sel':
            items = field_schema.get('items', [])
            opts = field_schema.get('opts', {})
            is_multi = str(opts.get('multiple', 'false')).lower() == 'true'

            if isinstance(items, dict):
                all_vals = list(range(
                    int(items.get('min', 1)),
                    int(items.get('max', 28)) + 1,
                    int(items.get('step', 1))
                ))
                if is_multi:
                    n = len(all_vals)
                    cols = 7 if n > 8 else n
                    selected = value if isinstance(value, list) else []
                    w = _MultiCheckWidget(
                        [(str(v), v) for v in all_vals],
                        selected,
                        cols
                    )
                    w.setFixedWidth(_CTRL_W)
                    w.itemSelectionChanged.connect(_schedule)
                else:
                    w = QComboBox()
                    w.setFixedWidth(_CTRL_W)
                    w.setCursor(Qt.PointingHandCursor)
                    w.view().setCursor(Qt.PointingHandCursor)
                    for v in all_vals:
                        w.addItem(str(v), v)
                    if value is not None:
                        idx = w.findData(value)
                        if idx >= 0:
                            w.setCurrentIndex(idx)
                    w.currentIndexChanged.connect(_schedule)
                    _install_combo_filters(w)
                return w

            if is_multi and isinstance(items, list):
                selected = value if isinstance(value, list) else []
                pairs = [(it.get('name', ''), it.get('value')) for it in items]
                cols = min(4, len(pairs))
                w = _MultiCheckWidget(pairs, selected, cols)
                w.setFixedWidth(_CTRL_W)
                w.itemSelectionChanged.connect(_schedule)
                return w

            w = QComboBox()
            w.setFixedWidth(_CTRL_W)
            w.setCursor(Qt.PointingHandCursor)
            w.view().setCursor(Qt.PointingHandCursor)
            for item_def in items:
                w.addItem(item_def.get('name', ''), item_def.get('value'))
            if value is not None:
                idx = w.findData(value)
                if idx >= 0:
                    w.setCurrentIndex(idx)
            w.currentIndexChanged.connect(_schedule)
            _install_combo_filters(w)
            return w

        if field_type == 'arr':
            w = QTextEdit()
            w.setFixedWidth(_CTRL_W)
            w.setFixedHeight(100)
            w.setPlaceholderText('每行一条')
            if isinstance(value, list):
                w.setPlainText('\n'.join(str(v) for v in value))
            elif isinstance(value, str):
                w.setPlainText(value)
            w.textChanged.connect(_schedule)
            return w

        if field_type == 'time':
            container = QWidget()
            container.setFixedWidth(_CTRL_W)
            cvl = QVBoxLayout(container)
            cvl.setContentsMargins(0, 0, 0, 0)
            cvl.setSpacing(3)

            inp = QLineEdit()
            inp.setText(str(value) if value is not None else '')
            cvl.addWidget(inp)

            err_lbl = QLabel('格式有误，应为 YYYY-MM-DD HH:MM:SS')
            err_lbl.setObjectName('time_error_lbl')
            err_lbl.setVisible(False)
            cvl.addWidget(err_lbl)

            def _validate_time():
                text = inp.text().strip()
                ok = not text or bool(_TIME_RE.match(text))
                err_lbl.setVisible(not ok)
                inp.setStyleSheet('' if ok else 'border-color: #e74c3c;')
                return ok

            def _on_time_changed():
                if _validate_time():
                    _schedule()

            inp.textChanged.connect(_on_time_changed)
            _validate_time()
            inp._time_input = True
            return container

        return None

    def _get_value(self, key, widget):
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, QLineEdit):
            return widget.text()
        if isinstance(widget, QDoubleSpinBox):
            if widget.decimals() == 0:
                return int(widget.value())
            return widget.value()
        if isinstance(widget, QComboBox):
            return widget.currentData()
        if isinstance(widget, (QListWidget, _MultiCheckWidget)):
            return [item.data(Qt.UserRole) for item in widget.selectedItems()]
        if isinstance(widget, QTextEdit):
            text = widget.toPlainText().strip()
            if text:
                return [line.strip() for line in text.splitlines() if line.strip()]
            return []
        if hasattr(widget, '_time_input'):
            return widget._time_input.text().strip()
        if hasattr(widget, '_list_value'):
            return widget._list_value
        return None

    def _on_reset(self):
        if not self._con or not self._fn:
            return
        if not _confirm_reset(self, self._fn):
            return

        try:
            with open(config.get_froze_path('web/static/baas.json'), 'r', encoding='utf-8') as f:
                default_data = json.load(f)
        except Exception:
            return

        fn_default = default_data.get(self._fn)
        if fn_default is None:
            return

        try:
            data = config.load_ba_config(self._con)
            data[self._fn] = fn_default
            config.save_ba_config(self._con, data)
        except Exception:
            return

        self.load(self._con, self._fn)
        self._show_toast()

    def _do_save(self):
        if not self._con or not self._fn:
            return

        if self._content_stack.currentIndex() == 1:
            text = self._json_editor.toPlainText().strip()
            try:
                new_data = json.loads(text)
                data = config.load_ba_config(self._con)
                data[self._fn] = new_data
                config.save_ba_config(self._con, data)
                self._show_toast()
            except Exception:
                pass
            return

        for widget in self._widgets.values():
            if hasattr(widget, '_time_input'):
                text = widget._time_input.text().strip()
                if text and not _TIME_RE.match(text):
                    return

        try:
            data = config.load_ba_config(self._con)
        except Exception:
            return

        section_data = data.get(self._fn, {})
        for key, widget in self._widgets.items():
            value = self._get_value(key, widget)
            parts = key.split('.', 1)
            if len(parts) == 2:
                sect, field = parts
                if not isinstance(section_data.get(sect), dict):
                    section_data[sect] = {}
                section_data[sect][field] = value
            else:
                section_data[key] = value

        data[self._fn] = section_data

        try:
            config.save_ba_config(self._con, data)
            self._show_toast()
        except Exception:
            pass
