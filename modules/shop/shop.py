import time
from common import stage, image, color
from modules.baas import home

shop_position = {
    'cn': {'general': (150, 150), 'arena': (150, 533), 'swipe': False},
    'jp': {'general': (150, 150), 'arena': (150, 360), 'swipe': True},
    'intl': {'general': (150, 150), 'arena': (150, 280), 'swipe': True},
}

goods_position = {
    1: (650, 200), 2: (805, 200), 3: (960, 200), 4: (1110, 200),
    5: (650, 460), 6: (805, 460), 7: (960, 460), 8: (1110, 460),
    9: (650, 200), 10: (805, 200), 11: (960, 200), 12: (1110, 200),
    13: (650, 460), 14: (805, 460), 15: (960, 460), 16: (1110, 460),
    17: (650, 200),
    18: (805, 200), 19: (960, 200), 20: (1110, 200),
    21: (650, 460), 22: (805, 460), 23: (960, 460), 24: (1110, 460),
}

goods_position_intl = {
    1: (650, 200), 2: (805, 200), 3: (960, 200), 4: (1110, 200),
    5: (650, 460), 6: (805, 460), 7: (960, 460), 8: (1110, 460),
    9: (650, 200), 10: (805, 200), 11: (960, 200), 12: (1110, 200),
    13: (650, 460), 14: (805, 460), 15: (960, 460), 16: (1110, 460),
    17: (650, 200),
    18: (805, 200), 19: (960, 200), 20: (1110, 200),
    21: (650, 460), 22: (805, 460), 23: (960, 460), 24: (1110, 460),
    25: (650, 460), 26: (805, 460), 27: (960, 460), 28: (1110, 460),
}


def to_shop(self):
    pos = {'home_student': (793, 645)}
    home.to_menu(self, 'shop_menu', pos)


def to_goods_tab(self, shop):
    cl = shop_position[self.game_server][shop]
    need_swipe = shop_position[self.game_server]['swipe']
    if need_swipe and shop == 'arena':
        self.swipe(115, 460, 115, 0, 0.1)
        time.sleep(0.1)
        self.swipe(115, 460, 115, 0, 0.1)
        time.sleep(0.1)
        self.swipe(115, 460, 115, 0, 0.1)
        time.sleep(0.5)
    color.wait_rgb_similar(self, (cl[0] - 135, cl[1]), (45, 70, 99), cl=cl)


def start(self):
    home.go_home(self)
    to_shop(self)
    buy_goods(self)
    home.go_home(self)


def buy_goods(self):
    """
    刷新并购买商品
    """
    shops = ['general', 'arena']
    for shop in shops:
        if not self.tc[shop]['enable']:
            self.logger.error('当前商店{0}设置为: 不启用'.format(shop))
            continue
        to_goods_tab(self, shop)
        rst = start_buy(self, shop)
        if rst == 'not-coin':
            continue
        i = 0
        while refresh_shop(self, shop, i):
            i += 1
            rst = start_buy(self, shop)
            if rst == 'not-coin':
                break


def start_buy(self, shop):
    """
    开始购买商品
    """
    choose_goods(self, self.tc[shop]['goods'], shop)
    if not image.compare_image(self, 'shop_choose-buy', 1):
        self.logger.error('没有选中道具')
        return None

    if not color.check_rgb(self, (1200, 682), (251, 231, 68)):
        self.logger.error('货币不足，无法购买')
        return 'not-coin'

    pos = {'shop_choose-buy': (1166, 661)}
    ends = ('shop_buy-confirm1', 'shop_buy-confirm2')
    image.detect(self, ends, pos)

    p = {
        'intl': (760, 580, False),
        'jp': (760, 560, False),
        'cn': (760, 580, False),
    }
    self.click(*p[self.game_server])

    stage.close_prize_info(self, True)


def choose_goods(self, goods, shop):
    time.sleep(0.5)
    goods = sorted(goods)
    self.logger.warning('开始点击所需商品')
    swipe1 = False
    swipe2 = False
    swipe3 = False
    for g in goods:
        if g > 8 and not swipe1:
            swipe1 = True
            stage.screen_swipe(self, False, (933, 605, 933, 50, 0.6))
        if g > 16 and not swipe2:
            swipe2 = True
            stage.screen_swipe(self, False, (933, 605, 933, 50, 0.6))
        if g > 24 and not swipe3:
            swipe3 = True
            stage.screen_swipe(self, False, (933, 605, 933, 50, 0.1))
        time.sleep(0.2)
        region_position = {
            'cn': goods_position,
            'jp': goods_position_intl,
            'intl': goods_position_intl,
        }
        if g not in region_position[self.game_server]:
            continue
        self.click(*region_position[self.game_server][g], False)


def refresh_shop(self, shop, i):
    need_count = self.tc[shop]['count']
    purchased_count = 4 - calc_surplus_count(self)
    self.logger.warning('{0}商店 需要购买次数:{1}次 当前已购买次数{2}次'.format(shop, need_count, purchased_count))

    if need_count <= purchased_count or i > 3:
        home.click_house_under(self)
        return False

    self.click(765, 460, False)
    return True


def calc_surplus_count(self):
    ends = {('shop_buy2', 0.9), 'shop_not-refresh', ('shop_buy3', 0.9), ('shop_buy1', 0.9)}
    end = image.detect(self, ends, (1168, 660), 0.5)
    if end == 'shop_not-refresh':
        return 0
    return int(end.replace('shop_buy', ''))
