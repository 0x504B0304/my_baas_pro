from __future__ import annotations

import os

from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QBrush, QFont, QIcon, QPixmap
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QListWidget,
    QListWidgetItem,
)

from gui.widgets import SpinnerWidget


class _MenuTree(QTreeWidget):
    """重写 mousePressEvent，阻止点击一级分组时改变选中状态。"""

    def mousePressEvent(self, event: QMouseEvent):
        item = self.itemAt(event.pos())
        if item is not None:
            payload = item.data(0, Qt.UserRole)
            if payload is not None:
                con, fn = payload
                if fn is None:
                    item.setExpanded(not item.isExpanded())
                    return
        super().mousePressEvent(event)


from common import config, process, app as app_module


def _make_icon(path: str) -> QIcon:
    pix = QPixmap(config.resource_path(path))
    ico = QIcon()
    ico.addPixmap(pix, QIcon.Mode.Normal)
    ico.addPixmap(pix, QIcon.Mode.Selected)
    return ico


DASHBOARD_FN = '__dashboard__'
HOME_FN = '__home__'
HELP_FN = '__help__'
SUPPORT_FN = '__support__'
CONFIG_MGMT_FN = '__config_mgmt__'

MENUS = [
    {
        'name': 'Baas',
        'text': 'Baas',
        'child': [
            {'name': 'baas', 'text': 'Baas设置'},
            {'name': 'restart', 'text': '重启设置'},
            {'name': 'env_check', 'text': '环境检查'},
            {'name': 'fhx', 'text': '反和谐'},
            {'name': 'delete_friend', 'text': '删除好友'},
        ],
    },
    {
        'name': 'daily',
        'text': '每日',
        'child': [
            {'name': 'group', 'text': '小组'},
            {'name': 'make', 'text': '制造'},
            {'name': 'schedule', 'text': '日程'},
            {'name': 'cafe', 'text': '咖啡厅'},
        ],
    },
    {
        'name': 'shop',
        'text': '商店',
        'child': [
            {'name': 'shop', 'text': '商店购买'},
            {'name': 'buy_ap', 'text': '购买体力'},
        ],
    },
    {
        'name': 'attack',
        'text': '出击',
        'child': [
            {'name': 'total_war', 'text': '总力战'},
            {'name': 'special_entrust', 'text': '特殊委托'},
            {'name': 'wanted', 'text': '通缉悬赏'},
            {'name': 'tactics_test', 'text': '战术测试'},
            {'name': 'arena', 'text': '战术对抗赛'},
            {'name': 'exchange_meeting', 'text': '学园交流会'},
            {'name': 'normal_task', 'text': '普通关卡-扫荡'},
            {'name': 'hard_task', 'text': '困难关卡-扫荡'},
        ],
    },
    {
        'name': 'exp',
        'text': '开图',
        'child': [
            {'name': 'exp_normal_task', 'text': '普通关卡-开图'},
            {'name': 'exp_hard_task', 'text': '困难关卡-开图'},
        ],
    },
    {
        'name': 'task',
        'text': '任务',
        'child': [
            {'name': 'challenge_normal_task', 'text': '普通关卡-挑战'},
            {'name': 'challenge_hard_task', 'text': '困难关卡-挑战'},
        ],
    },
    {
        'name': 'story',
        'text': '剧情',
        'child': [
            {'name': 'momo_talk', 'text': '桃信'},
            {'name': 'main_story', 'text': '主线剧情'},
        ],
    },
    {
        'name': 'reward',
        'text': '收获',
        'child': [
            {'name': 'mailbox', 'text': '领取邮箱'},
            {'name': 'work_task', 'text': '工作任务'},
        ],
    },
    {
        'name': 'activity',
        'text': '活动',
        'child': [
            {'name': 'cn_activity', 'text': '国服-通用活动'},
            {'name': 'jp_activity', 'text': '日服-通用活动'},
            {'name': 'intl_activity', 'text': '国际服-通用活动'},
            {'name': 'activity_story', 'text': '活动-活动故事'},
        ],
    },
]

FN_NAMES: dict[str, str] = {}
for _g in MENUS:
    for _c in _g['child']:
        FN_NAMES[_c['name']] = _c['text']

_LIGHT_RUN = QColor('#27ae60')
_LIGHT_STOP = QColor('#2d3436')
_LIGHT_GRP = QColor('#636e72')

_DARK_RUN = QColor('#27ae60')
_DARK_STOP = QColor('#dfe6e9')
_DARK_GRP = QColor('#b2bec3')


class Sidebar(QWidget):
    menu_selected = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._accounts = []

        self._acc_items = {}

        self._current_con = ''

        self._selected_item = None

        self._browsing_grp = None

        self._dark_mode = False

        self._icon_right = _make_icon('assets/icon/right.svg')
        self._icon_down = _make_icon('assets/icon/down.svg')
        self._icon_home = _make_icon('assets/icon/home.png')
        self._icon_overview = _make_icon('assets/icon/overview.png')
        self._icon_help = _make_icon('assets/icon/help.png')
        self._icon_diam = _make_icon('assets/icon/diam.png')
        self._icon_settings = _make_icon('assets/icon/config.png')

        self._setup_ui()
        self._build_accounts()

        self._timer = QTimer(self)
        self._timer.setInterval(3000)
        self._timer.timeout.connect(self._refresh_states)
        self._timer.start()

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)

        self._home_btn = QPushButton('主页')
        self._home_btn.setObjectName('sidebar_home_btn')
        self._home_btn.setCheckable(True)
        self._home_btn.setFixedSize(100, 36)
        self._home_btn.setIcon(self._icon_home)
        self._home_btn.setIconSize(QSize(16, 16))
        self._home_btn.setCursor(Qt.PointingHandCursor)
        self._home_btn.clicked.connect(self._on_home_btn_click)
        left.addWidget(self._home_btn)

        self._acc_list = QListWidget()
        self._acc_list.setObjectName('account_list')
        self._acc_list.setFixedWidth(100)
        self._acc_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._acc_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._acc_list.setIconSize(QSize(0, 0))
        self._acc_list.setViewportMargins(0, 0, 0, 0)
        self._acc_list.setCursor(Qt.PointingHandCursor)
        self._acc_list.currentRowChanged.connect(self._on_account_changed)
        left.addWidget(self._acc_list)

        root.addLayout(left)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        root.addWidget(sep)

        self._menu_tree = _MenuTree()
        self._menu_tree.setHeaderHidden(True)
        self._menu_tree.setIndentation(10)
        self._menu_tree.setRootIsDecorated(False)
        self._menu_tree.setIconSize(QSize(14, 14))
        self._menu_tree.setCursor(Qt.PointingHandCursor)
        self._menu_tree.itemClicked.connect(self._on_menu_click)
        self._menu_tree.itemExpanded.connect(self._on_item_expanded)
        self._menu_tree.itemCollapsed.connect(self._on_item_collapsed)
        root.addWidget(self._menu_tree)

    def _add_acc_item(self, con: str):
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 36))
        self._acc_list.addItem(item)

        cell = QWidget()
        cell.setAttribute(Qt.WA_TranslucentBackground)
        hl = QHBoxLayout(cell)
        hl.setContentsMargins(0, 0, 6, 0)
        hl.setSpacing(4)

        lbl = QLabel(con)
        lbl.setFont(QFont('Source Han Sans CN', 13))
        lbl.setAttribute(Qt.WA_TranslucentBackground)

        spinner = SpinnerWidget(14)

        hl.addWidget(lbl, 1)
        hl.addWidget(spinner)

        self._acc_list.setItemWidget(item, cell)
        self._acc_items[con] = (item, lbl, spinner)

    def _build_accounts(self):
        self._acc_list.clear()
        self._acc_items.clear()
        self._accounts.clear()
        self._menu_tree.clear()
        self._selected_item = None

        accounts = app_module.get_ordered_accounts()
        self._accounts = accounts

        for con in accounts:
            self._add_acc_item(con)

        if accounts:
            self._acc_list.setCurrentRow(0)

        self._refresh_states()

    def _build_menu(self, con: str):
        self._menu_tree.clear()
        self._selected_item = None
        self._browsing_grp = None

        dash = QTreeWidgetItem(['总览'])
        dash.setIcon(0, self._icon_overview)
        dash.setData(0, Qt.UserRole, (con, DASHBOARD_FN))
        self._menu_tree.addTopLevelItem(dash)

        for group in MENUS:
            grp_item = QTreeWidgetItem([group['text']])
            grp_item.setIcon(0, self._icon_right)
            grp_item.setData(0, Qt.UserRole, (con, None))
            grp_item.setData(0, Qt.UserRole + 1, group['text'])
            grp_item.setForeground(0, self._col_grp)
            grp_item.setFlags(grp_item.flags() & ~Qt.ItemIsSelectable)

            for child in group['child']:
                c = QTreeWidgetItem([child['text']])
                c.setData(0, Qt.UserRole, (con, child['name']))
                grp_item.addChild(c)

            self._menu_tree.addTopLevelItem(grp_item)

    def _build_home_menu(self):
        self._menu_tree.clear()
        self._selected_item = None
        self._browsing_grp = None

        for fn, text, icon in (
            (HOME_FN, '主页', self._icon_home),
            (HELP_FN, '帮助教程', self._icon_help),
            (CONFIG_MGMT_FN, '配置管理', self._icon_settings),
            (SUPPORT_FN, '关于赞助', self._icon_diam),
        ):
            item = QTreeWidgetItem([text])
            item.setIcon(0, icon)
            item.setData(0, Qt.UserRole, ('', fn))
            self._menu_tree.addTopLevelItem(item)

        first = self._menu_tree.topLevelItem(0)
        self._menu_tree.setCurrentItem(first)
        self._selected_item = first

    @property
    def _col_run(self):
        if self._dark_mode:
            return _DARK_RUN
        return _LIGHT_RUN

    @property
    def _col_stop(self):
        if self._dark_mode:
            return _DARK_STOP
        return _LIGHT_STOP

    @property
    def _col_grp(self):
        if self._dark_mode:
            return _DARK_GRP
        return _LIGHT_GRP

    def set_theme(self, dark: bool):
        self._dark_mode = dark
        if dark:
            base = 'assets/icon_white'
            ext = 'png'
        else:
            base = 'assets/icon'
            ext = 'svg'

        self._icon_right = _make_icon(f'{base}/right.{ext}')
        self._icon_down = _make_icon(f'{base}/down.{ext}')
        self._icon_home = _make_icon(f'{base}/home.png')
        self._icon_help = _make_icon(f'{base}/help.png')
        self._icon_diam = _make_icon(f'{base}/diam.png')
        self._icon_settings = _make_icon(f'{base}/config.png')

        self._home_btn.setIcon(self._icon_home)
        self._refresh_states()

        for i in range(self._menu_tree.topLevelItemCount()):
            item = self._menu_tree.topLevelItem(i)
            if item is None:
                continue
            payload = item.data(0, Qt.UserRole)
            if payload and payload[0] == '' and payload[1] in (HOME_FN, HELP_FN, SUPPORT_FN, CONFIG_MGMT_FN):
                icon_map = {
                    HOME_FN: self._icon_home,
                    HELP_FN: self._icon_help,
                    SUPPORT_FN: self._icon_diam,
                    CONFIG_MGMT_FN: self._icon_settings,
                }
                item.setIcon(0, icon_map[payload[1]])
            elif item.data(0, Qt.UserRole + 1):
                if item.isExpanded():
                    item.setIcon(0, self._icon_down)
                else:
                    item.setIcon(0, self._icon_right)
                item.setForeground(0, self._col_grp)

    def _refresh_states(self):
        for con, (item, lbl, spinner) in self._acc_items.items():
            running = process.m.state_process(con)
            if running:
                lbl.setStyleSheet(f'color: {self._col_run.name()};')
            else:
                lbl.setStyleSheet(f'color: {self._col_stop.name()};')
            spinner.set_running(running)
            spinner.setVisible(running)

    def _on_account_changed(self, row: int):
        if row < 0 or row >= len(self._accounts):
            return

        self._home_btn.setChecked(False)

        prev_fn = None
        if self._selected_item is not None:
            payload = self._selected_item.data(0, Qt.UserRole)
            if payload and payload[1] not in (None, DASHBOARD_FN):
                prev_fn = payload[1]

        con = self._accounts[row]
        self._current_con = con
        self._build_menu(con)

        if prev_fn:
            self.select_menu(prev_fn)
            if self._selected_item is not None:
                self.menu_selected.emit(con, prev_fn)
            return

        if self._menu_tree.topLevelItemCount() > 0:
            dash_item = self._menu_tree.topLevelItem(0)
            self._menu_tree.setCurrentItem(dash_item)
            self._selected_item = dash_item

        self.menu_selected.emit(con, DASHBOARD_FN)

    def _on_home_btn_click(self):
        self._home_btn.setChecked(True)
        self._acc_list.blockSignals(True)
        self._acc_list.setCurrentRow(-1)
        self._acc_list.blockSignals(False)
        self._current_con = ''
        self._build_home_menu()
        self.menu_selected.emit('', HOME_FN)

    def _on_menu_click(self, item: QTreeWidgetItem, _col: int):
        payload = item.data(0, Qt.UserRole)
        if payload is None:
            return
        con, fn = payload
        if fn is None:
            return

        old_grp = self._selected_item.parent() if self._selected_item else None
        new_grp = item.parent()

        if fn == DASHBOARD_FN:
            if old_grp is not None:
                old_grp.setExpanded(False)
            if self._browsing_grp is not None and self._browsing_grp is not old_grp:
                self._browsing_grp.setExpanded(False)
            self._browsing_grp = None
        else:
            if old_grp is not None and old_grp is not new_grp:
                old_grp.setExpanded(False)
            self._browsing_grp = new_grp

        self._menu_tree.setCurrentItem(item)
        self._selected_item = item
        self.menu_selected.emit(con, fn)

    def _on_item_expanded(self, item: QTreeWidgetItem):
        base = item.data(0, Qt.UserRole + 1)
        if not base:
            return
        item.setText(0, base)
        item.setIcon(0, self._icon_down)

        sel_grp = self._selected_item.parent() if self._selected_item else None

        if self._browsing_grp is not None:
            if self._browsing_grp is not item:
                if self._browsing_grp is not sel_grp:
                    self._browsing_grp.setExpanded(False)
        self._browsing_grp = item

    def _on_item_collapsed(self, item: QTreeWidgetItem):
        base = item.data(0, Qt.UserRole + 1)
        if base:
            item.setText(0, base)
            item.setIcon(0, self._icon_right)
        if self._browsing_grp is item:
            self._browsing_grp = None

    def accounts(self) -> list[str]:
        return list(self._accounts)

    def first_account(self) -> str:
        if self._accounts:
            return self._accounts[0]
        return ''

    def select_home(self):
        self._on_home_btn_click()

    def select_dashboard(self, con: str):
        try:
            idx = self._accounts.index(con)
        except ValueError:
            return
        if self._acc_list.currentRow() != idx:
            self._acc_list.setCurrentRow(idx)
        if self._menu_tree.topLevelItemCount() > 0:
            dash_item = self._menu_tree.topLevelItem(0)
            self._menu_tree.setCurrentItem(dash_item)
            self._selected_item = dash_item

    def select_menu(self, fn: str):
        for i in range(self._menu_tree.topLevelItemCount()):
            item = self._menu_tree.topLevelItem(i)
            payload = item.data(0, Qt.UserRole)
            if payload and payload[1] == fn:
                self._menu_tree.setCurrentItem(item)
                self._selected_item = item
                return
            for j in range(item.childCount()):
                child = item.child(j)
                payload = child.data(0, Qt.UserRole)
                if payload and payload[1] == fn:
                    item.setExpanded(True)
                    self._menu_tree.setCurrentItem(child)
                    self._selected_item = child
                    return

    def refresh_accounts(self):
        accounts = app_module.get_ordered_accounts()
        self._accounts = accounts

        self._acc_list.blockSignals(True)
        self._acc_list.clear()
        self._acc_items.clear()

        for con in accounts:
            self._add_acc_item(con)

        self._acc_list.blockSignals(False)
        self._refresh_states()
