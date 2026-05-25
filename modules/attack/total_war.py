import time
from common import color, image, stage, limit
from modules.baas import home
from modules.attack import special_entrust
from modules.exp.normal_task import exp_normal_task
from modules.story import main_story

x = {}

stage_position = {
    1: (1155, 225),
    2: (1155, 355),
    3: (1155, 485),
    4: (1155, 165),
    5: (1155, 250),
    6: (1155, 390),
    7: (1155, 530),
}


def to_total_war(self):
    pos = {
        'home_student': (1200, 573),
        'home_bus': (926, 450),
    }
    home.to_menu(self, 'total_war_menu', pos)


force_index = 1


def start(self):
    force_index = 1

    home.go_home(self)

    to_total_war(self)

    check_ticket(self)

    if not self.tc['help']['enable']:
        start_scan(self)

    start_exp(self)

    start_scan(self)

    get_prize(self)

    finish_task(self)

    home.go_home(self)


def finish_task(self):
    self.md = self.tc
    self.md['exp']['enable'] = False


def get_prize(self):
    if not color.check_rgb(self, (1241, 628), (251, 64, 16)):
        self.logger.error('没有奖励可以领取')
        return

    pos = {
        'total_war_menu': (1180, 656),
        'total_war_my-info': (925, 170),
        'total_war_rank-prize': (240, 310),
    }

    image.detect(self, 'total_war_score-prize', pos)

    if not color.check_rgb(self, (1003, 580), (245, 233, 75)):
        self.logger.error('没有奖励可以领取')
        return

    self.click(1063, 577, False)
    stage.close_prize_info(self, False, False)


def check_ticket(self):
    if image.compare_image(self, 'total_war_no-ticket', 0.9, 1, threshold=True, retry=True):
        self.logger.error('没票了')
        return


def skip_main_story_plot(self):
    pos = {
        'fight_pass-confirm': (1170, 666),
        'total_war_get-prize': (773, 655),
        'total_war_score-confirm': (640, 530),
        'total_war_fight-result': (645, 570),
    }
    ends = ('fight_fail', 'total_war_menu')

    end = image.detect(self, ends, pos, 2, rate=True)

    if end == 'fight_fail':
        force_index += 1
        if force_index == 5:
            self.click(56, 36, False)
            self.exit('作战失败，停止运行。。。')
            return
        start_next(self)
        return


def start_next(self):
    pos = {
        'fight_fail': (645, 655),
    }
    image.detect(self, 'total_war_menu', pos, 1, rate=True)
    image.compare_image(self, 'total_war_detail-info', (1155, 225), 1, cl=True, rate=True)
    start_fight(self)


def start_exp(self):
    if not self.tc['exp']['enable']:
        return
    for stage in self.tc['exp']['stage']:
        if image.compare_image(self, 'total_war_no-ticket', 0.9, 1, threshold=True, retry=True):
            self.logger.error('没票了')
            return
        stage = int(stage)
        do_exp(self, stage)


need_help = True


def do_exp(self, stage, need_swipe=True):
    need_help = True

    if need_swipe:
        if stage <= 4:
            self.swipe(1000, 166, 1000, 700, 0.1)
        else:
            self.swipe(1000, 555, 1000, 0, 0.1)
        time.sleep(2)

    image.compare_image(self, 'total_war_detail-info', stage_position[stage], 1, cl=True, rate=True)

    if not self.tc['help']['enable'] and image.compare_image(self, 'total_war_can-scan', 1, retry=True):
        image.compare_image(self, 'total_war_detail-info', (1121, 166), 1, True, cl=True, rate=True, n=True)
        return

    start_fight(self)


def total_select_force(self):
    if self.tc['force']['mode'] == 2:
        start_auto_select(self)
        image.compare_image(self, 'total_war_force-edit')
        return
    exp_normal_task.select_force_fight(self, force_index)


def start_auto_select(self):
    p = {
        'total_war_force-edit': (1200, 185),
    }
    image.detect(self, 'cm_bonus-tzbd', p)

    position = {
        'cn': {
            'auto': [(650, 590), (1150, 590), (766, 500)],
            'help': [(370, 600), (1060, 160), (645, 310)],
        },
        'jp': {
            'auto': [(615, 595), (1170, 590), (766, 500)],
            'help': [(345, 595), (1060, 160), (640, 300)],
        },
        'intl': {
            'auto': [(615, 595), (1170, 590), (766, 500)],
            'help': [(345, 595), (1060, 160), (640, 300)],
        },
    }

    count = 0

    for i in position[self.game_server]['auto']:
        self.click(i, False)
        time.sleep(1)
        if count == 0 and need_help and self.tc['help']['enable']:
            need_help = False
            for k in position[self.game_server]['help']:
                self.click(k, False)
                time.sleep(1)
        count += 1


def start_fight(self):
    image.compare_image(self, 'total_war_force-edit', (1020, 520), 1, cl=True, rate=True)

    total_select_force(self)

    if force_index == 1:
        pos = {
            'total_war_force-edit': (1160, 650),
            'total_war_need-help': (770, 490),
        }
        image.detect(self, 'total_war_join-notice', pos, 20, retry=True)
        image.compare_image(self, 'total_war_join-notice', (770, 500), 1, True, 20, cl=True, rate=True, n=True, retry=True)
    else:
        image.compare_image(self, 'total_war_force-edit', (1160, 650), 1, True, cl=True, rate=True, n=True)

    if force_index == 1:
        stage.wait_loading(self)
        pos = {
            'momo_talk_menu': (1205, 42),
            'momo_talk_skip': (1212, 116),
            'momo_talk_confirm-skip': (770, 516),
        }
        image.detect(self, 'total_war_skip-anm', pos, 30, (630, 330), retry=True, cl=True)

    image.show_and_hide(self, 'total_war_skip-anm', (630, 330), (770, 500))

    main_story.auto_fight(self, 5, s=True)

    time.sleep(30)
    skip_main_story_plot(self)
    time.sleep(5)


def start_scan(self):
    if image.compare_image(self, 'total_war_no-ticket', 0.9, 1, threshold=True, retry=True):
        self.logger.error('没票了')
        return

    if not self.tc['scan']['enable']:
        return

    lv = self.tc['scan']['stage']

    if lv <= 3:
        self.swipe(1000, 166, 1000, 700, 0.1)
    else:
        self.swipe(1000, 555, 1000, 0, 0.1)

    time.sleep(2)

    p = stage_position[lv]

    if not color.check_rgb(self, (1110, p[1]), (245, 233, 75)):
        return

    image.compare_image(self, 'total_war_detail-info', p, 1, cl=True, rate=True)

    if not image.compare_image(self, 'total_war_can-scan', 1, retry=True):
        do_exp(self, lv, False)
        start_scan(self)
        return

    self.double_click(1073, 303, False)
    self.double_click(1073, 303, False)
    self.d.long_click(1073, 303, 2)

    image.compare_image(self, 'total_war_join-notice', (855, 395), 1, 20, cl=True, rate=True, retry=True)
    image.compare_image(self, 'total_war_join-notice', (770, 500), 1, True, 20, cl=True, rate=True, n=True, retry=True)

    stage.start_scan(self)
