import time
from common import image, color, limit
from common import stage
from modules.activity import cn_activity, jp_activity, intl_activity
from modules.baas import home
from modules.exp.normal_task import exp_normal_task
from modules.story import main_story

position = {}


def to_tab(self, t):
    tabs = {
        'story': ((832, 103, 833, 104), (77, 55, 40)),
        'task': ((1002, 103, 1003, 104), (77, 55, 40)),
        'challenge': ((1190, 103, 1191, 104), (77, 55, 40)),
        'challenge-task': ((1190, 103, 1191, 104), (77, 55, 40)),
    }
    tab = tabs[t]
    color.wait_rgb_similar(self, tab[0], tab[1], tab[0][0] - 100, tab[0][1], cl=tab[1])
    return None


is_exp = False


def do_exp(self):
    tab = 'story'
    svc = {'cn': cn_activity, 'jp': jp_activity, 'intl': intl_activity}
    time.sleep(2)
    svc[self.game_server].to_activity_page(self)
    stage.screen_swipe(self, 0, False, (926, 150, 926, 720, 0.1), threshold2=False, reset=False)
    state, stage_index = svc[self.game_server].calc_need_fight_stage(self, tab)
    if state is None:
        self.logger.critical('本区域没有需要开图的任务关卡...')
        self.click(55, 38)
        return None
    svc[self.game_server].start_fight(self, 'exp', 0, stage_index, tab)
    do_exp(self)
    return None


def start(self):
    if self.game_server != 'cn':
        return None
    home.go_home(self)
    pos = {'home_student': (1070, 560)}
    image.detect(self, 'activity_story_menu', pos)
    time.sleep(1)
    self.click(95, 135)
    time.sleep(1)
    while True:
        self.click(1100, 110)
        time.sleep(1)
        self.click(370, 160)
        time.sleep(1)
        self.click(775, 570)
        if 1 == 2:
            break
        self.click(685, 225)
        do_exp(self)
    home.go_home(self)
    return None
