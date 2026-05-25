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
    rst = image.find_img(self, self.get_screenshot_array(), 'tactics_test_join', y_add=20)
    if len(rst) <= 0:
        self.logger.warning('找不到要测试的项目... ')
        return None
    image.compare_image(self, 'tactics_test_show-all', cl=rst[0])
    return None


def start(self):
    global force_index
    if self.game_server != 'cn':
        self.logger.error('本功能目前仅支持国服版本,其它服务器正在开发中...')
        return None
    force_index = 1
    home.go_home(self)
    to_test_menu(self)
    if not check_ticket(self):
        home.go_home(self)
        return None
    if not self.tc['exp']['help']:
        start_scan(self)
    start_exp(self)
    start_scan(self)
    home.go_home(self)
    return None


def check_ticket(self):
    if image.compare_image(self, 'tactics_test_no-ticket', threshold=0.9, retry=1):
        self.logger.error('没票了')
        return False
    return True


def skip_main_story_plot(self):
    global force_index
    pos = {
        'fight_pass-confirm': (1170, 666),
        'tactics_test_over': (645, 525),
        'cm_get-prize': (650, 640),
    }
    ends = ('fight_fail', 'tactics_test_menu', 'tactics_test_show-all')
    end = image.detect(self, ends, pos, rate=1)
    if end == 'tactics_test_menu':
        to_test_menu(self)
    force_index += 1
    if end == 'fight_fail':
        force_index -= 1
        start_next(self)
        return None
    return None


def start_next(self):
    pos = {'fight_fail': (645, 655)}
    image.detect(self, 'tactics_test_show-all', pos, rate=1)
    image.compare_image(self, 'tactics_test_info', cl=(1155, 225), rate=1)
    start_fight(self)
    return None


def start_exp(self):
    if not self.tc['exp']['enable']:
        return None
    if not check_ticket(self):
        return None
    self.click(1155, 645, False)
    time.sleep(1)
    self.click(770, 500, False)
    time.sleep(1)
    for stage in self.tc['exp']['stage']:
        if not check_ticket(self):
            return None
        stage = int(stage)
        do_exp(self, stage)
    if self.tc['exp']['help']:
        start_exp(self)
        return None
    return None


def do_exp(self, stage):
    image.compare_image(self, 'tactics_test_info', cl=stage_position[stage], rate=1)
    start_fight(self)
    return None


def total_select_force(self):
    if self.tc['exp']['auto']:
        start_auto_select(self)
        return None
    exp_normal_task.select_force_fight(self, force_index)
    return None


def start_auto_select(self):
    global first_force
    p = {'tactics_test_force-edit': (1200, 185)}
    image.detect(self, 'cm_bonus-tzbd', p, rate=1)
    time.sleep(0.5)
    self.double_click(650, 590)
    time.sleep(0.5)
    if self.tc['exp']['help'] and first_force:
        first_force = False
        stu_p = [(100, 600), (1070, 160), (640, 300)]
        for sp in stu_p:
            self.click(*sp, False)
            time.sleep(1)
    stu_p = [(1150, 590), (766, 500)]
    for sp in stu_p:
        self.click(*sp, False)
        time.sleep(1)
    return None


def start_fight(self):
    image.compare_image(self, 'tactics_test_force-edit', cl=(640, 505), rate=1)
    total_select_force(self)
    time.sleep(1)
    if force_index == 1 and self.tc['exp']['help']:
        pos = {
            'tactics_test_force-edit': (1160, 650),
            'total_war_need-help': (770, 490),
        }
        image.detect(self, 'total_war_join-notice', pos, retry=10)
        image.compare_image(self, 'total_war_join-notice', cl=(770, 500), rate=1, n=True)
        image.compare_image(self, 'tactics_test_force-edit', cl=(770, 500), rate=1, n=True)
    else:
        image.compare_image(self, 'tactics_test_force-edit', cl=(1160, 650), rate=1, n=True)
    main_story.auto_fight(self, s=5)
    time.sleep(100)
    skip_main_story_plot(self)
    time.sleep(5)
    return None


def start_scan(self):
    if not self.tc['scan']['enable']:
        return None
    if not check_ticket(self):
        return None
    if image.compare_image(self, 'tactics_test_not-scan', retry=3):
        return None
    image.compare_image(self, 'tactics_test_scan-window', cl=(820, 650), rate=1)
    self.double_click(990, 360, False, 5)
    image.compare_image(self, 'tactics_test_scan-notice', cl=(780, 440))
    image.compare_image(self, 'tactics_test_scan-notice', cl=(770, 500), rate=1, n=True)
    stage.start_scan(self)
    return None
