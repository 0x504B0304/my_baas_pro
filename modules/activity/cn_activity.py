import time
from common import image, color
from common import stage
from modules.baas import home, restart
from modules.exp.normal_task import exp_normal_task
from modules.story import main_story

current_men = 'cm_activity-menu'

position = {
    1: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    2: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    3: ((1130, 300), (1130, 415), (1130, 530), (1130, 640)),
    4: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    5: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    6: ((1130, 300), (1130, 415), (1130, 530), (1130, 640)),
    7: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    8: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    9: ((1130, 300), (1130, 415), (1130, 530), (1130, 640)),
    10: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    11: ((1130, 200), (1130, 310), (1130, 430), (1130, 540)),
    12: ((1130, 300), (1130, 415), (1130, 530), (1130, 640)),
}

position_special = {
    1: ((1130, 180), (1130, 280), (1130, 380), (1130, 480)),
    2: ((1130, 180), (1130, 280), (1130, 380), (1130, 480)),
    3: ((1130, 180), (1130, 280), (1130, 380), (1130, 480)),
    4: ((1130, 180), (1130, 280), (1130, 380), (1130, 480)),
    5: ((1130, 350), (1130, 450), (1130, 550), (1130, 650)),
    6: ((1130, 350), (1130, 450), (1130, 550), (1130, 650)),
    7: ((1130, 350), (1130, 450), (1130, 550), (1130, 650)),
    8: ((1130, 350), (1130, 450), (1130, 550), (1130, 650)),
}

stage_data = {
    'story-1': 1, 'story-2': 1, 'story-3': 1, 'story-4': 1, 'story-5': 1,
    'story-6': 1, 'story-7': 1, 'story-8': 1, 'story-9': 1, 'story-10': 1,
    'story-11': 1, 'story-12': 1, 'story-13': 1, 'story-14': 1, 'story-15': 1,
    'task-1': 1, 'task-2': 1, 'task-3': 1, 'task-4': 1, 'task-5': 1,
    'task-6': 1, 'task-7': 1, 'task-8': 1, 'task-9': 1, 'task-10': 1,
    'task-11': 1, 'task-12': 1, 'task-13': 1, 'task-14': 1, 'task-15': 1,
    'challenge-2': {
        'start': {'1': (550, 180), '2': (940, 430)},
        'action': [
            {'t': 'click', 'p': (640, 320)}, {'t': 'click', 'p': (710, 520)},
            {'t': 'click', 'p': (610, 370)}, {'t': 'click', 'p': (580, 500)},
            {'t': 'exchange'}, {'t': 'click', 'p': (530, 410)},
            {'t': 'click_change', 'p': (530, 410)}, {'t': 'click', 'p': (410, 410)},
            {'t': 'exchange'}, {'t': 'click', 'p': (440, 290)},
            {'t': 'click', 'p': (550, 440)},
        ],
    },
}

stage_data['challenge-task-2'] = {
    'start': {'1': (550, 180)},
    'action': [
        {'t': 'click', 'p': (460, 260)}, {'t': 'click', 'p': (690, 280)},
        {'t': 'click', 'p': (750, 320)}, {'t': 'click', 'p': (810, 400)},
        {'t': 'click', 'p': (730, 480)}, {'t': 'click', 'p': (540, 400)},
        {'t': 'click', 'p': (420, 400)},
    ],
}

stage_data['challenge-4'] = {
    'start': {'3': (262, 222), '2': (1207, 177), '1': (900, 685)},
    'action': [
        {'t': 'click', 'p': (555, 300)}, {'t': 'click', 'p': (660, 350)},
        {'t': 'click', 'p': (600, 500)}, {'t': 'exchange'},
        {'t': 'click_move', 'p': (777, 360)}, {'t': 'exchange'},
        {'t': 'exchange'}, {'t': 'click', 'p': (620, 350)},
        {'t': 'click', 'p': (660, 410)}, {'t': 'click_move', 'p': (780, 430)},
        {'t': 'click_change', 'p': (480, 350)}, {'t': 'click', 'p': (380, 350)},
        {'t': 'click', 'p': (620, 360)}, {'t': 'click_move', 'p': (720, 500)},
        {'t': 'click', 'p': (820, 490)}, {'t': 'click_move', 'p': (440, 440)},
        {'t': 'exchange'}, {'t': 'exchange'},
        {'t': 'click', 'p': (555, 490)}, {'t': 'click_move', 'p': (555, 440)},
        {'t': 'click', 'p': (730, 490)}, {'t': 'exchange'},
        {'t': 'click', 'p': (666, 390)}, {'t': 'click', 'p': (560, 430)},
        {'t': 'click_change', 'p': (620, 420)}, {'t': 'click', 'p': (730, 420)},
    ],
}

stage_data['challenge-task-4'] = {
    'start': {'3': (262, 222), '2': (1207, 177), '1': (900, 685)},
    'action': [
        {'t': 'click', 'p': (560, 290)}, {'t': 'click_move', 'p': (660, 350)},
        {'t': 'click_move', 'p': (640, 450)}, {'t': 'close_skip'},
        {'t': 'click', 'p': (610, 370)}, {'t': 'click', 'p': (660, 410)},
        {'t': 'click_change', 'p': (660, 420)}, {'t': 'click', 'p': (540, 410), 'not-wait': True},
        {'t': 'abort_fight'}, {'t': 'open_skip'},
        {'t': 'click_move', 'p': (640, 390)}, {'t': 'click', 'p': (840, 460)},
        {'t': 'click_move', 'p': (450, 430)}, {'t': 'click', 'p': (666, 410)},
        {'t': 'click', 'p': (555, 455)}, {'t': 'click', 'p': (660, 410)},
        {'t': 'click', 'p': (610, 380)}, {'t': 'exchange'},
        {'t': 'click', 'p': (610, 390)}, {'t': 'end-turn'},
    ],
}


TAB_LAYOUTS = (
    {
        'story': ((760, 110), (730, 110)),
        'task': ((935, 110), (900, 104)),
        'challenge': ((1125, 110), (1060, 104)),
        'challenge-task': ((1125, 110), (1060, 104)),
    },
    {
        'story': ((891, 110), (860, 104)),
        'task': ((1115, 110), (1060, 104)),
        'challenge': ((1190, 110), (1135, 104)),
        'challenge-task': ((1190, 110), (1135, 104)),
    },
)


def to_tab(self, t):
    if t not in TAB_LAYOUTS[0]:
        raise ValueError('不支持的活动页签: {0}'.format(t))

    # quest 模板仅用于确定尝试顺序，不能作为唯一布局判断依据。
    legacy_first = image.compare_image(self, 'cn_activity_quest', retry=0)
    layouts = TAB_LAYOUTS[::-1] if legacy_first else TAB_LAYOUTS
    for layout in layouts:
        click_pos, check_pos = layout[t]
        for _ in range(8):
            if color.check_rgb(self, check_pos, (34, 60, 85), threshold=55):
                return None
            self.click(*click_pos, False)
            time.sleep(0.3)

    raise restart.RestartTaskException('活动页签切换失败: {0}'.format(t))


is_exp = False


ACTIVITY_PAGE_MARKERS = (current_men, 'cm_activity-notice')


def to_activity_page(self, retry=120):
    pos = {
        'momo_talk_menu': (1205, 42, 0.95), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516), 'normal_task_task-info': (1234, 26),
        'normal_task_buy-ap-window': (920, 166), 'home_student': (1200, 573),
        'home_bus': (100, 160), 'new_year_guide': (1184, 156),
        'home_new-players': (1234, 26), 'god_cross_task': (55, 37),
        'cm_get-prize': (650, 640),
    }
    result = image.detect(self, ACTIVITY_PAGE_MARKERS, pos, retry=retry)
    if result is None:
        raise restart.RestartTaskException(
            '进入国服活动页面失败，超过{0}次图片检索'.format(retry)
        )
    return result


def start(self):
    if self.game_server != 'cn':
        return None
    home.go_home(self)
    to_activity_page(self)
    start_exp(self)
    start_bonus(self)
    rst = start_scan(self)
    if rst == 'return':
        home.go_home(self)
        return None
    start_dice(self)
    start_exchange(self)
    start_draw_card(self)
    finish_task(self)
    home.go_home(self)
    return None


def finish_task(self):
    self.md = self.tc
    self.md['story_exp']['enable'] = False
    self.md['task_exp']['enable'] = False
    self.md['bonus']['enable'] = False
    return None


def challenge_task(self):
    if not self.tc['challenge-task']['enable']:
        return None
    self.log_title('开始国服活动-挑战任务')
    tasks = {2: (1100, 280), 4: (1100, 475)}
    for s, p in tasks.items():
        to_activity_page(self)
        image.detect(self, 'normal_task_task-info', p, cl=p)
        start_fight(self, 'exp', 0, s, 'challenge-task')
    return None


def start_dice(self):
    if not self.tc['dice']['enable']:
        return None
    self.log_title('开始国服活动-掷骰子')
    to_activity_page(self)
    pos = {current_men: (515, 635)}
    image.detect(self, 'cm_dice-menu', pos, 1, retry=1)
    time.sleep(1)
    while True:
        if image.compare_image(self, 'cm_dice-need', 0, retry=0):
            self.logger.error('不能掷骰子了...')
            return None
        time.sleep(1)
        self.click(1180, 666, False)


def start_exchange(self):
    if not self.tc['exchange']['enable']:
        return None
    self.log_title('开始国服活动-兑换奖励')
    to_activity_page(self)
    pos = {current_men: (306, 614)}
    image.detect(self, 'cm_activity-exchange-menu', pos, 1, retry=1)
    time.sleep(1)
    self.click(125, 100, False)
    time.sleep(1)
    self.click(773, 317, False)
    time.sleep(1)
    self.click(768, 488, False)
    time.sleep(1)
    while True:
        time.sleep(1)
        if color.check_rgb(self, (393, 676), (245, 233, 75)):
            if image.compare_image(self, 'cm_activity-exchange-clean', 0, retry=0):
                self.click(1156, 113, False)
                time.sleep(0.5)
                self.click(767, 502)
            else:
                self.logger.error('不能抽卡了...')
                return None
            time.sleep(0.5)
            self.click(450, 650)
            time.sleep(0.5)
            pos = {'cm_activity-exchange-again': (932, 602), 'cm_activity-exchange-over': (670, 600)}
            image.detect(self, 'cm_activity-exchange-menu', pos, cl=(1135, 605), rate=0)


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
    self.log_title('开始国服活动-全自动开图')
    tabs = ['story', 'task']
    for tab in tabs:
        if not self.tc[tab + '_exp']['enable']:
            continue
        is_exp = True
        to_activity_page(self)
        do_exp(self, tab)
        is_exp = False
    return None


def open_gq(self, gq):
    stage1 = False
    stage2 = False
    stage3 = False
    gq = int(gq)
    if gq not in position_special:
        self.exit('本次活动不支持扫荡该关卡')
    x, y = activity_stage_position(gq, special=True)
    if gq <= 4 and not stage1:
        stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 150, 926, 700, 0.1))
    if 4 < gq < 9 and not stage2:
        stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 150, 926, 700, 0.1))
        stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 590, 926, 150, 0.5))
    if gq >= 9 and not stage3:
        stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 590, 926, 0, 0.1))
    if gq >= 9 and image.compare_image(self, 'cm_activity-prize-info', 3):
        y -= 100
    self.click(x, y)
    return None


def start_scan(self):
    if not self.tc['scan']['enable']:
        return None
    self.log_title('开始国服活动-扫荡')
    rst = to_activity_page(self)
    if rst == 'return':
        return None
    to_tab(self, 'task')
    stage_list = self.tc['scan']['stage']
    stage1 = False
    stage2 = False
    stage3 = False
    for task in stage_list:
        gq, count = task.split('-')
        gq = int(gq)
        if gq not in position:
            self.exit('本次活动不支持扫荡该关卡')
        x, y = activity_stage_position(gq)
        if gq <= 4 and not stage1:
            stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 150, 926, 700, 0.1))
            stage1 = True
        if 4 < gq < 9 and not stage2:
            stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 150, 926, 700, 0.1))
            stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 590, 926, 150, 0.5))
            stage2 = True
        if gq >= 9 and not stage3:
            stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 590, 926, 0, 0.1))
            stage3 = True
        if gq >= 9 and image.compare_image(self, 'cm_activity-prize-info', 3):
            y -= 100
        self.click(x, y)
        rst = stage.confirm_scan(self, gq, count, 99)
        rst2 = to_activity_page(self)
        if rst == 'return' or rst2 == 'return':
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
    self.log_title('开始国服活动-全自动加成')
    is_exp = True
    to_activity_page(self)
    is_exp = False
    tab = 'task'
    to_tab(self, tab)
    bonus_list = ['bonus1', 'bonus2', 'bonus3', 'bonus4']
    stage1 = False
    stage2 = False
    stage3 = False
    for i, bon in enumerate(bonus_list):
        if bon not in self.tc['bonus']:
            continue
        cu_bonus = self.tc['bonus'][bon]
        for gq in cu_bonus:
            lv = int(gq)
            x, y = activity_stage_position(lv)
            if lv <= 4 and not stage1:
                stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 150, 926, 700, 0.1))
                stage1 = True
            if 4 < lv < 9 and not stage2:
                stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 150, 926, 700, 0.1))
                stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 590, 926, 150, 0.5))
                stage2 = True
            if lv >= 9 and not stage3:
                stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 590, 926, 0, 0.1))
                stage3 = True
            if lv >= 9 and image.compare_image(self, 'cm_activity-prize-info', 3):
                y -= 100
            self.click(x, y)
            ends = ('normal_task_task-info-window-activity', 'normal_task_task-info-window')
            image.detect(self, ends, 1, rate=1)
            start_fight(self, 'bonus', i + 1, lv, tab)
    return None


def do_exp(self, tab):
    max_runs = len([key for key in stage_data if key.startswith(tab + '-')])
    for _ in range(max_runs):
        tmp = 'story' if tab == 'task' else 'task'
        to_tab(self, tmp)
        to_activity_page(self)
        to_tab(self, tab)
        stage.screen_swipe(self, 0, False, threshold2=False, reset=False, f=(926, 150, 926, 720, 0.1))
        state, stage_index = calc_need_fight_stage(self, tab)
        if state is None:
            self.logger.info('活动%s开图已完成，没有需要战斗的关卡', tab)
            return None
        start_fight(self, 'exp', 0, stage_index, tab)
    raise restart.RestartTaskException(
        '活动{0}开图超过最大关卡数，停止本轮任务'.format(tab)
    )


prev_bonus_index = -1


def start_fight(self, t, bonus_index, stage_index, tab):
    global prev_bonus_index
    pos = {
        'main_story_main-lv-start-task': (943, 532),
        'main_story_side-lv-start-task': (640, 511),
        'normal_task_story-quest2': (640, 511),
        'normal_task_story-quest3': (640, 511),
    }
    ends = ('god_cross_no-score', 'momo_talk_menu', 'normal_task_force-edit',
            'momo_talk_skip', 'momo_talk_confirm-skip', 'fight_start-task', 'cm_get-prize')
    end = image.detect(self, ends, pos, retry=300)
    if end is None:
        raise restart.RestartTaskException('活动关卡启动流程识别超时')
    if end == 'momo_talk_menu':
        skip_story(self)
        return start_fight(self, t, bonus_index, stage_index, tab)
    if end == 'god_cross_no-score':
        home.click_house_under(self)
        home.click_house_under(self)
        return None
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
        'momo_talk_confirm-skip': (770, 516), 'cn_activity_unlock': (1259, 62),
        'cm_get-prize': (650, 640),
    }
    result = image.detect(self, ACTIVITY_PAGE_MARKERS, possible, retry=300)
    if result is None:
        raise restart.RestartTaskException('战斗结束后无法返回活动页面')
    return None


def do_special_fight_or_scan(self):
    pass


def skip_story(self):
    pos = {
        'momo_talk_menu': (1205, 42), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516), 'cn_activity_unlock': (1259, 62),
    }
    ends = ('normal_task_force-edit', 'cm_get-prize')
    result = image.detect(self, ends, pos, retry=300)
    if result is None:
        raise restart.RestartTaskException('活动剧情跳过流程识别超时')
    return result


def wait_task_info(self, open_info=True):
    markers = (
        'cn_activity_info-window',
        'normal_task_task-info',
        'normal_task_side-quest',
    )
    if open_info:
        result = image.detect(
            self,
            markers,
            cl=(1130, 190),
            rate=0.5,
            retry=20,
        )
        if result is None:
            raise restart.RestartTaskException('活动关卡信息窗口识别失败')
        return result
    return any(image.compare_image(self, marker, retry=0) for marker in markers)


def calc_need_fight_stage(self, tab):
    wait_task_info(self)
    supported = sorted(
        int(key.rsplit('-', 1)[1])
        for key in stage_data
        if key.startswith(tab + '-')
    )
    for stage_index in supported:
        task_state = check_task_state(self, tab)
        self.logger.info('当前关卡状态为:{0}'.format(task_state))
        if task_state == 'sss':
            self.logger.warning('当前关卡已三星,查找下一关')
            self.click(1172, 358)
            continue
        if task_state is None:
            return (None, 0)
        return (task_state, stage_index)
    return (None, 0)


def check_task_state(self, tab):
    time.sleep(1)
    # 活动详情是覆盖在活动页上的弹窗，底层的 notice/menu 模板仍可能可见。
    # 因此只能以详情窗口是否存在判断是否已经遍历到末尾。
    if not wait_task_info(self, False):
        return None
    if tab == 'story':
        # 剧情详情不显示普通关卡的三星标志；未完成关卡会显示“首次”奖励。
        return (
            'no-sss'
            if image.compare_image(self, 'cn_activity_first-reward', 0, 0.8)
            else 'sss'
        )
    if image.compare_image(self, 'normal_task_sss', 0, 0.9):
        return 'sss'
    return 'no-sss'


def activity_stage_position(gq, special=False):
    positions = position_special if special else position
    slots = positions[int(gq)]
    return slots[(int(gq) - 1) % len(slots)]
