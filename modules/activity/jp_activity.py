import time
from common import image, color, limit
from common import stage
from modules.baas import home
from modules.exp.normal_task import exp_normal_task
from modules.story import main_story

position = {
    1: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    2: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    3: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    4: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    5: ((1130, 230), (1130, 330), (1130, 450), (1130, 570)),
    6: ((1130, 230), (1130, 330), (1130, 450), (1130, 570)),
    7: ((1130, 230), (1130, 330), (1130, 450), (1130, 570)),
    8: ((1130, 230), (1130, 330), (1130, 450), (1130, 570)),
    9: ((1130, 290), (1130, 400), (1130, 520), (1130, 630)),
    10: ((1130, 290), (1130, 400), (1130, 520), (1130, 630)),
    11: ((1130, 290), (1130, 400), (1130, 520), (1130, 630)),
    12: ((1130, 290), (1130, 400), (1130, 520), (1130, 630)),
}

stage_data = {
    'story-1': 1, 'story-2': 1, 'story-3': 1, 'story-4': 1, 'story-5': 1,
    'story-6': 1, 'story-7': 1, 'story-8': 1, 'story-9': 1, 'story-10': 1,
    'story-11': 1, 'story-12': 1, 'story-13': 1, 'story-14': 1, 'story-15': 1,
    'task-1': 1, 'task-2': 1, 'task-3': 1, 'task-4': 1, 'task-5': 1,
    'task-6': 1, 'task-7': 1, 'task-8': 1, 'task-9': 1, 'task-10': 1,
    'task-11': 1, 'task-12': 1, 'task-13': 1, 'task-14': 1, 'task-15': 1,
    'challenge-1': 1, 'challenge-2': 1, 'challenge-3': 1,
}

current_men = 'cm_activity-menu'


def to_tab(self, t):
    tabs = {
        'story': ((832, 103, 833, 104), (77, 55, 40)),
        'task': ((1002, 103, 1003, 104), (77, 55, 40)),
        'challenge': ((1190, 103, 1191, 104), (77, 55, 40)),
        'challenge-task': ((1190, 103, 1191, 104), (77, 55, 40)),
    }
    if image.compare_image(self, 'cn_activity_quest', retry=3, cl=(730, 110)):
        tabs['task'] = ((1115, 103, 1116, 104), (77, 55, 40))
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
    finish_task(self)
    home.go_home(self)
    return None


def finish_task(self):
    self.md = self.tc
    self.md['story_exp']['enable'] = False
    self.md['task_exp']['enable'] = False
    self.md['bonus']['enable'] = False
    return None


def start_exp(self):
    tabs = ['story', 'task']
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
    self.log_title('开始日服活动-扫荡')
    to_activity_page(self)
    to_tab(self, 'task')
    stage_list = self.tc['scan']['stage']
    stage.screen_swipe(self, 0, False, (926, 590, 926, 0, 0.1), threshold2=False, reset=False)
    stage1 = False
    stage2 = False
    stage3 = False
    for task in stage_list:
        gq, count = task.split('-')
        gq = int(gq)
        self.logger.warning('正在扫荡第{0}关 扫荡{1}次...'.format(gq, count))
        x, y = position[gq]
        if gq in position:
            self.exit('本次活动不支持扫荡该关卡')
        if gq <= 4 and not stage1:
            stage.screen_swipe(self, 0, False, (926, 150, 926, 700, 0.1), threshold2=False, reset=False)
            stage1 = True
        if 4 < gq < 9 and not stage2:
            stage.screen_swipe(self, 0, False, (926, 150, 926, 700, 0.1), threshold2=False, reset=False)
            stage.screen_swipe(self, False, (926, 590, 926, 150, 0.5), reset=False)
            stage2 = True
        if gq >= 9 and not stage3:
            stage.screen_swipe(self, 0, False, (926, 590, 926, 0, 0.1), threshold2=False, reset=False)
            stage3 = True
        if gq >= 9 and image.compare_image(self, 'cm_activity-prize-info', 3):
            y -= 100
        self.click(x, y)
        rst = stage.confirm_scan(self, gq, count, 99)
        to_activity_page(self)
        if rst == 'return':
            return None
    return None


def start_bonus(self):
    if not self.tc['bonus']['enable']:
        return None
    to_activity_page(self)
    tab = 'task'
    to_tab(self, tab)
    bonus_list = ['bonus1', 'bonus2', 'bonus3']
    stage1 = False
    stage2 = False
    stage3 = False
    for i, bon in enumerate(bonus_list):
        cu_bonus = self.tc['bonus'][bon]
        for gq in cu_bonus:
            gq = int(gq)
            x, y = position[gq]
            self.logger.warning('正在自动加成第{0}关...'.format(gq))
            if gq in position:
                self.exit('本次活动不支持扫荡该关卡')
            if gq <= 4 and not stage1:
                stage.screen_swipe(self, 0, False, (926, 150, 926, 700, 0.1), threshold2=False, reset=False)
                stage1 = True
            if 4 < gq < 9 and not stage2:
                stage.screen_swipe(self, 0, False, (926, 150, 926, 700, 0.1), threshold2=False, reset=False)
                stage.screen_swipe(self, False, (926, 590, 926, 150, 0.5), reset=False)
                stage2 = True
            if gq >= 9 and not stage3:
                stage.screen_swipe(self, 0, False, (926, 590, 926, 0, 0.1), threshold2=False, reset=False)
                stage3 = True
            if gq >= 9 and image.compare_image(self, 'cm_activity-prize-info', 3):
                y -= 100
            self.click(x, y)
            image.detect(self, 'main_story_main-lv-start-task', 1, rate=1)
            start_fight(self, 'bonus', i + 1, gq, tab)
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
                exp_normal_task.choose_yushe_and_start_action(self, gk)
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
                stage.choose_role(self, stage_data[gk])
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
    if tab == 'story':
        if (image.compare_image(self, 'cm_activity-sss', 0) or
                image.compare_image(self, 'cm_activity-sss2', 0)):
            return 'sss'
    return 'no-sss'
