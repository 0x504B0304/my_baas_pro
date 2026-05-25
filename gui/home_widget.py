import os
import shutil
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QScrollArea, QFrame, QDialog, QLineEdit, QComboBox, QButtonGroup
from PySide6.QtGui import QPixmap, QIcon
from gui.release_dialog import _RELEASE_HTML
from common import app as app_module
from common import config as app_config
from common import config as cfg

def _make_icon(rel_path: str) -> QIcon:
    from PySide6.QtGui import QPixmap
    pix = QPixmap(app_config.resource_path(rel_path))
    ico = QIcon()
    ico.addPixmap(pix, QIcon.Mode.Normal)
    ico.addPixmap(pix, QIcon.Mode.Selected)
    return ico

_HELP_LINKS = [
    {
        'name': '帮助/教程',
        'items': [
            {'name': '多开教程', 'link': 'https://www.bilibili.com/video/BV1ke411z7si/'},
            {'name': '开机启动/一键启动Baas', 'link': 'https://www.bilibili.com/video/BV1Cf421Z7Bf/'},
            {'name': '已知BUG', 'link': 'https://github.com/baas-pro/baas/issues'},
            {'name': '提交Bug', 'link': 'https://github.com/baas-pro/baas/issues/new/choose'},
        ],
    },
]

class _HelpTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        vl = QVBoxLayout(container)
        vl.setContentsMargins(24, 20, 24, 20)
        vl.setSpacing(14)

        for group in _HELP_LINKS:
            for item in group['items']:
                lbl = QLabel(f'<a href="{item["link"]}" style="color:#4E4C97; font-size:14px; text-decoration:none;">› {item["name"]}</a>')
                lbl.setOpenExternalLinks(True)
                lbl.setTextInteractionFlags(Qt.TextBrowserInteraction)
                lbl.setCursor(Qt.PointingHandCursor)
                vl.addWidget(lbl)

        vl.addStretch()
        self.setWidget(container)

class _HomeTab(QWidget):
    theme_set = Signal(bool)
    release_requested = Signal()
    configs_changed = Signal()
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        vl = QVBoxLayout(self)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        center = QWidget()
        cl = QVBoxLayout(center)
        cl.setContentsMargins(40, 40, 40, 40)
        cl.setSpacing(20)
        cl.setAlignment(Qt.AlignTop)

        theme_row = QHBoxLayout()
        theme_row.setSpacing(0)
        theme_lbl = QLabel('界面主题')
        theme_lbl.setStyleSheet('font-size:14px; font-weight:bold;')
        theme_row.addWidget(theme_lbl)
        theme_row.addStretch()

        self._dark_btn = QPushButton('暗色')
        self._light_btn = QPushButton('亮色')
        self._dark_btn.setIcon(_make_icon('assets/icon/moon.png'))
        self._light_btn.setIcon(_make_icon('assets/icon/sun.png'))

        for btn in [self._dark_btn, self._light_btn]:
            btn.setObjectName('theme_seg_btn')
            btn.setCheckable(True)
            btn.setFixedSize(110, 34)
            btn.setIconSize(QSize(15, 15))
            btn.setCursor(Qt.PointingHandCursor)

        self._theme_group = QButtonGroup(self)
        self._theme_group.setExclusive(True)
        self._theme_group.addButton(self._dark_btn, 0)
        self._theme_group.addButton(self._light_btn, 1)
        self._light_btn.setChecked(True)

        self._theme_group.idClicked.connect(self._on_theme_id)
        theme_row.addWidget(self._dark_btn)
        theme_row.addSpacing(6)
        theme_row.addWidget(self._light_btn)
        cl.addLayout(theme_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName('home_sep')
        cl.addWidget(sep)

        reset_row = QHBoxLayout()
        reset_lbl = QLabel('还原设置')
        reset_lbl.setStyleSheet('font-size:14px; font-weight:bold;')
        reset_desc = QLabel('重置窗口大小/位置、关闭方式、侧边栏排序、自动启动、主题等设置，不会删除账号配置。')
        reset_desc.setStyleSheet('font-size:12px; color:#636e72;')
        reset_left = QVBoxLayout()
        reset_left.setSpacing(2)
        reset_left.addWidget(reset_lbl)
        reset_left.addWidget(reset_desc)
        reset_row.addLayout(reset_left)
        reset_row.addStretch()

        reset_btn = QPushButton('还原')
        reset_btn.setObjectName('theme_toggle_btn')
        reset_btn.setFixedSize(110, 34)
        reset_btn.setIcon(_make_icon('assets/icon_white/recover.png'))
        reset_btn.setIconSize(QSize(15, 15))
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(self._on_reset)
        reset_row.addWidget(reset_btn)
        cl.addLayout(reset_row)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setObjectName('home_sep')
        cl.addWidget(sep2)

        log_row = QHBoxLayout()
        log_lbl = QLabel('清理日志')
        log_lbl.setStyleSheet('font-size:14px; font-weight:bold;')
        log_row.addWidget(log_lbl)
        log_row.addStretch()

        self._log_size_lbl = QLabel(self._get_log_size())
        self._log_size_lbl.setStyleSheet('font-size:12px; color:gray;')
        log_row.addWidget(self._log_size_lbl)
        log_row.addSpacing(8)

        clean_btn = QPushButton('清理')
        clean_btn.setObjectName('theme_toggle_btn')
        clean_btn.setFixedSize(110, 34)
        clean_btn.setCursor(Qt.PointingHandCursor)
        clean_btn.setIcon(_make_icon('assets/icon_white/clean.png'))
        clean_btn.setIconSize(QSize(15, 15))
        clean_btn.clicked.connect(self._on_clean_logs)
        log_row.addWidget(clean_btn)
        cl.addLayout(log_row)

        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setObjectName('home_sep')
        cl.addWidget(sep3)

        release_row = QHBoxLayout()
        release_lbl = QLabel('更新日志')
        release_lbl.setStyleSheet('font-size:14px; font-weight:bold;')
        release_row.addWidget(release_lbl)
        release_row.addStretch()

        release_btn = QPushButton('查看')
        release_btn.setObjectName('theme_toggle_btn')
        release_btn.setFixedSize(110, 34)
        release_btn.setCursor(Qt.PointingHandCursor)
        release_btn.setIcon(_make_icon('assets/icon_white/view.png'))
        release_btn.setIconSize(QSize(15, 15))
        release_btn.clicked.connect(self.release_requested)
        release_row.addWidget(release_btn)
        cl.addLayout(release_row)

        vl.addWidget(center)
        vl.addStretch()

    def _get_log_size(self) -> str:
        log_dir = cfg.resource_path('runtime/logs')
        if not os.path.isdir(log_dir):
            return '0 B'

        total = sum(
            os.path.getsize(os.path.join(log_dir, f))
            for f in os.listdir(log_dir)
            if os.path.isfile(os.path.join(log_dir, f))
        )

        for unit in ('B', 'KB', 'MB', 'GB'):
            if total < 1024:
                if unit != 'B':
                    return f'{total:.1f} {unit}'
                else:
                    return f'{total} B'
            total /= 1024
        return f'{total:.1f} TB'

    def refresh_log_size(self):
        self._log_size_lbl.setText(self._get_log_size())

    def _on_clean_logs(self):
        log_dir = cfg.resource_path('runtime/logs')
        if os.path.isdir(log_dir):
            for f in os.listdir(log_dir):
                fp = os.path.join(log_dir, f)
                if os.path.isfile(fp):
                    try:
                        os.remove(fp)
                    except Exception:
                        pass
        self._log_size_lbl.setText(self._get_log_size())

    def _on_reset(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('确认还原')
        dlg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        dlg.setFixedWidth(360)
        vl = QVBoxLayout(dlg)
        vl.setContentsMargins(24, 20, 24, 16)
        vl.setSpacing(16)

        lbl = QLabel('确定要还原脚本设置吗？')
        lbl.setWordWrap(True)
        lbl.setStyleSheet('font-size:13px;')
        vl.addWidget(lbl)

        btn_hl = QHBoxLayout()
        btn_hl.setSpacing(12)
        btn_yes = QPushButton('确认')
        btn_no = QPushButton('取消')
        btn_yes.setObjectName('reset_confirm_yes')
        btn_no.setObjectName('reset_confirm_no')
        btn_yes.setFixedSize(88, 32)
        btn_no.setFixedSize(72, 32)
        btn_yes.setCursor(Qt.PointingHandCursor)
        btn_no.setCursor(Qt.PointingHandCursor)
        btn_yes.clicked.connect(dlg.accept)
        btn_no.clicked.connect(dlg.reject)
        btn_hl.addStretch()
        btn_hl.addWidget(btn_yes)
        btn_hl.addWidget(btn_no)
        vl.addLayout(btn_hl)

        dlg.adjustSize()
        dlg.setFixedSize(dlg.size())

        if dlg.exec() == QDialog.DialogCode.Accepted:
            app_module.reset_app_config()

            self._light_btn.setChecked(True)
            self._dark_btn.setChecked(False)
            self.theme_set.emit(False)

            self.configs_changed.emit()

            self.reset_requested.emit()

            ok_dlg = QDialog(self)
            ok_dlg.setWindowTitle('还原成功')
            ok_dlg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
            ok_vl = QVBoxLayout(ok_dlg)
            ok_vl.setContentsMargins(24, 20, 24, 16)
            ok_vl.setSpacing(16)

            ok_lbl = QLabel('脚本设置已还原。')
            ok_lbl.setStyleSheet('font-size:13px;')
            ok_vl.addWidget(ok_lbl)

            ok_btn = QPushButton('确认')
            ok_btn.setObjectName('reset_confirm_yes')
            ok_btn.setFixedSize(88, 32)
            ok_btn.setCursor(Qt.PointingHandCursor)
            ok_btn.clicked.connect(ok_dlg.accept)

            ok_hl = QHBoxLayout()
            ok_hl.addStretch()
            ok_hl.addWidget(ok_btn)
            ok_vl.addLayout(ok_hl)

            ok_dlg.adjustSize()
            ok_dlg.setFixedSize(ok_dlg.size())
            ok_dlg.exec()

    def _on_theme_id(self, btn_id: int):
        self.theme_set.emit(btn_id == 0)

    def update_theme_icon(self, dark: bool):
        self._dark_btn.setChecked(dark)
        self._light_btn.setChecked(not dark)

def _confirm_delete(parent: QWidget, name: str) -> bool:
    dlg = QDialog(parent)
    dlg.setWindowTitle('确认删除')
    dlg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
    dlg.setFixedWidth(320)

    vl = QVBoxLayout(dlg)
    vl.setContentsMargins(24, 20, 24, 16)
    vl.setSpacing(16)

    lbl = QLabel(f'确定要删除配置 <b>{name}</b> 吗？<br>此操作不可恢复。')
    lbl.setWordWrap(True)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet('font-size: 13px;')
    vl.addWidget(lbl)

    btn_hl = QHBoxLayout()
    btn_hl.setSpacing(12)
    btn_yes = QPushButton('确认删除')
    btn_no = QPushButton('取消')
    btn_yes.setObjectName('reset_confirm_yes')
    btn_no.setObjectName('reset_confirm_no')
    btn_yes.setFixedSize(88, 32)
    btn_no.setFixedSize(72, 32)
    btn_yes.clicked.connect(dlg.accept)
    btn_no.clicked.connect(dlg.reject)
    btn_hl.addWidget(btn_yes)
    btn_hl.addWidget(btn_no)
    vl.addLayout(btn_hl)

    dlg.adjustSize()
    dlg.setFixedSize(dlg.size())
    return dlg.exec() == QDialog.DialogCode.Accepted

class _RenameConfigDialog(QDialog):
    def __init__(self, old_name: str, existing: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle('重命名配置')
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setFixedWidth(360)

        if parent:
            self.setStyleSheet(parent.window().styleSheet())

        vl = QVBoxLayout(self)
        vl.setContentsMargins(24, 20, 24, 20)
        vl.setSpacing(12)

        name_lbl = QLabel('新配置名称')
        name_lbl.setStyleSheet('font-size: 13px; color: gray;')
        vl.addWidget(name_lbl)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText(f'当前：{old_name}')
        self._name_edit.setText(old_name)
        self._name_edit.selectAll()
        self._name_edit.setFixedHeight(32)
        vl.addWidget(self._name_edit)

        self._err_lbl = QLabel('')
        self._err_lbl.setStyleSheet('color: #e17055; font-size: 12px;')
        vl.addWidget(self._err_lbl)

        vl.addSpacing(4)

        btn_hl = QHBoxLayout()
        btn_hl.setSpacing(8)
        btn_ok = QPushButton('保存')
        btn_cancel = QPushButton('取消')
        btn_ok.setFixedSize(88, 34)
        btn_cancel.setFixedSize(88, 34)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_cancel.setCursor(Qt.PointingHandCursor)

        btn_ok.setStyleSheet('QPushButton { background:#4E4C97; color:white; border:none; border-radius:4px; font-size:13px; font-weight:bold; }QPushButton:hover { background:#5d5ab0; }QPushButton:pressed { background:#3d3b7a; }')

        btn_cancel.setStyleSheet('QPushButton { background:#e17055; color:white; border:none; border-radius:4px; font-size:13px; }QPushButton:hover { background:#d96044; }QPushButton:pressed { background:#c0503a; }')

        btn_ok.clicked.connect(self._on_ok)
        btn_cancel.clicked.connect(self.reject)
        btn_hl.addStretch()
        btn_hl.addWidget(btn_ok)
        btn_hl.addWidget(btn_cancel)
        vl.addLayout(btn_hl)

        self._old_name = old_name
        self._existing = existing
        self._result_name = ''

    def _on_ok(self):
        name = self._name_edit.text().strip()
        if not name:
            self._err_lbl.setText('配置名称不能为空')
            return
        if any(c in name for c in '/\\:*?"<>|'):
            self._err_lbl.setText('名称含有非法字符')
            return
        if name == self._old_name:
            self.reject()
            return
        if name in self._existing:
            self._err_lbl.setText('该名称已存在，请换一个')
            return
        self._result_name = name
        self.accept()

    def get_result(self) -> str:
        return self._result_name

class _AddConfigDialog(QDialog):
    def __init__(self, existing: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle('新增配置')
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setFixedWidth(360)

        if parent:
            self.setStyleSheet(parent.window().styleSheet())

        vl = QVBoxLayout(self)
        vl.setContentsMargins(24, 20, 24, 20)
        vl.setSpacing(12)

        name_lbl = QLabel('配置名称')
        name_lbl.setStyleSheet('font-size: 13px; color: gray;')
        vl.addWidget(name_lbl)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText('输入新配置名称')
        self._name_edit.setFixedHeight(32)
        vl.addWidget(self._name_edit)

        src_lbl = QLabel('复制来源')
        src_lbl.setStyleSheet('font-size: 13px; color: gray;')
        vl.addWidget(src_lbl)

        self._src_combo = QComboBox()
        self._src_combo.setCursor(Qt.PointingHandCursor)
        self._src_combo.view().setCursor(Qt.PointingHandCursor)
        self._src_combo.addItem('默认配置', '__default__')
        for name in existing:
            self._src_combo.addItem(name, name)
        vl.addWidget(self._src_combo)

        self._err_lbl = QLabel('')
        self._err_lbl.setStyleSheet('color: #e17055; font-size: 12px;')
        vl.addWidget(self._err_lbl)

        vl.addSpacing(4)

        btn_hl = QHBoxLayout()
        btn_hl.setSpacing(8)
        btn_ok = QPushButton('新增')
        btn_cancel = QPushButton('取消')
        btn_ok.setFixedSize(88, 34)
        btn_cancel.setFixedSize(88, 34)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_cancel.setCursor(Qt.PointingHandCursor)

        btn_ok.setStyleSheet('QPushButton { background:#4E4C97; color:white; border:none; border-radius:4px; font-size:13px; font-weight:bold; }QPushButton:hover { background:#5d5ab0; }QPushButton:pressed { background:#3d3b7a; }')

        btn_cancel.setStyleSheet('QPushButton { background:#e17055; color:white; border:none; border-radius:4px; font-size:13px; }QPushButton:hover { background:#d96044; }QPushButton:pressed { background:#c0503a; }')

        btn_ok.clicked.connect(self._on_ok)
        btn_cancel.clicked.connect(self.reject)
        btn_hl.addStretch()
        btn_hl.addWidget(btn_ok)
        btn_hl.addWidget(btn_cancel)
        vl.addLayout(btn_hl)

        self._result_name = ''
        self._result_src = ''

    def _on_ok(self):
        name = self._name_edit.text().strip()
        if not name:
            self._err_lbl.setText('配置名称不能为空')
            return
        if any(c in name for c in '/\\:*?"<>|'):
            self._err_lbl.setText('名称含有非法字符')
            return
        self._result_name = name
        self._result_src = self._src_combo.currentData()
        self.accept()

    def get_result(self) -> tuple[str, str]:
        return (self._result_name, self._result_src)

class _ConfigMgmtTab(QWidget):
    configs_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        vl = QVBoxLayout(self)
        vl.setContentsMargins(20, 16, 20, 16)
        vl.setSpacing(12)

        hdr = QHBoxLayout()
        open_btn = QPushButton('查看文件')
        open_btn.setObjectName('theme_toggle_btn')
        open_btn.setFixedSize(110, 34)
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setIcon(_make_icon('assets/icon_white/view.png'))
        open_btn.setIconSize(QSize(15, 15))
        open_btn.clicked.connect(self._on_open_config_dir)

        add_btn = QPushButton('新增配置')
        add_btn.setObjectName('save_btn')
        add_btn.setFixedSize(110, 34)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setIcon(_make_icon('assets/icon_white/add.png'))
        add_btn.setIconSize(QSize(15, 15))
        add_btn.clicked.connect(self._on_add)

        hdr.addStretch()
        hdr.addWidget(open_btn)
        hdr.addSpacing(8)
        hdr.addWidget(add_btn)
        vl.addLayout(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_container)
        vl.addWidget(scroll, 1)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()

    def _accounts(self) -> list[str]:
        return app_module.get_ordered_accounts()

    def _refresh(self):
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        accounts = self._accounts()
        self._current_order = list(accounts)
        auto_start = app_module.load_auto_start()
        total = len(accounts)

        for idx, name in enumerate(accounts):
            row = QFrame()
            row.setObjectName('config_row')
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 10, 14, 10)
            rl.setSpacing(8)

            lbl = QLabel(name)
            lbl.setStyleSheet('font-size:14px;')

            up_btn = QPushButton('↑')
            up_btn.setObjectName('config_sort_btn')
            up_btn.setCursor(Qt.PointingHandCursor)
            up_btn.setFixedSize(28, 28)
            up_btn.setEnabled(idx > 0)
            up_btn.clicked.connect((lambda checked, n=name: self._on_move(n, -1)))

            down_btn = QPushButton('↓')
            down_btn.setObjectName('config_sort_btn')
            down_btn.setCursor(Qt.PointingHandCursor)
            down_btn.setFixedSize(28, 28)
            down_btn.setEnabled(idx < total - 1)
            down_btn.clicked.connect((lambda checked, n=name: self._on_move(n, 1)))

            auto_btn = QPushButton('自动启动')
            auto_btn.setObjectName('bool_toggle_btn')
            auto_btn.setCheckable(True)
            auto_btn.setChecked(name in auto_start)
            auto_btn.setCursor(Qt.PointingHandCursor)
            auto_btn.setFixedHeight(28)
            auto_btn.toggled.connect((lambda checked, n=name: self._on_toggle_auto_start(n, checked)))

            rename_btn = QPushButton('重命名')
            rename_btn.setObjectName('config_rename_btn')
            rename_btn.setCursor(Qt.PointingHandCursor)
            rename_btn.clicked.connect((lambda checked, n=name: self._on_rename(n)))

            del_btn = QPushButton('删除')
            del_btn.setObjectName('config_del_btn')
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.clicked.connect((lambda checked, n=name: self._on_delete(n)))

            rl.addWidget(lbl, 1)
            rl.addWidget(up_btn)
            rl.addWidget(down_btn)
            rl.addWidget(auto_btn)
            rl.addWidget(rename_btn)
            rl.addWidget(del_btn)

            self._list_layout.insertWidget(self._list_layout.count() - 1, row)

    def _on_move(self, name: str, direction: int):
        accounts = list(self._current_order)
        if name not in accounts:
            return
        idx = accounts.index(name)
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(accounts):
            return

        accounts[new_idx], accounts[idx] = accounts[idx], accounts[new_idx]
        self._current_order = accounts
        app_module.save_config_order(accounts)
        self._refresh()
        self.configs_changed.emit()

    def _on_rename(self, name: str):
        existing = self._accounts()
        dlg = _RenameConfigDialog(name, existing, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        new_name = dlg.get_result()
        if not new_name:
            return
        try:
            os.rename(cfg.config_filepath(name), cfg.config_filepath(new_name))
        except Exception:
            return

        order = app_module.load_config_order()
        if name in order:
            order[order.index(name)] = new_name
            app_module.save_config_order(order)

        self._refresh()
        self.configs_changed.emit()

    def _on_delete(self, name: str):
        if not _confirm_delete(self, name):
            return
        try:
            os.remove(cfg.config_filepath(name))
        except Exception:
            pass

        order = app_module.load_config_order()
        if name in order:
            order.remove(name)
            app_module.save_config_order(order)

        self._refresh()
        self.configs_changed.emit()

    def _on_toggle_auto_start(self, name: str, checked: bool):
        lst = app_module.load_auto_start()
        if checked and name not in lst:
            lst.append(name)
        elif not checked and name in lst:
            lst.remove(name)
        app_module.save_auto_start(lst)

    def _on_open_config_dir(self):
        import subprocess
        subprocess.Popen(['explorer', cfg.config_dir()])

    def _on_add(self):
        existing = self._accounts()
        dlg = _AddConfigDialog(existing, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        new_name, src = dlg.get_result()
        if not new_name:
            return

        new_path = cfg.config_filepath(new_name)
        if os.path.exists(new_path):
            warn = QDialog(self)
            warn.setWindowTitle('名称重复')
            warn.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
            wv = QVBoxLayout(warn)
            wv.setContentsMargins(20, 16, 20, 12)
            wv.addWidget(QLabel(f'配置 "{new_name}" 已存在，请换一个名称。'))

            ok_b = QPushButton('确定')
            ok_b.setFixedSize(72, 30)
            ok_b.clicked.connect(warn.accept)

            wh = QHBoxLayout()
            wh.addStretch()
            wh.addWidget(ok_b)
            wv.addLayout(wh)
            warn.exec()
            return

        if src == '__default__':
            if existing:
                shutil.copy(cfg.config_filepath(existing[0]), new_path)
            else:
                cfg.save_ba_config(new_name, {})
        else:
            shutil.copy(cfg.config_filepath(src), new_path)

        self._refresh()
        self.configs_changed.emit()

class HomeWidget(QWidget):
    theme_set = Signal(bool)
    release_requested = Signal()
    configs_changed = Signal()
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        vl = QVBoxLayout(self)
        vl.setContentsMargins(16, 16, 16, 16)
        vl.setSpacing(0)

        card = QFrame()
        card.setObjectName('home_card')
        card_vl = QVBoxLayout(card)
        card_vl.setContentsMargins(1, 1, 1, 1)
        card_vl.setSpacing(0)

        self._stack = QStackedWidget()
        card_vl.addWidget(self._stack)
        vl.addWidget(card)

        self._home_tab = _HomeTab()
        self._home_tab.theme_set.connect(self.theme_set)
        self._home_tab.release_requested.connect(self.release_requested)
        self._home_tab.configs_changed.connect(self.configs_changed)
        self._home_tab.reset_requested.connect(self.reset_requested)
        self._stack.addWidget(self._home_tab)

        self._stack.addWidget(_HelpTab())

        self._cfg_tab = _ConfigMgmtTab()
        self._cfg_tab.configs_changed.connect(self.configs_changed)
        self._stack.addWidget(self._cfg_tab)

    def set_tab(self, idx: int):
        self._stack.setCurrentIndex(idx)
        if idx == 0:
            self._home_tab.refresh_log_size()

    def update_theme_icon(self, dark: bool):
        self._home_tab.update_theme_icon(dark)
