import time
from common import color, image, stage, limit
from modules.baas import home
from modules.attack import special_entrust
from modules.exp.normal_task import exp_normal_task
from modules.story import main_story

stage_position = {
    1: (1180, 190),
    2: (1180, 280),
    3: (1180, 380),
    4: (1180, 480),
}

force_index = 1
first_force = True


def to_test_menu(self):
    pos = {
        'home_student': (1200, 573),
        'home_bus': (1000, 450),
        'tactics_test_over': (645, 525),
        'cm_get-prize': (645, 633, 0.7),
    }
    home.to_menu(self, ('tactics_test_menu', 'tactics_test_show-all'), pos)

    time.sleep(2)
    rst = image.find_img(self, self.get_screenshot_array(), 'tactics_test_join', 20, y_add=True)
    if len(rst) <= 0:
        self.logger.warning('找不到要测试的项目... ')
        return

    image.compare_image(self, 'tactics_test_show-all', rst[0], cl=True)


def start(self):
    if self.game_server != 'cn':
        self.logger.error('本功能目前仅支持国服版本,其它服务器正在开发中...')
        return

    force_index = 1

    home.go_home(self)

    to_test_menu(self)

    if not check_ticket(self):
        home.go_home(self)
        return

    if not self.tc['exp']['help']:
        start_scan(self)

    start_exp(self)

    start_scan(self)

    home.go_home(self)


def check_ticket(self):
    if image.compare_image(self, 'tactics_test_no-ticket', 0.9, 1, threshold=True, retry=True):
        self.logger.error('没票了')
        return False
    return True


def skip_main_story_plot(self):
    pos = {
        'fight_pass-confirm': (1170, 666),
        'tactics_test_over': (645, 525),
        'cm_get-prize': (650, 640),
    }
    ends = ('fight_fail', 'tactics_test_menu', 'tactics_test_show-all')

    end = image.detect(self, ends, pos, 1, rate=True)

    if end == 'tactics_test_menu':
        to_test_menu(self)

    force_index += 1

    if end == 'fight_fail':
        force_index -= 1
        start_next(self)
        return

    return


def start_next(self):
    pos = {
        'fight_fail': (645, 655),
    }
    image.detect(self, 'tactics_test_show-all', pos, 1, rate=True)
    image.compare_image(self, 'tactics_test_info', (1155, 225), 1, cl=True, rate=True)
    start_fight(self)


def start_exp(self):
    if not self.tc['exp']['enable']:
        return

    if not check_ticket(self):
        return

    self.click(1155, 645, False)
    time.sleep(1)
    self.click(770, 500, False)
    time.sleep(1)

    for stage in self.tc['exp']['stage']:
        if not check_ticket(self):
            return
        stage = int(stage)
        do_exp(self, stage)

    if self.tc['exp']['help']:
        start_exp(self)
        return
    return


def do_exp(self, stage):
    image.compare_image(self, 'tactics_test_info', stage_position[stage], 1, cl=True, rate=True)
    start_fight(self)


def total_select_force(self):
    if self.tc['exp']['auto']:
        start_auto_select(self)
        return
    exp_normal_task.select_force_fight(self, force_index)


def start_auto_select(self):
    p = {
        'tactics_test_force-edit': (1200, 185),
    }
    image.detect(self, 'cm_bonus-tzbd', p, 1, rate=True)
    time.sleep(0.5)
    self.double_click(650, 590)
    time.sleep(0.5)

    if self.tc['exp']['help'] and first_force:
        first_force = False
        stu_p = [(100, 600), (1070, 160), (640, 300)]
        for sp in stu_p:
            self.click(sp, False)
            time.sleep(1)

    stu_p = [(1150, 590), (766, 500)]
    for sp in stu_p:
        self.click(sp, False)
        time.sleep(1)


def start_fight(self):
    image.compare_image(self, 'tactics_test_force-edit', (640, 505), 1, cl=True, rate=True)

    total_select_force(self)

    time.sleep(1)

    if force_index == 1 and self.tc['exp']['help']:
        pos = {
            'tactics_test_force-edit': (1160, 650),
            'total_war_need-help': (770, 490),
        }
        image.detect(self, 'total_war_join-notice', pos, 10, retry=True)
        image.compare_image(self, 'total_war_join-notice', (770, 500), 1, True, cl=True, rate=True, n=True)
        image.compare_image(self, 'tactics_test_force-edit', (770, 500), 1, True, cl=True, rate=True, n=True)
    else:
        image.compare_image(self, 'tactics_test_force-edit', (1160, 650), 1, True, cl=True, rate=True, n=True)

    main_story.auto_fight(self, 5, s=True)

    time.sleep(100)
    skip_main_story_plot(self)
    time.sleep(5)


def start_scan(self):
    if not self.tc['scan']['enable']:
        return

    if not check_ticket(self):
        return

    if image.compare_image(self, 'tactics_test_not-scan', 3, retry=True):
        return

    image.compare_image(self, 'tactics_test_scan-window', (820, 650), 1, cl=True, rate=True)

    self.double_click(990, 360, False, 5)

    image.compare_image(self, 'tactics_test_scan-notice', (780, 440), cl=True)

    image.compare_image(self, 'tactics_test_scan-notice', (770, 500), 1, True, cl=True, rate=True, n=True)

    stage.start_scan(self)
