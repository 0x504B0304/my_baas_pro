import time
from common import image, color, limit
from common import stage
from modules.baas import home
from modules.exp.normal_task import exp_normal_task
from modules.story import main_story

position = {9: (1130, 290), 10: (1130, 400), 11: (1130, 520), 12: (1130, 630)}

stage_data = {
    'story-1': 1, 'story-2': 1, 'story-3': 1, 'story-4': 1, 'story-5': 1,
    'story-6': 1, 'story-7': 1, 'story-8': 1, 'story-9': 1, 'story-10': 1,
    'task-1': 1, 'task-2': 1, 'task-3': 1, 'task-4': 1, 'task-5': 1,
    'task-6': 1, 'task-7': 1, 'task-8': 1, 'task-9': 1, 'task-10': 1,
    'task-11': 1, 'task-12': 1, 'challenge-1': 1, 'challenge-2': 2,
    'challenge-3': 1,
}

current_men = 'cm_activity-menu'


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


def to_activity_page(self):
    pos = {
        'momo_talk_menu': (1205, 42), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516), 'normal_task_task-info': (1084, 142),
        'normal_task_task-info-window': (1084, 142), 'wanted_task-info-window': (1130, 142),
        'cm_activity-task-info': (1084, 142), 'normal_task_buy-ap-window': (920, 166),
        'home_student': (1200, 573), 'home_bus': (100, 160),
        'new_year_guide': (1184, 156), 'home_new-players': (1234, 26),
    }
    image.detect(self, current_men, pos)
    return None


def start(self):
    if self.game_server != 'jp':
        self.logger.error('日服专属活动,其它区服不执行该任务')
        return None
    home.go_home(self)
    to_activity_page(self)
    start_exp(self)
    start_bonus(self)
    start_scan(self)
    home.go_home(self)
    return None


def start_exp(self):
    tabs = ['story', 'task', 'challenge']
    for tab in tabs:
        if not self.tc[tab + '_exp']['enable']:
            continue
        to_activity_page(self)
        do_exp(self, tab)
    return None


def challenge_task(self):
    if not self.tc['challenge-task']['enable']:
        return None
    for s, p in {1100: (1100, 475), 280: (2, 4)}.items():
        to_activity_page(self)
        image.detect(self, 'cm_activity-task-info', p, cl=p)
        start_fight(self, 'exp', 0, s, 'challenge-task')
    return None


def start_scan(self):
    if not self.tc['scan']['enable']:
        return None
    to_activity_page(self)
    to_tab(self, 'task')
    stage_list = self.tc['scan']['stage']
    stage.screen_swipe(self, 0, False, (926, 590, 926, 0, 0.1), threshold2=False, reset=False)
    for task in stage_list:
        gq, count = task.split('-')
        gq = int(gq)
        if gq in position:
            self.exit('本次活动收益最高的是前4关，不能扫荡其它关卡')
        self.click(*position[gq])
        rst = stage.confirm_scan(self, gq, count, 99)
        to_activity_page(self)
        if rst == 'return':
            return None
    return None


def start_draw_card(self):
    if not self.tc['draw_card']['enable']:
        return None
    to_activity_page(self)
    pos = {current_men: (520, 640)}
    image.detect(self, 'alive_draw-menu', pos)
    time.sleep(2)
    while True:
        if color.check_rgb(self, (800, 600), (118, 220, 255)):
            image.detect(self, 'alive_card', cl=(815, 568))
        if not color.check_rgb(self, (970, 590), (245, 233, 74)):
            self.logger.error('不能抽卡了...')
            return None
        time.sleep(0.1)
        self.click(1050, 560)
        ends = (('alive_not-210', 0.9), ('alive_210', 0.9))
        end = image.detect(self, ends, rate=0)
        if end == 'alive_not-210':
            self.logger.error('不能抽卡了...')
            return None


def start_bonus(self):
    if not self.tc['bonus']['enable']:
        return None
    to_activity_page(self)
    tab = 'task'
    to_tab(self, tab)
    bonus_list = ['bonus1', 'bonus2', 'bonus3']
    for i, bon in enumerate(bonus_list):
        cu_bonus = self.tc['bonus'][bon]
        for gq in cu_bonus:
            stage.screen_swipe(self, 0, False, (926, 650, 926, 0, 0.1), threshold2=False, reset=False)
            lv = int(gq)
            self.click(*position[lv])
            image.detect(self, 'main_story_main-lv-start-task', 1, rate=1)
            start_fight(self, 'bonus', i + 1, lv, tab)
    return None


def do_exp(self, tab):
    tmp = 'challenge'
    if tmp in tab:
        tmp = 'story'
    to_tab(self, tmp)
    to_activity_page(self)
    to_tab(self, tab)
    if 'challenge' in tab:
        stage.screen_swipe(self, 0, False, (926, 150, 926, 720, 0.1), threshold2=False, reset=False)
    state, stage_index = calc_need_fight_stage(self, tab)
    if state is None:
        self.logger.critical('本区域没有需要开图的任务关卡...')
        return None
    start_fight(self, 'exp', 0, stage_index, tab)
    do_exp(self, tab)
    return None


prev_bonus_index = -1


def start_fight(self, t, bonus_index, stage_index, tab):
    pos = {'main_story_main-lv-start-task': (943, 532), 'main_story_side-lv-start-task': (640, 511)}
    ends = ('momo_talk_menu', 'normal_task_force-edit', 'momo_talk_skip', 'momo_talk_confirm-skip', 'fight_start-task')
    end = image.detect(self, ends, pos)
    if end == 'fight_start-task':
        gk = f'{tab}-{stage_index}'
        if gk in stage_data:
            image.compare_image(self, 'fight_force-edit')
            image.compare_image(self, 'fight_force-edit', threshold=0.6, cl=(1171, 670), rate=1, n=True)
        else:
            self.stage_data = stage_data
            if t == 'exp':
                exp_normal_task.choose_team_and_start_action(self, gk)
            else:
                exp_normal_task.choose_bonus_and_start_action(self, gk, bonus_index)
    else:
        end = skip_story(self)
        if end == 'cm_get-prize':
            wait_fight_over(self)
            return None
        image.compare_image(self, 'fight_force-edit')
        gk = f'{tab}-{stage_index}'
        if t == 'exp':
            if isinstance(stage_data[gk], int):
                exp_normal_task.select_force_fight(self, stage_data[gk])
        elif prev_bonus_index != bonus_index:
            exp_normal_task.start_bonus_single(self, bonus_index)
            prev_bonus_index = bonus_index
        image.compare_image(self, 'fight_force-edit', threshold=0.6, cl=(1171, 670), rate=1, n=True)
    main_story.auto_fight(self)
    self.logger.info('强制等待25秒...')
    time.sleep(25)
    wait_fight_over(self)
    return None


def wait_fight_over(self):
    possible = {
        'main_story_fight-confirm': (1168, 659), 'main_story_fight-fail': (647, 655),
        'fight_pass-confirm': (1170, 666), 'fight_task-finish-confirm': (1033, 666),
        'fight_prize-confirm1': (645, 670), 'fight_prize-confirm2': (775, 660),
        'momo_talk_menu': (1205, 42), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516), 'alive_unlock': (1259, 62),
        'cm_get-prize': (650, 640),
    }
    image.detect(self, current_men, possible)
    return None


def skip_story(self):
    pos = {'momo_talk_menu': (1205, 42), 'momo_talk_skip': (1212, 116), 'momo_talk_confirm-skip': (770, 516)}
    ends = ('normal_task_force-edit', 'cm_get-prize')
    return image.detect(self, ends, pos)


def wait_task_info(self, open_info=True):
    if open_info:
        image.detect(self, ('cm_activity-task-info', 'cm_activity-task-info2', 'normal_task_side-quest'), cl=(1082, 190), rate=1)
        return None
    image.detect(self, ('cm_activity-task-info', 'cm_activity-task-info2', 'normal_task_side-quest'), retry=10)
    return None


def calc_need_fight_stage(self, tab):
    wait_task_info(self)
    stage_index = 1
    while True:
        if tab == 'challenge' and stage_index >= 5:
            break
        task_state = check_task_state(self, tab)
        self.logger.info('当前关卡状态为:{0}'.format(task_state))
        if task_state is not None and tab + '-' + str(stage_index) in stage_data:
            self.logger.error('当前关卡不支持卡图,查找下一关')
            self.click(1172, 358)
            stage_index += 1
            continue
        if task_state == 'sss' and tab != 'challenge-task':
            self.logger.warning('不满足战斗条件,查找下一关')
            self.click(1172, 358)
            stage_index += 1
            continue
        if task_state is None:
            return (None, 0)
        return (task_state, stage_index)
    return (None, 0)


def check_task_state(self, tab):
    wait_task_info(self, False)
    time.sleep(1)
    if image.compare_image(self, 'normal_task_sss2', 0, 0.9):
        return 'sss'
    if image.compare_image(self, current_men, 0):
        return None
    if self.game_server == 'jp' and tab == 'story' and not image.compare_image(self, 'cm_activity-sss', 0):
        return 'sss'
    return 'no-sss'
