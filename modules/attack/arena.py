import time
from common import ocr, color, stage, image
from modules.baas import home

finish_seconds = 55


def to_arena(self):
    pos = {
        'home_student': (1200, 573),
        'home_bus': (880, 580),
        'arena_help': (1015, 130),
    }
    home.to_menu(self, 'arena_menu', pos, retry=120)


def do_fight(self):
    pos = {
        'arena_menu': (769, 251),
    }
    image.detect(self, 'arena_war-force', pos)
    pos = {
        'arena_war-force': (646, 571),
    }
    image.detect(self, 'fight_edit-attack-force', pos)


def start(self):
    home.go_home(self)
    to_arena(self)
    start_fight(self)
    home.go_home(self)


def get_prize(self):
    image.detect(self, 'arena_id', cl=(1235, 82))
    self.logger.warning('开始领取每日奖励')
    if color.check_rgb(self, (320, 400)):
        self.click(353, 385)
        stage.close_prize_info(self)
    if color.check_rgb(self, (330, 480)):
        self.click(348, 465)
        stage.close_prize_info(self)


def start_fight(self, wait=False):
    time.sleep(0.5)
    if image.compare_image(self, 'arena_0-5', 0):
        self.logger.error('入场券不足')
        get_prize(self)
        return
    if wait or not image.compare_image(self, 'arena_cd', 0):
        self.finish_seconds = finish_seconds
        return
    choose_enemy(self)
    do_fight(self)
    image.compare_image(self, 'arena_skip', cl=(1239, 600), rate=1)
    image.compare_image(self, 'fight_edit-attack-force', cl=(1163, 658), rate=1, n=True)
    image.detect(self, 'arena_id', cl=(1235, 82))
    if self.tc['config']['get_type'] == 'one':
        self.sleep(1)
        self.finish_seconds = 0
        self.logger.error('当前设置只打一次，直接领取奖励。并且短时间内不再继续进攻')
        get_prize(self)
        return
    start_fight(self, True)


def choose_enemy(self):
    less_level = int(self.tc['config']['less_level'])

    area = image.get_box(self, 'arena_my-lv')
    try:
        my_lv = float(ocr.screenshot_get_text(self, area, self.ocrNum))
    except Exception:
        my_lv = 100

    refresh = 0
    while True:
        if refresh > self.tc['config']['max_refresh']:
            less_level -= 1
            refresh = 0
            continue

        area = image.get_box(self, 'arena_enemy-lv')
        try:
            enemy_lv = float(ocr.screenshot_get_text(self, area, self.ocrNum))
        except Exception:
            enemy_lv = 0

        self.logger.info('我的等级{0} 对手等级 {1}'.format(my_lv, enemy_lv))
        if enemy_lv + less_level <= my_lv:
            return

        self.logger.warning('开始更换对手')
        self.double_click(1158, 145)
        refresh += 1
