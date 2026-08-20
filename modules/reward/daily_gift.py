from common import image, ocr, stage
from modules.baas import home


def _click_box_center(self, name):
    x1, y1, x2, y2 = image.get_box(self, name)
    self.click((x1 + x2) // 2, (y1 + y2) // 2, False)


def to_daily_gift(self):
    if self.game_server != 'cn':
        self.logger.warning('每日礼包领取当前仅支持国服')
        return False

    home.go_home(self)
    self.click(979, 37, False)
    if not image.detect(self, 'daily_gift_shop-title', retry=20, rate=0.5):
        self.logger.warning('未能打开购买青辉石界面')
        return False

    _click_box_center(self, 'daily_gift_gift-tab')
    if image.detect(
        self,
        (('daily_gift_free-available', 0.9), ('daily_gift_free-unavailable', 0.9)),
        retry=5, rate=0.5,
    ):
        return True

    self.logger.warning('未能打开礼包页')
    return False


def _status_text(self):
    if self.game_server != 'cn' or not hasattr(self, 'ocr'):
        return ''
    out = ocr.screenshot_cut_get_text(self, (300, 415, 475, 446), need_loading=False)
    return ''.join(t.get('text', '') for t in out)


def is_free_gift_available(self):
    if image.compare_image(self, 'daily_gift_free-available', 0, 0.9):
        return True
    if image.compare_image(self, 'daily_gift_free-unavailable', 0, 0.9):
        return False

    text = _status_text(self)
    self.logger.info('daily gift status OCR:%s', text)
    if '0' in text:
        return False
    if '1' in text:
        return True
    return False


def buy_free_gift(self):
    if not is_free_gift_available(self):
        self.logger.warning('每日免费礼包当前不可领取')
        return

    _click_box_center(self, 'daily_gift_free-button')
    if not image.detect(self, 'daily_gift_confirm-title', retry=20, rate=0.5):
        self.logger.warning('未检测到每日免费礼包购买确认框')
        return

    if not image.compare_image(self, 'daily_gift_confirm-free', 0, 0.65):
        self.logger.warning('每日礼包价格不是免费，取消购买')
        _click_box_center(self, 'daily_gift_cancel-button')
        return

    if image.compare_image(self, 'daily_gift_confirm-button', 0, 0.65):
        _click_box_center(self, 'daily_gift_confirm-button')
    else:
        self.logger.warning('未检测到每日免费礼包确认按钮')
        return

    stage.close_prize_info(self, True)


def start(self):
    if to_daily_gift(self):
        buy_free_gift(self)
    home.go_home(self)
