import time
from fuzzywuzzy import fuzz
import numpy as np

from common import image, color, ocr
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
)

ACTIVITY_TAB_LABELS = {
    'story': '故事',
    'task': '任务',
    'challenge': '挑战',
    'challenge-task': '挑战',
}
ACTIVITY_STAGE_TAB_AREA = (670, 75, 1210, 145)
ACTIVITY_BOTTOM_NAV_AREA = (30, 590, 650, 710)


def _activity_tab_selected(self, tab):
    screenshot = self.get_screenshot_array()
    for layout in TAB_LAYOUTS:
        check_pos = layout[tab][1]
        if not color.check_rgb(
            self, check_pos, (34, 60, 85), threshold=55,
            ss_data=screenshot,
        ):
            continue
        blue, _, red = screenshot[check_pos[1], check_pos[0]]
        if int(blue) - int(red) >= 20:
            return True
    return False


def _activity_tab_positions_by_ocr(self):
    if getattr(self, 'ocr', None) is None:
        return {}
    output = ocr.screenshot_cut_get_text(
        self, ACTIVITY_STAGE_TAB_AREA, 0, False,
    )
    result = {}
    for item in output:
        text = str(item.get('text', ''))
        pos = item.get('position')
        if pos is None:
            continue
        for tab, label in ACTIVITY_TAB_LABELS.items():
            if fuzz.ratio(text, label) <= 60:
                continue
            xs = [point[0] for point in pos]
            ys = [point[1] for point in pos]
            result[tab] = (
                ACTIVITY_STAGE_TAB_AREA[0] + int(sum(xs) / len(xs)),
                ACTIVITY_STAGE_TAB_AREA[1] + int(sum(ys) / len(ys)),
            )
    return result


def _activity_bottom_entry_by_ocr(self, labels):
    if getattr(self, 'ocr', None) is None:
        return None, False
    output = ocr.screenshot_cut_get_text(
        self, ACTIVITY_BOTTOM_NAV_AREA, 0, False,
    )
    best = None
    for item in output:
        text = str(item.get('text', ''))
        pos = item.get('position')
        if pos is None:
            continue
        score = max(fuzz.ratio(text, label) for label in labels)
        if score <= 60 or (best is not None and score <= best[0]):
            continue
        xs = [point[0] for point in pos]
        ys = [point[1] for point in pos]
        best = (
            score,
            (
                ACTIVITY_BOTTOM_NAV_AREA[0] + int(sum(xs) / len(xs)),
                ACTIVITY_BOTTOM_NAV_AREA[1] + int(sum(ys) / len(ys)),
            ),
        )
    return (best[1] if best is not None else None), bool(output)


def _enter_activity_feature_page(self, marker, labels, fallback_pos):
    if image.compare_image(self, marker, retry=0):
        return True
    click_pos, ocr_available = _activity_bottom_entry_by_ocr(self, labels)
    if click_pos is None:
        if ocr_available:
            self.logger.info('当前活动底栏没有玩法入口:%s', '/'.join(labels))
            return False
        click_pos = fallback_pos
    self.click(*click_pos, False)
    if image.compare_image(self, marker, retry=5):
        return True
    self.logger.warning('活动玩法入口已点击，但目标页面识别失败:%s', '/'.join(labels))
    if not is_activity_stage_page(self):
        self.click(55, 35, False)
        time.sleep(2)
    return False


def to_tab(self, t):
    if t not in ACTIVITY_TAB_LABELS:
        raise ValueError('不支持的活动页签: {0}'.format(t))
    tab = 'challenge' if t == 'challenge-task' else t

    if _activity_tab_selected(self, tab):
        return None

    positions = _activity_tab_positions_by_ocr(self)
    attempts = []
    if tab in positions:
        attempts.append(positions[tab])
    attempts.extend(layout[tab][0] for layout in TAB_LAYOUTS)

    for click_pos in dict.fromkeys(attempts):
        self.click(*click_pos, False)
        time.sleep(0.6)
        if _activity_tab_selected(self, tab):
            return None

    raise restart.RestartTaskException('活动页签切换失败: {0}'.format(t))


is_exp = False


ACTIVITY_PAGE_MARKERS = (current_men, 'cm_activity-notice')
ACTIVITY_HOME_ENTRY_POS = (1185, 215)
ACTIVITY_HOME_CAROUSEL_AREA = (1100, 155, 1260, 260)
ACTIVITY_HOME_CAROUSEL_DOT_AREA = (1160, 262, 1230, 272)
ACTIVITY_HOME_CAROUSEL_MAX_CANDIDATES = 8
ACTIVITY_HOME_CAROUSEL_POLL = 0.2
ACTIVITY_HOME_CAROUSEL_TIMEOUT = 30
ACTIVITY_HOME_CAROUSEL_STABLE_DELTA = 2.5
ACTIVITY_STAGE_CONTENT_AREA = (680, 140, 1210, 695)
ACTIVITY_FIRST_STAGE_POS = {
    'story': (1130, 190),
    'task': (1130, 190),
}
ACTIVITY_STORY_BUTTON_AREA = (1070, 145, 1195, 695)
ACTIVITY_STORY_NUMBER_X = (700, 770)
ACTIVITY_STORY_ICON_X = (715, 750)
ACTIVITY_STORY_ROW_MIN_HEIGHT = 30
DRAW_RESOURCE_AREA = (712, 165, 790, 202)
DRAW_SINGLE_COST_AREA = (780, 520, 870, 565)
DRAW_SINGLE_BUTTON_POS = (815, 568)
DRAW_SINGLE_COLOR_POS = (800, 600)
DRAW_SHUFFLE_BUTTON_POS = (1150, 185)
DRAW_SHUFFLE_COLOR_POS = (1150, 185)
DRAW_MAX_ACTIONS = 100


def _home_activity_carousel_index(screenshot):
    x1, y1, x2, y2 = ACTIVITY_HOME_CAROUSEL_DOT_AREA
    strip = screenshot[y1:y2, x1:x2].astype(np.int16)
    active = (strip[:, :, 0] - strip[:, :, 2] > 120) & (strip[:, :, 0] > 180)
    _, xs = np.where(active)
    if len(xs) < 3:
        return None
    return x1 + int(round(float(np.median(xs))))


def _wait_home_activity_candidate(self, excluded, timeout=ACTIVITY_HOME_CAROUSEL_TIMEOUT):
    deadline = time.monotonic() + timeout
    previous_index = None
    previous_crop = None
    x1, y1, x2, y2 = ACTIVITY_HOME_CAROUSEL_AREA
    while time.monotonic() < deadline:
        screenshot = self.get_screenshot_array()
        index = _home_activity_carousel_index(screenshot)
        crop = screenshot[y1:y2, x1:x2]
        stable = False
        if index is not None and index not in excluded and float(crop.mean()) >= 70:
            if previous_index == index and previous_crop is not None:
                delta = float(np.abs(crop.astype(np.int16) - previous_crop).mean())
                stable = delta <= ACTIVITY_HOME_CAROUSEL_STABLE_DELTA
        if stable:
            return index
        previous_index = index
        previous_crop = crop.copy()
        time.sleep(ACTIVITY_HOME_CAROUSEL_POLL)
    raise restart.RestartTaskException('主页活动轮播候选识别超时')


def open_next_home_activity_candidate(self):
    seen = getattr(self, '_activity_home_carousel_seen', set())
    if len(seen) >= ACTIVITY_HOME_CAROUSEL_MAX_CANDIDATES:
        raise restart.RestartTaskException('主页活动轮播没有可用的通用活动入口')
    index = _wait_home_activity_candidate(self, set(seen))
    seen.add(index)
    self._activity_home_carousel_seen = seen
    self.logger.info('尝试主页活动轮播候选，高亮点 x:%s', index)
    self.click(*ACTIVITY_HOME_ENTRY_POS, False)
    time.sleep(2)
    return False


def to_activity_page(self, retry=120):
    self._activity_home_carousel_seen = set()
    pos = {
        'restart_news': (1232, 42),
        'home_news': (1140, 100),
        'home_news2': (1140, 100),
        'home_news-intl': (1226, 54),
        'home_quick-home': (1233, 25),
        'home_student': (open_next_home_activity_candidate, (self,)),
        'momo_talk_menu': (1205, 42, 0.95), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516), 'normal_task_task-info': (1234, 26),
        'normal_task_buy-ap-window': (920, 166),
        'new_year_guide': (1184, 156),
        'home_new-players': (1234, 26), 'god_cross_task': (55, 37),
        'cm_get-prize': (650, 640),
    }
    for _ in range(ACTIVITY_HOME_CAROUSEL_MAX_CANDIDATES * 2 + 2):
        result = image.detect(self, ACTIVITY_PAGE_MARKERS, pos, retry=retry)
        if result is None:
            raise restart.RestartTaskException(
                '进入国服活动页面失败，超过{0}次图片检索'.format(retry)
            )
        if result == current_men:
            if is_target_activity_page(self, retry=1):
                return result
            self.logger.info('当前可能位于活动子页面，尝试返回活动关卡主页')
            self.click(55, 35, False)
            time.sleep(2)
            continue
        elif is_target_activity_page(self, retry=4):
            return result
        self.logger.warning('当前活动页不是通用活动关卡结构，返回首页重新选择活动入口')
        self.click(1233, 25)
        time.sleep(3)
    raise restart.RestartTaskException('国服通用活动关卡入口选择失败')


def is_target_activity_page(self, retry=0):
    if is_activity_stage_page(self):
        return not is_activity_ended(self)
    if retry <= 0:
        return False
    time.sleep(0.5)
    return is_target_activity_page(self, retry - 1)


def is_activity_ended(self):
    if getattr(self, 'ocr', None) is None:
        return False
    return ocr.screenshot_check_text(
        self, '活动时间已结束', ACTIVITY_STAGE_CONTENT_AREA, 0, 0, False,
    )


def has_activity_stage_tabs(self):
    if image.compare_image(self, 'cn_activity_stage-story-tab', retry=0, threshold=0.75):
        return True
    positions = _activity_tab_positions_by_ocr(self)
    labels = {ACTIVITY_TAB_LABELS[tab] for tab in positions}
    if len(labels) >= 2:
        return True
    selected = [
        _activity_tab_selected(self, tab)
        for tab in ('story', 'task', 'challenge')
    ]
    return sum(selected) == 1


def is_activity_stage_page(self):
    return has_activity_stage_tabs(self)


def enter_activity_stage_page(self):
    if is_activity_stage_page(self):
        return None
    raise restart.RestartTaskException('活动右上关卡页签识别失败')


def start(self):
    if self.game_server != 'cn':
        return None
    home.go_home(self)
    to_activity_page(self)
    start_exp(self)
    challenge_task(self)
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
    if 'challenge-task' in self.md:
        self.md['challenge-task']['enable'] = False
    return None


def challenge_task(self):
    if not self.tc.get('challenge-task', {}).get('enable', False):
        return None
    self.log_title('开始国服活动-挑战任务')
    tasks = {2: (1100, 280), 4: (1100, 475)}
    for s, p in tasks.items():
        to_activity_page(self)
        to_tab(self, 'challenge')
        image.detect(self, 'normal_task_task-info', p, cl=p)
        start_fight(self, 'exp', 0, s, 'challenge-task')
    return None


def start_dice(self):
    if not self.tc['dice']['enable']:
        return None
    self.log_title('开始国服活动-掷骰子')
    to_activity_page(self)
    if not _enter_activity_feature_page(
        self, 'cm_dice-menu', ('骰子', '赛跑'), (515, 635),
    ):
        return None
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
    if not _enter_activity_feature_page(
        self,
        'cm_activity-exchange-menu',
        ('兑换', '商店'),
        (306, 614),
    ):
        return None
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
    if not _enter_activity_feature_page(
        self, 'brzx_draw-menu', ('抽卡', '卡片商店'), (520, 640),
    ):
        return None
    time.sleep(1)
    return draw_cards_on_current_page(self)


def draw_cards_on_current_page(self):
    for _ in range(DRAW_MAX_ACTIONS):
        screenshot = self.get_screenshot_array()
        state = _draw_card_state(self, screenshot)
        if state == 'done':
            self.logger.info('活动卡片道具不足，结束抽卡')
            return None
        if state == 'shuffle':
            self.click(*DRAW_SHUFFLE_BUTTON_POS, False)
            time.sleep(1)
            continue
        self.click(*DRAW_SINGLE_BUTTON_POS, False)
        _close_draw_reward(self)
    raise restart.RestartTaskException('活动卡片商店操作次数异常')


def _close_draw_reward(self):
    if not image.compare_image(
        self,
        'cm_get-prize',
        retry=60,
        threshold=0.8,
    ):
        raise restart.RestartTaskException('活动卡片奖励弹窗识别失败')
    self.click(640, 635, False)
    if not image.compare_image(
        self,
        'cm_get-prize',
        retry=60,
        threshold=0.8,
        n=True,
    ):
        raise restart.RestartTaskException('活动卡片奖励弹窗关闭失败')


def _draw_card_state(self, screenshot):
    if color.check_rgb(
        self,
        DRAW_SINGLE_COLOR_POS,
        (118, 220, 255),
        threshold=45,
        ss_data=screenshot,
    ):
        return 'draw'

    resource = _draw_number(self, DRAW_RESOURCE_AREA, screenshot)
    cost = _draw_number(self, DRAW_SINGLE_COST_AREA, screenshot)
    if resource is None or cost is None or resource < cost:
        return 'done'
    if color.check_rgb(
        self,
        DRAW_SHUFFLE_COLOR_POS,
        (45, 70, 99),
        threshold=55,
        ss_data=screenshot,
    ):
        return 'shuffle'
    return 'done'


def _draw_number(self, area, screenshot):
    engine = getattr(self, 'ocrNum', None)
    if engine is None:
        self.logger.warning('数字 OCR 未初始化，停止活动卡片商店操作')
        return None
    try:
        crop = image.screenshot_cut(self, area, 0, False, ss=screenshot)
        output = engine.ocr(crop) or []
        if not output:
            return None
        item = max(output, key=lambda value: float(value.get('score', 1.0)))
        text = str(item.get('text', ''))
        score = float(item.get('score', 1.0))
        digits = ''.join(char for char in text if char.isdigit())
        value = int(digits) if digits and score >= 0.25 else None
        self.logger.info(
            '活动卡片数字 OCR area:%s text:%s score:%.3f value:%s',
            area, text, score, value,
        )
        return value
    except Exception as exc:
        self.logger.warning('活动卡片商店数字 OCR 失败:%s', exc)
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
        to_activity_page(self)
        enter_activity_stage_page(self)
        to_tab(self, tab)
        reset_activity_stage_list(self, tab)
        state, stage_index = calc_need_fight_stage(self, tab)
        if state is None:
            self.logger.info('活动%s开图已完成，没有需要战斗的关卡', tab)
            return None
        start_fight(self, 'exp', 0, stage_index, tab)
    raise restart.RestartTaskException(
        '活动{0}开图超过最大关卡数，停止本轮任务'.format(tab)
    )


def reset_activity_stage_list(self, tab):
    stage.screen_swipe(
        self, 0, False, threshold2=False, reset=False,
        f=(926, 150, 926, 720, 0.1),
    )
    if tab == 'task':
        self.swipe(930, 300, 930, 520, 0.5)
        time.sleep(1)


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
            # 活动故事战斗使用固定编队，新版本会禁用右侧的预设入口。
            if tab != 'story' and isinstance(stage_data[gk], int):
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
        'cm_get-prize': (650, 640),
        'main_story_fight-confirm': (1168, 659), 'main_story_fight-fail': (647, 655),
        'fight_pass-confirm': (1170, 666), 'fight_task-finish-confirm': (1033, 666),
        'fight_prize-confirm1': (645, 670), 'fight_prize-confirm2': (775, 660),
        'momo_talk_menu': (1205, 42), 'momo_talk_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516), 'cn_activity_unlock': (1259, 62),
    }
    result = image.detect(
        self,
        ACTIVITY_PAGE_MARKERS,
        possible,
        pre_func=handle_activity_fight_prompt,
        pre_argv=(self,),
        retry=300,
    )
    if result is None:
        raise restart.RestartTaskException('战斗结束后无法返回活动页面')
    return None


def handle_activity_fight_prompt(self):
    now = time.monotonic()
    last_check = getattr(self, '_last_activity_fight_prompt_ocr', 0.0)
    if now - last_check < 1.5:
        return None
    self._last_activity_fight_prompt_ocr = now

    engine = getattr(self, 'ocr', None)
    screenshot = getattr(self, 'latest_img_array', None)
    if engine is None or screenshot is None:
        return None
    try:
        output = engine.ocr(screenshot[70:710, 250:1030]) or []
        text = ''.join(
            str(item.get('text', ''))
            for item in output
            if isinstance(item, dict)
        ).replace(' ', '')
    except Exception as exc:
        self.logger.debug('活动战斗提示 OCR 失败:%s', exc)
        return None

    if '战败' in text and '确认' in text:
        self.logger.info('识别到活动战败结算，点击确认')
        self.click(640, 655, False)
        return ('click', 'progress')

    is_battle_tip = all(label in text for label in ('提示', '返回大厅', '确认'))
    if not is_battle_tip:
        return None
    self.logger.info('识别到活动战斗提示，点击确认')
    self.click(775, 660, False)
    return ('click', 'progress')


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


def wait_task_info(self, open_info=True, click_pos=(1130, 190)):
    markers = (
        'cn_activity_info-window',
        'normal_task_task-info',
        'normal_task_side-quest',
    )
    if open_info:
        result = image.detect(
            self,
            markers,
            cl=click_pos,
            rate=0.5,
            retry=20,
        )
        if result is None:
            raise restart.RestartTaskException('活动关卡信息窗口识别失败')
        return result
    return any(image.compare_image(self, marker, retry=0) for marker in markers)


def calc_need_fight_stage(self, tab):
    if tab == 'story':
        return calc_need_story_stage(self)

    wait_task_info(self, click_pos=ACTIVITY_FIRST_STAGE_POS[tab])
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


def calc_need_story_stage(self):
    supported = {
        int(key.rsplit('-', 1)[1])
        for key in stage_data
        if key.startswith('story-')
    }
    for _ in range(6):
        screenshot = self.get_screenshot_array()
        unlocked_rows = _story_stage_button_rows(screenshot, unlocked=True)
        for center_y in unlocked_rows:
            stage_index = _story_stage_number(self, screenshot, center_y)
            if stage_index not in supported:
                continue
            completed = _story_stage_completed(screenshot, center_y)
            self.logger.info(
                '活动故事列表关卡:%s 状态:%s',
                stage_index,
                '已完成' if completed else '未完成',
            )
            if completed:
                continue
            wait_task_info(self, click_pos=(1130, center_y))
            return ('no-sss', stage_index)

        locked_rows = _story_stage_button_rows(screenshot, unlocked=False)
        if locked_rows:
            self.logger.info('活动故事列表已到达首个未解锁关卡')
            return (None, 0)

        before = screenshot[
            ACTIVITY_STORY_BUTTON_AREA[1]:ACTIVITY_STORY_BUTTON_AREA[3],
            ACTIVITY_STORY_BUTTON_AREA[0]:ACTIVITY_STORY_BUTTON_AREA[2],
        ].copy()
        self.swipe(930, 620, 930, 260, 0.5)
        time.sleep(1)
        after = self.get_screenshot_array()[
            ACTIVITY_STORY_BUTTON_AREA[1]:ACTIVITY_STORY_BUTTON_AREA[3],
            ACTIVITY_STORY_BUTTON_AREA[0]:ACTIVITY_STORY_BUTTON_AREA[2],
        ]
        if before.shape == after.shape:
            delta = float(np.mean(np.abs(before.astype(np.int16) - after.astype(np.int16))))
            if delta < 2.0:
                self.logger.info('活动故事列表已滚动到底部')
                return (None, 0)

    raise restart.RestartTaskException('活动故事列表扫描超过最大页数')


def _story_stage_button_rows(screenshot, unlocked):
    x1, y1, x2, y2 = ACTIVITY_STORY_BUTTON_AREA
    crop = screenshot[y1:y2, x1:x2]
    blue = crop[:, :, 0]
    green = crop[:, :, 1]
    red = crop[:, :, 2]
    if unlocked:
        mask = (blue > 180) & (green > 140) & (red < 170)
    else:
        mask = (
            (blue > 55) & (blue < 130) &
            (green > 35) & (green < 110) &
            (red < 80)
        )
    present = np.count_nonzero(mask, axis=1) > 40
    edges = np.diff(np.r_[False, present, False].astype(np.int8))
    starts = np.flatnonzero(edges == 1)
    ends = np.flatnonzero(edges == -1)
    return [
        y1 + (int(start) + int(end)) // 2
        for start, end in zip(starts, ends)
        if end - start >= ACTIVITY_STORY_ROW_MIN_HEIGHT
    ]


def _story_stage_number(self, screenshot, center_y):
    engine = getattr(self, 'ocrNum', None)
    if engine is None:
        raise restart.RestartTaskException('数字OCR未初始化，无法读取活动故事关卡')
    x1, x2 = ACTIVITY_STORY_NUMBER_X
    crop = screenshot[max(0, center_y - 35):center_y + 5, x1:x2]
    try:
        output = engine.ocr(crop) or []
    except Exception as exc:
        raise restart.RestartTaskException(
            '活动故事列表关卡编号OCR失败:{0}'.format(exc)
        ) from exc
    candidates = []
    for item in output:
        text = str(item.get('text', ''))
        digits = ''.join(char for char in text if char.isdigit())
        if digits:
            candidates.append((float(item.get('score', 0.0)), int(digits)))
    if not candidates:
        self.logger.warning('活动故事列表关卡编号OCR无结果:y=%s', center_y)
        return None
    score, stage_index = max(candidates)
    if score < 0.4:
        self.logger.warning(
            '活动故事列表关卡编号OCR置信度过低:y=%s score=%.3f',
            center_y,
            score,
        )
        return None
    return stage_index


def _story_stage_completed(screenshot, center_y):
    x1, x2 = ACTIVITY_STORY_ICON_X
    crop = screenshot[center_y:center_y + 32, x1:x2]
    if crop.size == 0:
        return False
    blue = crop[:, :, 0]
    green = crop[:, :, 1]
    red = crop[:, :, 2]
    yellow = (blue < 130) & (green > 140) & (red > 160)
    return int(np.count_nonzero(yellow)) >= 8


def check_task_state(self, tab):
    time.sleep(1)
    # 活动详情是覆盖在活动页上的弹窗，底层的 notice/menu 模板仍可能可见。
    # 因此只能以详情窗口是否存在判断是否已经遍历到末尾。
    if not wait_task_info(self, False):
        return None
    if image.compare_image(self, 'normal_task_sss', 0, 0.9):
        return 'sss'
    return 'no-sss'


def activity_stage_position(gq, special=False):
    positions = position_special if special else position
    slots = positions[int(gq)]
    return slots[(int(gq) - 1) % len(slots)]
