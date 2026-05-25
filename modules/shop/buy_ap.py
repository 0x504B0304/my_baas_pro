from common import image, stage
from modules.baas import home


def to_buy_ap(self):
    p = (619, 37)
    if self.game_server == 'jp':
        p = (638, 35)
    possible = {'home_student': p}
    end = ('buy_ap_limited', 'buy_ap_notice')
    return image.detect(self, end, possible, pre_argv=home.go_home(self))


def start(self):
    home.go_home(self)
    res = to_buy_ap(self)
    if res == 'buy_ap_limited':
        home.go_home(self)
        return

    need_count = self.tc['config']['count']
    purchased_count = 20 - calc_surplus_count(self)
    self.logger.warning('需要购买次数:{0}次 当前已购买次数{1}次'.format(need_count, purchased_count))

    if need_count <= purchased_count:
        home.go_home(self)
        return

    buy_count = need_count - purchased_count
    self.click(806, 345, False, min(buy_count, 3) - 1)
    self.click(770, 501, False)

    if image.compare_image(self, 'buy_ap_confirm', 5):
        self.click(768, 485, False)

    if image.compare_image(self, 'buy_ap_limited', 5):
        self.logger.warning('体力超出持有上限,延迟运行本任务')
        self.finish_seconds = 30
        home.go_home(self)
        return

    try:
        stage.close_prize_info(self, False, True)
        if buy_count > 3:
            return start(self)
    except ValueError:
        self.logger.info('次数识别失败')

    home.go_home(self)


def calc_surplus_count(self):
    """
    计算剩余购买次数,这里必须用图片匹配才能精准,用文字识别小数字必出bug
    """
    for i in range(20, 0, -1):
        if image.compare_image(self, 'buy_ap_buy{0}'.format(i), 0, 0.9):
            return i
    return 0
