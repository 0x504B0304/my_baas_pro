import os
import shutil
import time as _time
import datetime
from PySide6.QtCore import Qt, Signal, QThread, QSize, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QTextBrowser, QScrollArea, QFrame, QDialog, QLineEdit, QComboBox, QButtonGroup
from PySide6.QtGui import QPixmap, QIcon, QPalette, QColor
from gui.release_dialog import _RELEASE_HTML
from common import app as app_module
from common import config as app_config
from common import limit
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

def _build_support_html(dark: bool = False) -> str:
    is_support = limit.user_type == 'support'
    ut = '赞助版' if is_support else '开源版'
    uid = limit.user_id if limit.user_id else '加载中...'

    tc = '#dfe6e9' if dark else '#2d3436'
    tc2 = '#b2bec3' if dark else '#636e72'
    cell_sep = '#3a4144' if dark else '#e5e9ed'
    hdr_sep = '#6b6ab0'
    row1 = '#242b2f' if dark else '#ffffff'
    row2 = '#2a3236' if dark else '#f5f6f8'
    qa_q = '#a29bfe' if dark else '#4E4C97'
    ut_color = '#4E4C97' if is_support else '#0984e3'

    def section_title(text: str, color: str = '#4E4C97') -> str:
        bar = '#6c6acd' if dark else color
        tc_ = '#c5c3ff' if dark else color
        return f'<p style="margin:0 0 8px 0; padding:2px 0 2px 10px; border-left:3px solid {bar}; font-size:14px; font-weight:bold; color:{tc_};">{text}</p>'

    def row(label: str, *cells, highlight: bool = False) -> str:
        rbg = row2 if highlight else row1
        tlbl = '#4E4C97' if highlight else tc
        out = f'<tr bgcolor="{rbg}"><td style="padding:8px 12px; font-size:13px; font-weight:bold; color:{tlbl}; white-space:nowrap; border-right:1px solid {cell_sep}; border-bottom:1px solid {cell_sep};">{label}</td>'
        for c in cells:
            out += f'<td style="padding:8px 12px; font-size:13px; color:{tc}; line-height:180%; border-right:1px solid {cell_sep}; border-bottom:1px solid {cell_sep}; vertical-align:top;">{c}</td>'
        return out + '</tr>\n'

    Y = '<font color="#00b894"><b>✔</b></font>'
    N = '<font color="#e17055"><b>✘</b></font>'

    qa_rows = ''
    qa_items = [
        ('支付后多久可以解锁赞助版本?', '24小时自动发货解锁，如遇发货失败可Q群私聊管理（奇犽揍敌客x）', True),
        ('可以绑定多个设备吗?', '不可以，其它设备需要单独赞助', False),
        ('可以换绑设备吗?', '可以免费换1次，请联系我。', False),
        ('赞助后可以退款吗?', '不可以，请考虑好', False),
        ('为什么赞助版本要限制9个账号?', '理论上个人使用，账号9个完全够了，如果你是脚本代肝一天要跑几十上百个账号的话，私聊我吧', False),
    ]
    for i, (q, a, is_warn) in enumerate(qa_items):
        mt = '0' if i == 0 else '10px'
        qc = '#e17055' if is_warn else qa_q
        ac = '#e17055' if is_warn else tc
        qa_rows += f'<p style="margin:{mt} 0 0 0; padding:0;"><span style="font-size:14px; font-weight:bold; color:{qc};">Q：{q}</span><br><span style="font-size:13px; color:{ac};">A：{a}</span></p>\n'

    return ''.join([
        f'\n<div style="font-family: Microsoft YaHei, sans-serif; color:{tc}; padding:14px 16px;">\n\n<!-- 当前版本 -->\n<span style="font-size:14px;">当前版本：<b style="color:{ut_color};">{ut}</b>&nbsp;&nbsp;&nbsp;设备ID：<b style="font-size:15px; color:#00b894;">{uid}</b></span><br>\n<!-- 安全提示 -->\n<span style="display:block; padding:5px 8px; font-size:13px; font-weight:bold; color:#d63031; border:1px solid #d63031; border-left:3px solid #d63031; border-radius:6px;">请妥善保管此设备ID，不要告诉任何人！换绑需要提供设备ID，如果遗失会导致无法换绑！</span>\n\n<table cellspacing="0" cellpadding="0" style="width:95%; margin-bottom:16px; border:1px solid {cell_sep}; border-radius:6px; font-size:13px;">\n<tr bgcolor="#4E4C97">\n  <th style="padding:8px 12px; text-align:left; color:#fff; white-space:nowrap; border-right:1px solid {hdr_sep};">版本</th>\n  <th style="padding:8px 12px; text-align:left; color:#fff; white-space:nowrap; border-right:1px solid {hdr_sep};">Baas</th>\n  <th style="padding:8px 12px; text-align:left; color:#fff; white-space:nowrap; border-right:1px solid {hdr_sep};">每日</th>\n  <th style="padding:8px 12px; text-align:left; color:#fff; white-space:nowrap; border-right:1px solid {hdr_sep};">商店</th>\n  <th style="padding:8px 12px; text-align:left; color:#fff; white-space:nowrap; border-right:1px solid {hdr_sep};">出击</th>\n  <th style="padding:8px 12px; text-align:left; color:#fff; white-space:nowrap; border-right:1px solid {hdr_sep};">自动开图</th>\n  <th style="padding:8px 12px; text-align:left; color:#fff; white-space:nowrap; border-right:1px solid {hdr_sep};">剧情</th>\n  <th style="padding:8px 12px; text-align:left; color:#fff; white-space:nowrap;">最新活动</th>\n</tr>\n',
        row('开源版',
            f'消息推送: {N}<br>每天可运行账号: 1个<br>一键反和谐: {Y}<br>定期删好友: {N}<br>24小时不间断运行: {N}<br>远程技术支持: {N}',
            f'小组: {Y}<br>制造: {N}<br>日程: {Y}<br>咖啡厅: {N}<br>领取邮箱: {Y}<br>工作任务: {Y}',
            f'商店购买: {Y}<br>体力购买: {Y}',
            f'总力战: {N}<br>特殊委托: {Y}<br>通缉悬赏: {Y}<br>战术对抗赛: {Y}<br>学园交流会: {Y}<br>普通关卡-扫荡: {Y}<br>困难关卡-扫荡: {Y}',
            f'普通关卡-开图⭐️⭐️⭐️: {N}<br>困难关卡-开图⭐️⭐️⭐️: {N}<br>困难宝箱💎: {N}<br>挑战三星: {N}',
            f'桃信: {N}<br>主线剧情: {N}',
            f'活动开图⭐️⭐️⭐️: {N}<br>扫荡：{N}<br>加成: {N}<br>成就: {N}<br>抽卡: {N}',
        ),
        row('赞助版',
            f'消息推送: {Y}<br>每天可运行账号: 9个<br>一键反和谐: {Y}<br>定期删好友: {Y}<br>24小时不间断运行: {Y}<br>远程技术支持: {Y}',
            f'小组: {Y}<br>制造: {Y}<br>日程: {Y}<br>咖啡厅: {Y}<br>领取邮箱: {Y}<br>工作任务: {Y}',
            f'商店购买: {Y}<br>体力购买: {Y}',
            f'总力战: {Y}<br>特殊委托: {Y}<br>通缉悬赏: {Y}<br>战术对抗赛: {Y}<br>学园交流会: {Y}<br>普通关卡-扫荡: {Y}<br>困难关卡-扫荡: {Y}',
            f'普通关卡-开图⭐️⭐️⭐️: {Y}<br>困难关卡-开图⭐️⭐️⭐️: {Y}<br>困难宝箱💎: {Y}<br>挑战三星: {Y}',
            f'桃信: {Y}<br>主线剧情: {Y}',
            f'活动开图⭐️⭐️⭐️: {Y}<br>扫荡：{Y}<br>加成: {Y}<br>成就: {Y}<br>抽卡: {Y}',
            highlight=True,
        ),
        '\n</table>\n\n<!-- 常见问题 -->\n',
        section_title('常见问题'),
        '\n',
        qa_rows,
        '\n</div>\n',
    ])

class _RegisterThread(QThread):
    done = Signal()

    def run(self):
        if limit.user_id == '':
            limit.register()
        self.done.emit()

class _PollThread(QThread):
    paid = Signal()

    def run(self):
        for _ in range(200):
            _time.sleep(3)
            limit.register()
            if limit.user_type == 'support':
                self.paid.emit()
                return

class _PayDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('开通赞助版')
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowTitleHint |
            Qt.CustomizeWindowHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint
        )

        vl = QVBoxLayout(self)
        vl.setContentsMargins(20, 16, 20, 16)
        vl.setSpacing(10)

        data = limit.get_price()
        price_val = data.get('price', str(limit.price) if limit.price else '50.00')
        deadline = data.get('time', '')

        if deadline:
            tip_text = f'限时优惠价 <b>{price_val} 元</b>，截止 {deadline}'
        else:
            tip_text = f'当前价格 <b>{price_val} 元</b>'

        tip_lbl = QLabel(tip_text)
        tip_lbl.setTextFormat(Qt.RichText)
        tip_lbl.setAlignment(Qt.AlignCenter)
        tip_lbl.setStyleSheet('font-size:30px; color:red; font-weight:bold;')
        vl.addWidget(tip_lbl)

        auto_lbl2 = QLabel('24小时自动发货，支付后重启脚本立即生效！')
        auto_lbl2.setAlignment(Qt.AlignCenter)
        auto_lbl2.setStyleSheet('font-size:22px; color:red; font-weight:bold;')
        vl.addWidget(auto_lbl2)

        id_lbl = QLabel(f'付款备注ID：<b style="color:#00C166; font-size:17px;">{limit.user_id}</b>')
        id_lbl.setTextFormat(Qt.RichText)
        id_lbl.setAlignment(Qt.AlignCenter)
        id_lbl.setStyleSheet('font-size:13px;')
        vl.addWidget(id_lbl)

        qr_lbl = QLabel()
        qr_lbl.setAlignment(Qt.AlignCenter)
        qr_path = app_config.resource_path(f'web/static/sk/{price_val}.jpg')
        pix = QPixmap(qr_path)
        if not pix.isNull():
            w = pix.width() // 2
            h = pix.height() // 2
            qr_lbl.setPixmap(pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            qr_lbl.setText('（二维码图片未找到）')
        vl.addWidget(qr_lbl)

        self._status_lbl = QLabel()
        self._status_lbl.setAlignment(Qt.AlignCenter)
        self._status_lbl.setStyleSheet('font-size:13px; color:#00b894; font-weight:bold;')
        self._status_lbl.setVisible(False)
        vl.addWidget(self._status_lbl)

        self.adjustSize()

        self._poll = _PollThread()
        self._poll.paid.connect(self._on_paid)
        self._poll.start()

    def _on_paid(self):
        self._status_lbl.setText('🎉 支付成功！请重启脚本使赞助版生效。')
        self._status_lbl.setVisible(True)

    def closeEvent(self, event):
        self._poll.terminate()
        super().closeEvent(event)

class _SupportTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark = False
        vl = QVBoxLayout(self)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        self._promo_bar = QWidget()
        self._promo_bar.setObjectName('promo_bar')
        self._promo_bar.setFixedHeight(56)
        pb = QHBoxLayout(self._promo_bar)
        pb.setContentsMargins(16, 0, 16, 0)
        pb.setSpacing(12)

        self._countdown_lbl = QLabel()
        self._countdown_lbl.setTextFormat(Qt.RichText)
        self._countdown_lbl.setStyleSheet('font-size:14px; color:red; font-weight:bold;')
        self._countdown_lbl.setWordWrap(True)
        pb.addWidget(self._countdown_lbl, 1)

        self._pay_btn = QPushButton('点击开通赞助版')
        self._pay_btn.setObjectName('save_btn')
        self._pay_btn.setFixedHeight(34)
        self._pay_btn.setCursor(Qt.PointingHandCursor)
        self._pay_btn.clicked.connect(self._on_pay)
        pb.addWidget(self._pay_btn)

        vl.addWidget(self._promo_bar)

        self._sep = QFrame()
        self._sep.setObjectName('log_hdr_sep')
        self._sep.setFixedHeight(1)
        vl.addWidget(self._sep)

        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        self._browser.setFrameShape(QFrame.Shape.NoFrame)
        self._browser.setStyleSheet('QTextBrowser { border: none; background: transparent; }')
        _pal = self._browser.palette()
        _pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        self._browser.setPalette(_pal)
        self._browser.viewport().setAutoFillBackground(False)
        vl.addWidget(self._browser, 1)

        self._reg_thread = _RegisterThread()
        self._reg_thread.done.connect(self._on_registered)

        self._cd_timer = QTimer(self)
        self._cd_timer.setInterval(1000)
        self._cd_timer.timeout.connect(self._update_countdown)

        self._blink_visible = True
        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(500)
        self._blink_timer.timeout.connect(self._blink_countdown)

    def showEvent(self, event):
        super().showEvent(event)
        if limit.user_id == '' and not self._reg_thread.isRunning():
            self._browser.setHtml('<p style="padding:12px;">正在获取设备信息...</p>')
            self._promo_bar.setVisible(False)
            self._sep.setVisible(False)
            self._reg_thread.start()
            return
        self._refresh()

    def _on_registered(self):
        self._refresh()

    def set_theme(self, dark: bool):
        self._dark = dark
        self._refresh()

    def _refresh(self):
        self._browser.setHtml(_build_support_html(self._dark))
        is_support = limit.user_type == 'support'
        self._promo_bar.setVisible(not is_support)
        self._sep.setVisible(not is_support)
        if not is_support:
            self._update_countdown()
            self._cd_timer.start()
            self._blink_timer.start()
        else:
            self._cd_timer.stop()
            self._blink_timer.stop()

    def _update_countdown(self):
        if limit.user_type == 'support':
            self._cd_timer.stop()
            self._promo_bar.setVisible(False)
            self._sep.setVisible(False)
            return

        diff = int(limit.ca) - int(_time.time())
        yj = 99 if str(limit.price) == '50' else 50
        price = limit.price if limit.price else '50'

        if diff > 0:
            h, rem = divmod(diff, 3600)
            m, s = divmod(rem, 60)
            self._countdown_lbl.setText(f'<del>原价{yj}元</del> 限时优惠还剩 <b>{h}小时{m}分{s}秒</b>，仅需 <b>{price}元</b> 永久解锁全部功能！')
        else:
            self._countdown_lbl.setText(f'<b>{price}元</b> 永久解锁赞助版本全部功能！')

    def _blink_countdown(self):
        self._blink_visible = not self._blink_visible
        if self._blink_visible:
            self._pay_btn.setStyleSheet('')
        else:
            self._pay_btn.setStyleSheet('QPushButton#save_btn { background: #d63031; color: white; font-weight: bold; }')

    def _on_pay(self):
        dlg = _PayDialog(self)
        dlg.exec()
        if limit.user_type == 'support':
            self._refresh()

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

        self._support_tab = _SupportTab()
        self._stack.addWidget(self._support_tab)

    def set_tab(self, idx: int):
        self._stack.setCurrentIndex(idx)
        if idx == 0:
            self._home_tab.refresh_log_size()

    def update_theme_icon(self, dark: bool):
        self._home_tab.update_theme_icon(dark)
        self._support_tab.set_theme(dark)
