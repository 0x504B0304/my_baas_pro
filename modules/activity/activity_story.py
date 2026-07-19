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
        'story': ((760, 110), (730, 110)),
        'task': ((935, 110), (900, 104)),
        'challenge': ((1125, 110), (1060, 104)),
        'challenge-task': ((1125, 110), (1060, 104)),
    }
    click_pos, check_pos = tabs[t]
    for _ in range(20):
        if color.check_rgb(self, check_pos, (34, 60, 85), threshold=45):
            return None
        self.click(*click_pos, False)
        time.sleep(0.3)
    self.exit('活动故事页签切换失败: {0}'.format(t))
    return None


is_exp = False


def do_exp(self):
    tab = 'story'
    svc = {'cn': cn_activity, 'jp': jp_activity, 'intl': intl_activity}
    time.sleep(2)
    svc[self.game_server].to_activity_page(self)
    stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 150, 926, 720, 0.1))
    state, stage_index = svc[self.game_server].calc_need_fight_stage(self, tab)
    if state is None:
        self.logger.critical('本区域没有需要开图的任务关卡...')
        self.click(55, 38)
        return False
    svc[self.game_server].start_fight(self, 'exp', 0, stage_index, tab)
    do_exp(self)
    return True


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
        self.click(685, 225)
        if not do_exp(self):
            break
    home.go_home(self)
    return None
