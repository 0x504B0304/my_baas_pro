import time
from common import image, color, limit
from common import stage
from modules.baas import home
from modules.exp.normal_task import exp_normal_task
from modules.story import main_story

current_men = 'cn_jmjh_menu'
position = {}
stage_data = {}


def to_activity_task(self):
    pos = {
        'momo_talk_menu': (1205, 42), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516), 'normal_task_task-info': (1084, 142),
        'normal_task_buy-ap-window': (920, 166), 'home_student': (1200, 573),
        'home_bus': (100, 160), 'new_year_guide': (1184, 156),
        'home_new-players': (1234, 26), current_men: (500, 640),
        'god_cross_task': (55, 37),
    }
    image.detect(self, 'cn_jmjh_task', pos)
    return None


def to_activity_page(self):
    pos = {
        'momo_talk_menu': (1205, 42), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516), 'normal_task_task-info': (1084, 142),
        'normal_task_buy-ap-window': (920, 166), 'home_student': (1200, 573),
        'home_bus': (100, 160), 'new_year_guide': (1184, 156),
        'home_new-players': (1234, 26), 'god_cross_task': (55, 37),
        'cn_jmjh_task': (50, 35), 'cn_jmjh_shop': (50, 35),
    }
    image.detect(self, current_men, pos)
    return None


def to_shop(self):
    pos = {current_men: (337, 644), 'cn_jmjh_occupy': (60, 36)}
    image.detect(self, 'cn_jmjh_shop', pos)
    return None


def to_occupy_menu(self):
    pos = {
        current_men: (950, 580), 'momo_talk_menu': (1205, 42),
        'momo_talk_skip': (1212, 116), 'momo_talk_confirm-skip': (770, 516),
        'normal_task_task-info': (1084, 142), 'normal_task_buy-ap-window': (920, 166),
        'home_student': (1200, 573), 'home_bus': (100, 160),
        'new_year_guide': (1184, 156), 'home_new-players': (1234, 26),
        'god_cross_task': (55, 37), 'cn_jmjh_task': (50, 35),
        'cn_jmjh_shop': (50, 35),
    }
    image.detect(self, 'cn_jmjh_occupy', pos)
    return None


def start(self):
    if self.game_server != 'cn':
        return None
    home.go_home(self)
    get_prize(self)
    start_occupy(self)
    start_occupy_all(self)
    finish_task(self)
    home.go_home(self)
    return None


def finish_task(self):
    self.md = self.tc
    self.md['occupy']['enable'] = False
    return None


def get_prize(self):
    self.log_title('开始国服活动-领取奖励')
    to_activity_task(self)
    if not color.check_rgb(self, (1085, 685), (249, 237, 73)):
        self.logger.error('没有奖励可以领取')
        return None
    self.click(1156, 666)
    stage.close_prize_info(self)
    return None


first = True


def start_occupy(self):
    if not self.tc['occupy']['enable']:
        return None
    self.log_title('开始国服活动-路线开图')
    to_occupy_menu(self)
    if first:
        time.sleep(3)
        to_occupy_menu(self)
    first = False
    stage = str(self.tc['occupy']['stage'])
    region_position = {
        '1': ((640, 300), region1),
        '2': ((640, 250), region2),
        '3': ((640, 190), region3),
        '4': ((640, 140), region4),
    }
    to_occupy_menu(self)
    self.click(650, 75, False)
    self.sleep(1)
    self.click(*region_position[stage][0], False)
    self.sleep(1)
    region_position[stage][1](self)
    return None


def start_occupy_all(self):
    if not self.tc['occupy_all']['enable']:
        return None
    self.log_title('开始国服活动-全地区开图')
    to_occupy_menu(self)
    stage_list = self.tc['occupy_all']['stage']
    region_position = {
        '1': ((640, 300), region_all1),
        '2': ((640, 250), region_all2),
        '3': ((640, 190), region_all3),
        '4': ((640, 140), region_all4),
    }
    for task in stage_list:
        to_occupy_menu(self)
        self.click(650, 75, False)
        self.sleep(1)
        self.click(*region_position[task][0], False)
        self.sleep(1)
        region_position[task][1](self)
    return None


def wait_fight_over(self):
    possible = {
        'main_story_fight-confirm': (1168, 659), 'main_story_fight-fail': (647, 655),
        'fight_pass-confirm': (1170, 666), 'fight_task-finish-confirm': (1033, 666),
        'fight_prize-confirm': (776, 655), 'fight_prize-confirm1': (645, 670),
        'fight_prize-confirm2': (775, 660), 'momo_talk_menu': (1205, 42),
        'momo_talk_skip': (1212, 116), 'momo_talk_confirm-skip': (770, 516),
        'cn_activity_unlock': (1259, 62), 'cm_get-prize': (650, 640),
    }
    image.detect(self, 'cn_jmjh_occupy', possible)
    return None


def do_fight(self, x, y, choose=False):
    self.click(x, y, False)
    time.sleep(1)
    self.click(x - 100, y + 25, False)
    time.sleep(1)
    if (image.compare_image(self, 'cn_jmjh_region', 5, retry=5) or
            image.compare_image(self, 'cn_jmjh_jdyy', 5, retry=5)):
        self.logger.error('已被占领...')
        return None
    self.click(645, 540, False)
    self.click(645, 515, False)
    pos = {
        'momo_talk_menu': (1205, 42), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516),
    }
    image.detect(self, 'normal_task_force-edit', pos)
    if choose:
        stage.choose_role(self, '1')
    image.compare_image(self, 'fight_force-edit', threshold=1, cl=(1160, 650), n=True)
    main_story.auto_fight(self)
    self.logger.info('强制等待5秒...')
    time.sleep(5)
    wait_fight_over(self)
    return None


def do_occupy(self, x, y):
    self.click(x, y, False)
    self.sleep(1)
    self.click(x - 100, y + 20, False)
    self.sleep(1)
    if (image.compare_image(self, 'cn_jmjh_region', 5, retry=5) or
            image.compare_image(self, 'cn_jmjh_jdyy', 5, retry=5)):
        self.logger.error('已被占领...')
        return None
    self.click(770, 500, False)
    return None


def do_operation(self, x, y):
    self.click(x, y)
    self.sleep(1)
    self.click(x - 100, y + 20)
    self.sleep(1)
    stage.wait_loading(self)
    self.sleep(2)
    self.click(480, 405)
    self.sleep(2)
    self.click(720, 580)
    self.sleep(2)
    self.click(1130, 580)
    self.sleep(2)
    self.click(770, 500)
    self.sleep(1)
    home.click_house_under(self)
    return None


def do_scan(self, x, y, count):
    self.click(x, y)
    self.sleep(1)
    self.click(x - 100, y + 20)
    self.sleep(1)
    stage.wait_loading(self)
    self.sleep(2)
    self.click(1033, 320, False, count - 1, 0.6)
    self.sleep(1)
    self.click(935, 535)
    self.sleep(1)
    self.click(765, 500)
    stage.start_scan(self)
    return None


def do_shop(self, p1, p2):
    to_shop(self)
    self.sleep(1)
    self.click(*p1)
    self.sleep(1)
    stage.screen_swipe(self, 0, False, (926, 590, 926, 0, 0.1), threshold2=False, reset=False)
    self.sleep(1)
    self.click(*p2)
    self.sleep(1)
    self.click(770, 480)
    stage.close_prize_info(self)
    return None


def start_action(self, data):
    i = 1
    for action in data:
        self.logger.info('开始第{0}次行动，{1}'.format(i, action))
        if action['t'] == 'fight':
            do_fight(self, *action['p'], i == 1)
        elif action['t'] == 'fight_boss':
            do_fight(self, *action['p'], i == 1)
        elif action['t'] == 'occupy':
            do_occupy(self, *action['p'])
        elif action['t'] == 'operation':
            do_operation(self, *action['p'])
        elif action['t'] == 'scan':
            do_scan(self, *action['p'], action['count'])
        elif action['t'] == 'shop':
            do_shop(self, action['p'], action['p2'])
        elif action['t'] == 'blank':
            self.click(*action['p'])
        i = i + 1
        home.click_house_under(self)
        time.sleep(2)
        home.click_house_under(self)
    return None


def region_all1(self):
    self.log_title('开始国服活动-区域1')
    data = [
        {'t': 'fight', 'p': (640, 555)}, {'t': 'occupy', 'p': (585, 480)},
        {'t': 'occupy', 'p': (640, 400)}, {'t': 'fight', 'p': (690, 330)},
        {'t': 'fight', 'p': (590, 330)}, {'t': 'fight_boss', 'p': (640, 270)},
    ]
    check_ap(self, data, True)
    start_action(self, data)
    return None


def region_all2(self):
    self.log_title('开始国服活动-区域2')
    data = [
        {'t': 'occupy', 'p': (640, 695)}, {'t': 'fight', 'p': (585, 620)},
        {'t': 'fight', 'p': (640, 540)}, {'t': 'occupy', 'p': (690, 470)},
        {'t': 'fight', 'p': (745, 395)}, {'t': 'occupy', 'p': (790, 330)},
        {'t': 'fight', 'p': (890, 330)}, {'t': 'blank', 'p': (890, 330)},
        {'t': 'fight', 'p': (690, 320)}, {'t': 'occupy', 'p': (480, 620)},
        {'t': 'occupy', 'p': (535, 545)}, {'t': 'occupy', 'p': (590, 470)},
        {'t': 'occupy', 'p': (640, 400)}, {'t': 'occupy', 'p': (590, 320)},
        {'t': 'occupy', 'p': (740, 550)}, {'t': 'occupy', 'p': (790, 470)},
        {'t': 'occupy', 'p': (840, 400)}, {'t': 'occupy', 'p': (480, 470)},
        {'t': 'occupy', 'p': (540, 400)}, {'t': 'occupy', 'p': (795, 620)},
        {'t': 'occupy', 'p': (430, 400)}, {'t': 'occupy', 'p': (380, 320)},
        {'t': 'fight', 'p': (850, 540)}, {'t': 'fight', 'p': (430, 540)},
        {'t': 'fight', 'p': (480, 320)}, {'t': 'fight', 'p': (690, 620)},
        {'t': 'fight', 'p': (440, 250)}, {'t': 'fight', 'p': (850, 250)},
        {'t': 'fight_boss', 'p': (640, 270)},
    ]
    check_ap(self, data, True)
    start_action(self, data)
    return None


def region_all3(self):
    self.log_title('开始国服活动-区域3')
    data = [
        {'t': 'occupy', 'p': (640, 695)}, {'t': 'fight', 'p': (585, 620)},
        {'t': 'fight', 'p': (640, 540)}, {'t': 'fight', 'p': (690, 470)},
        {'t': 'fight', 'p': (740, 390)}, {'t': 'fight', 'p': (690, 320)},
        {'t': 'fight', 'p': (590, 320)}, {'t': 'occupy', 'p': (740, 540)},
        {'t': 'occupy', 'p': (790, 470)}, {'t': 'occupy', 'p': (850, 400)},
        {'t': 'occupy', 'p': (790, 330)}, {'t': 'occupy', 'p': (640, 400)},
        {'t': 'occupy', 'p': (540, 400)}, {'t': 'occupy', 'p': (480, 320)},
        {'t': 'occupy', 'p': (480, 620)}, {'t': 'occupy', 'p': (800, 620)},
        {'t': 'occupy', 'p': (850, 550)}, {'t': 'occupy', 'p': (950, 550)},
        {'t': 'occupy', 'p': (1000, 470)}, {'t': 'occupy', 'p': (900, 330)},
        {'t': 'occupy', 'p': (430, 400)}, {'t': 'occupy', 'p': (320, 400)},
        {'t': 'occupy', 'p': (270, 470)}, {'t': 'occupy', 'p': (270, 470)},
        {'t': 'occupy', 'p': (325, 545)}, {'t': 'fight', 'p': (700, 620)},
        {'t': 'fight', 'p': (530, 540)}, {'t': 'fight', 'p': (430, 540)},
        {'t': 'fight', 'p': (380, 460)}, {'t': 'fight', 'p': (480, 470)},
        {'t': 'fight', 'p': (590, 470)}, {'t': 'fight', 'p': (900, 470)},
        {'t': 'fight', 'p': (950, 400)}, {'t': 'fight', 'p': (400, 320)},
        {'t': 'fight', 'p': (425, 265)}, {'t': 'fight', 'p': (840, 250)},
        {'t': 'fight_boss', 'p': (640, 270)},
    ]
    check_ap(self, data, True)
    start_action(self, data)
    return None


def region_all4(self):
    self.log_title('开始国服活动-区域4')
    data = [
        {'t': 'occupy', 'p': (640, 695)}, {'t': 'fight', 'p': (690, 615)},
        {'t': 'occupy', 'p': (740, 540)}, {'t': 'fight', 'p': (790, 460)},
        {'t': 'occupy', 'p': (790, 610)}, {'t': 'occupy', 'p': (850, 540)},
        {'t': 'occupy', 'p': (950, 540)}, {'t': 'occupy', 'p': (900, 620)},
        {'t': 'occupy', 'p': (1000, 470)}, {'t': 'occupy', 'p': (840, 390)},
        {'t': 'occupy', 'p': (790, 320)}, {'t': 'occupy', 'p': (740, 390)},
        {'t': 'occupy', 'p': (640, 390)}, {'t': 'occupy', 'p': (680, 460)},
        {'t': 'fight', 'p': (890, 460)}, {'t': 'fight', 'p': (950, 390)},
        {'t': 'fight', 'p': (900, 320)}, {'t': 'fight', 'p': (680, 320)},
        {'t': 'fight', 'p': (580, 320)}, {'t': 'fight', 'p': (530, 390)},
        {'t': 'fight', 'p': (590, 460)}, {'t': 'fight', 'p': (540, 540)},
        {'t': 'fight', 'p': (640, 540)}, {'t': 'fight', 'p': (580, 610)},
        {'t': 'occupy', 'p': (480, 610)}, {'t': 'occupy', 'p': (370, 610)},
        {'t': 'occupy', 'p': (430, 540)}, {'t': 'occupy', 'p': (480, 460)},
        {'t': 'occupy', 'p': (430, 390)}, {'t': 'occupy', 'p': (480, 310)},
        {'t': 'occupy', 'p': (330, 390)}, {'t': 'occupy', 'p': (280, 320)},
        {'t': 'occupy', 'p': (270, 460)}, {'t': 'fight', 'p': (320, 530)},
        {'t': 'fight', 'p': (380, 460)}, {'t': 'fight', 'p': (380, 320)},
        {'t': 'fight', 'p': (330, 250)}, {'t': 'fight', 'p': (940, 250)},
        {'t': 'occupy', 'p': (1000, 320)}, {'t': 'fight_boss', 'p': (640, 260)},
    ]
    check_ap(self, data, True)
    start_action(self, data)
    return None


def region1(self):
    self.log_title('开始国服活动-区域1')
    data = [
        {'t': 'fight', 'p': (640, 555)},
        {'t': 'operation', 'p': (640, 555)},
        {'t': 'scan', 'p': (640, 555), 'count': 21, 'ap': 105},
        {'t': 'occupy', 'p': (585, 480)},
        {'t': 'occupy', 'p': (640, 400)},
        {'t': 'fight', 'p': (690, 330)},
        {'t': 'fight', 'p': (590, 330)},
        {'t': 'fight_boss', 'p': (640, 270)},
        {'t': 'operation', 'p': (640, 270)},
        {'t': 'scan', 'p': (640, 270), 'count': 91, 'ap': 455},
        {'t': 'shop', 'p': (70, 137), 'p2': (1170, 380)},
    ]
    check_ap(self, data, False)
    start_action(self, data)
    return None


def check_ap(self, data, mode=True):
    need_ap = 0
    need_hb = 0
    for item in data:
        if item['t'] == 'fight':
            need_hb += 150
        elif item['t'] == 'occupy':
            need_hb += 100
        elif item['t'] == 'scan':
            need_ap += item['ap']
    ap = stage.get_ap(self)
    if ap < need_ap:
        self.exit('体力必须大于:{0}，当前已有体力：{1}'.format(need_ap, ap))
        return None
    return None


def region2(self):
    self.log_title('开始国服活动-区域2')
    data = [
        {'t': 'occupy', 'p': (640, 695)}, {'t': 'fight', 'p': (585, 620)},
        {'t': 'fight', 'p': (640, 540)}, {'t': 'fight', 'p': (690, 470)},
        {'t': 'fight', 'p': (745, 395)}, {'t': 'occupy', 'p': (790, 330)},
        {'t': 'fight', 'p': (690, 320)}, {'t': 'occupy', 'p': (480, 620)},
        {'t': 'occupy', 'p': (535, 545)}, {'t': 'occupy', 'p': (590, 470)},
        {'t': 'occupy', 'p': (640, 400)}, {'t': 'occupy', 'p': (590, 320)},
        {'t': 'occupy', 'p': (740, 550)}, {'t': 'occupy', 'p': (790, 470)},
        {'t': 'occupy', 'p': (840, 400)}, {'t': 'occupy', 'p': (430, 400)},
        {'t': 'fight', 'p': (850, 540)}, {'t': 'fight', 'p': (430, 540)},
        {'t': 'fight', 'p': (480, 320)}, {'t': 'fight', 'p': (690, 620)},
        {'t': 'fight', 'p': (440, 250)}, {'t': 'fight', 'p': (850, 250)},
        {'t': 'fight_boss', 'p': (640, 270)},
    ]
    check_ap(self, data)
    start_action(self, data)
    return None


def region3(self):
    self.log_title('开始国服活动-区域3')
    data = [
        {'t': 'occupy', 'p': (640, 695)}, {'t': 'fight', 'p': (585, 620)},
        {'t': 'fight', 'p': (640, 540)}, {'t': 'fight', 'p': (690, 470)},
        {'t': 'fight', 'p': (740, 390)}, {'t': 'fight', 'p': (690, 320)},
        {'t': 'fight', 'p': (590, 320)}, {'t': 'occupy', 'p': (740, 540)},
        {'t': 'occupy', 'p': (790, 470)}, {'t': 'occupy', 'p': (850, 400)},
        {'t': 'occupy', 'p': (790, 330)}, {'t': 'occupy', 'p': (640, 400)},
        {'t': 'occupy', 'p': (540, 400)}, {'t': 'occupy', 'p': (430, 400)},
        {'t': 'fight', 'p': (850, 540)}, {'t': 'fight', 'p': (430, 540)},
        {'t': 'fight', 'p': (380, 460)}, {'t': 'fight', 'p': (480, 470)},
        {'t': 'fight', 'p': (590, 470)}, {'t': 'fight', 'p': (900, 470)},
        {'t': 'fight', 'p': (950, 400)}, {'t': 'fight', 'p': (400, 320)},
        {'t': 'fight', 'p': (425, 265)}, {'t': 'fight', 'p': (840, 250)},
        {'t': 'fight_boss', 'p': (640, 270)},
    ]
    check_ap(self, data)
    start_action(self, data)
    return None


def region4(self):
    self.log_title('开始国服活动-区域4')
    data = [
        {'t': 'occupy', 'p': (640, 695)}, {'t': 'fight', 'p': (690, 615)},
        {'t': 'occupy', 'p': (740, 540)}, {'t': 'fight', 'p': (790, 460)},
        {'t': 'occupy', 'p': (790, 610)}, {'t': 'occupy', 'p': (850, 540)},
        {'t': 'occupy', 'p': (950, 540)}, {'t': 'occupy', 'p': (900, 620)},
        {'t': 'occupy', 'p': (1000, 470)}, {'t': 'occupy', 'p': (840, 390)},
        {'t': 'occupy', 'p': (790, 320)}, {'t': 'occupy', 'p': (740, 390)},
        {'t': 'occupy', 'p': (640, 390)}, {'t': 'occupy', 'p': (680, 460)},
        {'t': 'fight', 'p': (890, 460)}, {'t': 'fight', 'p': (950, 390)},
        {'t': 'fight', 'p': (900, 320)}, {'t': 'fight', 'p': (680, 320)},
        {'t': 'fight', 'p': (580, 320)}, {'t': 'fight', 'p': (530, 390)},
        {'t': 'fight', 'p': (590, 460)}, {'t': 'fight', 'p': (540, 540)},
        {'t': 'fight', 'p': (640, 540)}, {'t': 'fight', 'p': (580, 610)},
        {'t': 'occupy', 'p': (480, 610)}, {'t': 'occupy', 'p': (370, 610)},
        {'t': 'occupy', 'p': (430, 540)}, {'t': 'occupy', 'p': (480, 460)},
        {'t': 'occupy', 'p': (430, 390)}, {'t': 'occupy', 'p': (480, 310)},
        {'t': 'occupy', 'p': (330, 390)}, {'t': 'occupy', 'p': (280, 320)},
        {'t': 'occupy', 'p': (270, 460)}, {'t': 'fight', 'p': (320, 530)},
        {'t': 'fight', 'p': (380, 460)}, {'t': 'fight', 'p': (380, 320)},
        {'t': 'fight', 'p': (330, 250)}, {'t': 'fight', 'p': (940, 250)},
        {'t': 'occupy', 'p': (1000, 320)}, {'t': 'fight_boss', 'p': (640, 260)},
    ]
    check_ap(self, data)
    start_action(self, data)
    return None
