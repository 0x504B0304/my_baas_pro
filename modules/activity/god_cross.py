import time
from common import image, color, limit
from common import stage
from modules.baas import home
from modules.exp.normal_task import exp_normal_task
from modules.story import main_story

position = {
    1: ((1130, 190), (1130, 288), (1130, 385), (1130, 485), (1130, 570)),
    2: ((1130, 190), (1130, 288), (1130, 385), (1130, 485), (1130, 570)),
    3: ((1130, 190), (1130, 288), (1130, 385), (1130, 485), (1130, 570)),
    4: ((1130, 190), (1130, 288), (1130, 385), (1130, 485), (1130, 570)),
    5: ((1130, 190), (1130, 288), (1130, 385), (1130, 485), (1130, 570)),
    6: ((1130, 160), (1130, 233), (1130, 330), (1130, 430), (1130, 525)),
    7: ((1130, 160), (1130, 233), (1130, 330), (1130, 430), (1130, 525)),
    8: ((1130, 160), (1130, 233), (1130, 330), (1130, 430), (1130, 525)),
    9: ((1130, 160), (1130, 233), (1130, 330), (1130, 430), (1130, 525)),
    10: ((1130, 160), (1130, 233), (1130, 330), (1130, 430), (1130, 525)),
}

stage_data = {
    'story-1': 1, 'story-2': 1, 'story-3': 1, 'story-4': 1, 'story-5': 1,
    'story-6': 1, 'story-7': 1, 'story-8': 1, 'story-9': 1, 'story-10': 1,
    'story-11': 1, 'story-12': 1, 'story-13': 1, 'story-14': 1, 'story-15': 1,
    'story-16': 1, 'task-1': 2, 'task-2': 2, 'task-3': 2, 'task-4': 2,
    'task-5': 2, 'task-6': 2, 'task-7': 2, 'task-8': 2, 'task-9': 2,
    'task-10': 2,
}

current_men = 'god_cross_menu'


def to_tab(self, t):
    tabs = {
        'story': ((760, 110), (730, 110)),
        'task': ((935, 110), (900, 104)),
    }
    click_pos, check_pos = tabs[t]
    for _ in range(20):
        if color.check_rgb(self, check_pos, (34, 60, 85), threshold=45):
            return None
        self.click(*click_pos, False)
        time.sleep(0.3)
    self.exit('神名十字页签切换失败: {0}'.format(t))
    return None


def to_activity_page(self):
    pos = {
        'momo_talk_menu': (1205, 42), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516), 'normal_task_task-info': (1084, 142),
        'normal_task_buy-ap-window': (920, 166), 'home_student': (1200, 573),
        'home_bus': (100, 160), 'new_year_guide': (1184, 156),
        'home_new-players': (1234, 26), 'god_cross_task': (55, 37),
    }
    image.detect(self, current_men, pos)
    return None


def start(self):
    home.go_home(self)
    to_activity_page(self)
    get_prize(self)
    start_exp(self)
    start_scan(self)
    home.go_home(self)
    return None


def get_prize(self):
    pos = {current_men: (220, 660)}
    image.detect(self, 'god_cross_task', pos)
    if not color.check_rgb(self, (1085, 685), (249, 237, 73)):
        self.logger.error('没有奖励可以领取')
        return None
    self.click(1156, 666)
    stage.close_prize_info(self)
    return None


def start_exp(self):
    tabs = ['story', 'task']
    for tab in tabs:
        if not self.tc[tab + '_exp']['enable']:
            continue
        to_activity_page(self)
        do_exp(self, tab)
    return None


def start_scan(self):
    if not self.tc['scan']['enable']:
        return None
    to_activity_page(self)
    to_tab(self, 'task')
    stage_list = self.tc['scan']['stage']
    for task in stage_list:
        gq, count = task.split('-')
        gq = int(gq)
        stage.screen_swipe(self, gq, 5, (910, 570, 910, 0, 0.1), f=(910, 570, 910, 0, 0.1))
        self.click(*god_cross_stage_position(gq))
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
    image.detect(self, 'brzx_draw-menu', pos)
    time.sleep(2)
    while True:
        if color.check_rgb(self, (800, 600), (118, 220, 255)):
            image.detect(self, 'brzx_card', cl=(815, 568))
        if not color.check_rgb(self, (970, 590), (245, 233, 74)):
            self.logger.error('不能抽卡了...')
            return None
        time.sleep(0.1)
        self.click(1050, 560)
        ends = (('brzx_not-210', 0.9), ('brzx_210', 0.9))
        end = image.detect(self, ends, rate=0)
        if end == 'brzx_not-210':
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
            stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(930, 150, 930, 700, 0.1))
            lv = int(gq)
            self.click(*god_cross_stage_position(lv))
            image.detect(self, 'normal_task_task-info-window', 1, rate=1)
            start_fight(self, 'bonus', i + 1, lv, tab)
    return None


def do_exp(self, tab):
    tmp = 'story' if tab == 'task' else 'task'
    to_tab(self, tmp)
    to_activity_page(self)
    to_tab(self, tab)
    stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 150, 926, 720, 0.1))
    state, stage_index = calc_need_fight_stage(self, tab)
    if state is None:
        self.logger.critical('本区域没有需要开图的任务关卡...')
        return None
    rt = start_fight(self, 'exp', 0, stage_index, tab)
    if rt == 'return':
        return None
    do_exp(self, tab)
    return None


prev_bonus_index = -1


def start_fight(self, t, bonus_index, stage_index, tab):
    global prev_bonus_index
    pos = {'main_story_main-lv-start-task': (943, 532), 'main_story_side-lv-start-task': (640, 511)}
    ends = ('god_cross_no-score', 'momo_talk_menu', 'normal_task_force-edit',
            'momo_talk_skip', 'momo_talk_confirm-skip', 'fight_start-task')
    end = image.detect(self, ends, pos)
    if end == 'god_cross_no-score':
        home.click_house_under(self)
        home.click_house_under(self)
        return 'return'
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
        'fight_prize-confirm': (776, 655), 'fight_prize-confirm1': (645, 670),
        'fight_prize-confirm2': (775, 660), 'momo_talk_menu': (1205, 42),
        'momo_talk_skip': (1212, 116), 'momo_talk_confirm-skip': (770, 516),
        'cn_activity_unlock': (1259, 62), 'cm_get-prize': (650, 640),
    }
    image.detect(self, current_men, possible)
    return None


def skip_story(self):
    pos = {
        'momo_talk_menu': (1205, 42), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516),
    }
    image.detect(self, 'normal_task_force-edit', pos)
    return None


def wait_task_info(self, open_info=True):
    if open_info:
        image.detect(self, ('normal_task_task-info', 'normal_task_side-quest'), cl=(1082, 190), rate=2)
        return None
    image.compare_image(self, 'normal_task_task-info', 10)
    return None


def calc_need_fight_stage(self, tab):
    wait_task_info(self)
    stage_index = 1
    while True:
        task_state = check_task_state(self, tab)
        self.logger.info('当前关卡状态为:{0}'.format(task_state))
        if tab + '-' + str(stage_index) not in stage_data:
            self.logger.error('当前关卡不支持卡图,查找下一关')
            self.click(1172, 358)
            stage_index += 1
            continue
        if task_state == 'sss':
            self.logger.warning('不满足战斗条件,查找下一关')
            self.click(1172, 358)
            stage_index += 1
            continue
        if task_state is None:
            return (None, 0)
        return (task_state, stage_index)


def check_task_state(self, tab):
    wait_task_info(self, False)
    time.sleep(1)
    if image.compare_image(self, current_men, 0):
        return None
    if image.compare_image(self, 'normal_task_sss', 0, 0.9):
        return 'sss'
    return 'no-sss'


def god_cross_stage_position(gq):
    slots = position[int(gq)]
    return slots[(int(gq) - 1) % len(slots)]
