import time
import time
import cv2
import numpy as np
from fuzzywuzzy import fuzz
from common import stage, image, limit, color, ocr
from modules.activity import alive
from modules.baas import home
from modules.exp.normal_task import exp_normal_task
from modules.story import momo_talk

part_position = {
    '1': (680, 250),
    '2': (770, 450),
    '3': (460, 250),
    '4': (710, 460),
    '5': (650, 250),
    'EX': (570, 460),
    'F': (850, 633),
}

chapter_position = {
    1: (1020, 315),
    2: (1020, 380),
    3: (1020, 450),
    4: (1020, 510),
    5: (1020, 580),
}

AUTO_BATTLE_BUTTON = (1215, 675)
AUTO_BATTLE_TEXT_AREA = (1155, 645, 1268, 704)


def reset_battle_auto_state(self):
    self._battle_auto_clicked = False


def has_text_in_area(self, text, area, ss=None):
    if ss is None:
        return ocr.screenshot_check_text(self, text, area, 0)
    crop = ss[area[1]:area[3], area[0]:area[2], :]
    out = self.ocr.ocr(crop)
    matched = any(text in d.get('text', '') or fuzz.ratio(d.get('text', ''), text) > 60 for d in out)
    self.logger.info('screenshot_check_text T:%s R:%s', text, matched)
    return matched


def battle_auto_button_visible(self, ss=None):
    return has_text_in_area(self, '自动', AUTO_BATTLE_TEXT_AREA, ss)


def battle_auto_enabled(self, ss=None):
    return image.compare_image(self, 'fight_auto-over', 0, 0.6, ss=ss)


stage_data = {
    'F-1-14': {
        'start': {
            '2': (670, 470),
            '3': (660, 300),
            '1': (460, 470),
        },
        'action': [
            {'t': 'click', 'p': (740, 590)},
            {'t': 'click', 'p': (700, 190), 'f': 1},
            {'t': 'click', 'p': (520, 390), 'f': 3},
            {'t': 'exchange'},
            {'t': 'click', 'p': (690, 190)},
            {'t': 'exchange'},
            {'t': 'exchange'},
            {'t': 'click', 'p': (450, 350)},
            {'t': 'click', 'p': (730, 430)},
            {'t': 'click', 'p': (660, 410)},
        ],
    },
    'F-2-1': {
        'start': {
            '2': (670, 470),
            '3': (660, 300),
            '1': (460, 470),
        },
        'action': [
            {'t': 'click', 'p': (570, 370), 'f': 1},
            {'t': 'click', 'p': (700, 470), 'f': 1},
            {'t': 'click', 'p': (750, 390)},
            {'t': 'click', 'p': (670, 450)},
        ],
    },
    'F-2-6': {
        'start': {
            '2': (670, 470),
            '3': (660, 300),
            '1': (460, 470),
        },
        'action': [
            {'t': 'click', 'p': (560, 530), 'f': 1},
            {'t': 'click', 'p': (750, 390)},
            {'t': 'exchange'},
            {'t': 'click', 'p': (850, 490)},
            {'t': 'click', 'p': (690, 230), 'f': 2},
            {'t': 'click', 'p': (750, 390)},
            {'t': 'click', 'p': (700, 450)},
        ],
    },
    'F-2-9': {
        'start': {
            '2': (670, 470),
            '3': (660, 300),
            '1': (460, 470),
        },
        'action': [
            {'t': 'click', 'p': (560, 530)},
            {'t': 'click', 'p': (840, 490)},
            {'t': 'click', 'p': (560, 520)},
            {'t': 'end-turn', 'f': 2},
            {'t': 'click', 'p': (440, 510)},
            {'t': 'click', 'p': (770, 370)},
        ],
    },
    'F-2-12': {
        'start': {
            '2': (670, 470),
            '3': (660, 300),
            '1': (460, 470),
        },
        'action': [
            {'t': 'click', 'p': (570, 540)},
            {'t': 'click', 'p': (680, 300), 'f': 1},
            {'t': 'click', 'p': (700, 470)},
            {'t': 'click', 'p': (730, 270)},
        ],
    },
    'F-2-15': {
        'start': {
            '2': (670, 470),
            '3': (660, 300),
            '1': (460, 470),
        },
        'action': [
            {'t': 'click', 'p': (410, 480), 'f': 1},
            {'t': 'end-turn'},
            {'t': 'click', 'p': (660, 350)},
            {'t': 'click', 'p': (570, 450)},
        ],
    },
    'F-2-17': {
        'start': {
            '2': (670, 470),
            '3': (660, 300),
            '1': (460, 470),
        },
        'action': [
            {'t': 'click', 'p': (640, 470), 'f': 1},
            {'t': 'end-turn'},
            {'t': 'click', 'p': (830, 490)},
            {'t': 'click', 'p': (660, 300)},
        ],
    },
    'F-2-20': {
        'start': {
            '2': (670, 470),
            '3': (660, 300),
            '1': (460, 470),
        },
        'action': [
            {'t': 'exchange'},
            {'t': 'click', 'p': (460, 350), 'f': 1},
            {'t': 'exchange'},
            {'t': 'exchange'},
            {'t': 'click', 'p': (888, 438), 'f': 1},
            {'t': 'click', 'p': (580, 310)},
            {'t': 'exchange'},
            {'t': 'click', 'p': (510, 210)},
            {'t': 'click', 'p': (730, 450)},
            {'t': 'click', 'p': (880, 450)},
            {'t': 'click', 'p': (620, 410)},
            {'t': 'end-turn', 'f': 2},
            {'t': 'click', 'p': (630, 420)},
        ],
    },
    'F-3-14': {
        'start': {
            '2': (670, 470),
            '3': (660, 300),
            '1': (460, 470),
        },
        'action': [
            {'t': 'click', 'p': (740, 590)},
            {'t': 'click', 'p': (700, 190), 'f': 1},
            {'t': 'click', 'p': (520, 390), 'f': 3},
            {'t': 'exchange'},
            {'t': 'click', 'p': (690, 190)},
            {'t': 'exchange'},
            {'t': 'exchange'},
            {'t': 'click', 'p': (450, 350)},
            {'t': 'click', 'p': (730, 430)},
            {'t': 'click', 'p': (660, 410)},
        ],
    },
}


def to_main_story(self):
    pos = {
        'home_student': (1200, 573),
        'home_bus': (1033, 260),
        'main_story_story': (240, 350),
        'main_story_go-main-story': (58, 108),
        'main_story_choose-plot': (56, 38),
    }
    ends = (('main_story_menu1', 0.9),)
    home.to_menu(self, ends, pos, rate=1)


def choose_story_pre(self):
    ss = self.latest_img_array
    if image.compare_image(self, 'main_story_choose-plot', 0, 0.7, ss=ss):
        return 'end', 'main_story_choose-plot'
    if image.compare_image(self, 'restart_menu', 0, 0.7, ss=ss):
        self.click(640, 500, False)
        time.sleep(3)
        return 'click', 'restart_menu', 'progress'
    if close_story_reward(self, ss):
        return 'click', 'story_reward', 'progress'
    if (has_text_in_area(self, '\u4e0b\u4e00\u8bdd', (560, 290, 720, 345), ss)
            or has_text_in_area(self, '\u8bdd', (560, 290, 720, 345), ss)):
        self.click(640, 635, False)
        time.sleep(1)
        return 'click', 'story_title', 'progress'
    if image.compare_image(self, 'momo_talk_confirm-skip', 0, 0.5, ss=ss):
        self.click(770, 516, False)
        time.sleep(1)
        return 'click', 'skip_confirm', 'progress'
    if image.compare_image(self, 'main_story_continue', 0, 0.5, ss=ss):
        self.click(505, 520, False)
        time.sleep(1)
        return 'click', 'continue', 'progress'
    if image.compare_image(self, 'main_story_skip-story', 0, 0.5, ss=ss):
        self.click(770, 520, False)
        time.sleep(1)
        return 'click', 'skip_story', 'progress'
    if image.compare_image(self, 'momo_talk_menu', 0, 0.8, ss=ss):
        momo_talk.skip_plot(self)
        time.sleep(1)
        return 'click', 'story_menu', 'progress'

    last_tap = getattr(self, '_choose_story_idle_click_at', 0)
    if time.time() - last_tap > 5:
        self.click(640, 635, False)
        self._choose_story_idle_click_at = time.time()
        return 'click', 'idle_story_tap'
    return None


def to_choose_story(self):
    self._choose_story_idle_click_at = 0
    pos = {
        'restart_menu': (640, 500),
        'restart_update': (770, 500),
        'restart_update2': (770, 555),
        'restart_news': (1232, 42),
        'home_news': (1142, 104),
        'home_news2': (1142, 104),
        'fight_fail': (647, 655),
        'fight_pass-confirm': (1170, 666),
        'momo_talk_begin-relationship': (920, 568),
        'momo_talk_menu': (1205, 42),
        'momo_talk_skip': (1212, 116),
        'main_story_get-prize': (644, 634),
        'main_story_continue': (505, 520),
        'main_story_skip-story': (770, 520),
        'cm_get-prize': (645, 633, 0.7),
    }
    image.detect(self, 'main_story_choose-plot', pos, pre_func=choose_story_pre, pre_argv=(self,))


def start(self):
    home.go_home(self)
    start_story(self)
    home.go_home(self)


def check_finish(self):
    ss = self.get_screenshot_array()
    if (image.compare_image(self, 'main_story_clearance', 0, 0.8, ss=ss)
            or image.compare_image(self, 'main_story_current-clearance', 0, 0.8, ss=ss)):
        return None
    return 'main_story_choose-plot'


def story_row_candidates(self):
    ss = self.get_screenshot_array()
    new_rows = []
    active_rows = []
    for y in (250, 360, 465, 572):
        entry_button = ss[max(0, y - 35):min(ss.shape[0], y + 35), 930:1185, :]
        entry_hsv = cv2.cvtColor(entry_button, cv2.COLOR_BGR2HSV)
        entry_mask = cv2.inRange(entry_hsv, np.array([88, 50, 160]), np.array([105, 255, 255]))
        entry_area = int(np.count_nonzero(entry_mask))

        new_mark = ss[max(0, y - 65):min(ss.shape[0], y - 25), 620:675, :]
        new_hsv = cv2.cvtColor(new_mark, cv2.COLOR_BGR2HSV)
        new_mask = cv2.inRange(new_hsv, np.array([18, 80, 120]), np.array([45, 255, 255]))
        _, _, new_stats, _ = cv2.connectedComponentsWithStats(new_mask)
        new_area = int(new_stats[1:, cv2.CC_STAT_AREA].max()) if len(new_stats) > 1 else 0

        self.logger.info('main_story row_y:%s new_area:%s entry_area:%s', y, new_area, entry_area)
        if entry_area < 1000:
            continue
        active_rows.append(y)
        if new_area >= 80:
            new_rows.append(y)
    return new_rows + [y for y in active_rows if y not in new_rows]


def open_available_plot(self):
    rows = story_row_candidates(self)
    for y in rows:
        for x in (1050, 1115, 980):
            self.click(x, y, False)
            time.sleep(1)
            ss = self.get_screenshot_array()
            if image.compare_image(self, 'main_story_plot-info', 0, 0.7, ss=ss):
                return True
            if not image.compare_image(self, 'main_story_choose-plot', 0, 0.7, ss=ss):
                return image.compare_image(self, 'main_story_plot-info', retry=5)
    return False


def lianhe_fihgt(self):
    pos = {
        'main_story_finish-stone': (915, 160),
        'main_story_choose-plot': (125, 210),
        'main_story_join-lianhe': (960, 590),
    }
    image.detect(self, 'main_story_lianhe-fight', pos)
    position = [
        (200, 330), (420, 420), (560, 630), (620, 200),
        (1070, 360), (850, 120), (777, 430),
    ]
    for p in position:
        image.compare_image(self, 'main_story_lianhe-info', 10, 1, cl=p)
        time.sleep(1)
        if image.compare_image(self, 'main_story_lianhe-finish', 5):
            self.click(922, 95)
            continue
        image.compare_image(self, 'main_story_lianhe-edit-force', threshold=0.6, cl=(640, 580), rate=1)
        image.compare_image(self, 'main_story_lianhe-edit-force', threshold=0.6, cl=(1171, 670), rate=1, n=True)
        auto_fight(self)
        stage.wait_loading(self)
        check_momo_talk(self)
        self.logger.info('强制等待30秒...')
        time.sleep(30)
        wait_fight_over(self)


def start_admission(self, chapter):
    if check_finish(self) is None:
        self.logger.error('剧情已经完成了')
        return

    if not open_available_plot(self):
        self.logger.error('当前章节没有可进入剧情')
        return

    is_fight = image.compare_image(self, 'main_story_plot-fight', 0, 0.6)

    if chapter == '2' and image.compare_image(self, 'main_story_finish-stone', 0, 0.9):
        lianhe_fihgt(self)
        start(self)
        return

    if chapter == '3' and image.compare_image(self, 'main_story_finish-stone3', 0, 0.9):
        self.click(915, 160)
        time.sleep(1)
        self.click(130, 200)
        time.sleep(1)
        self.exit('清手动完成占领战')
        return

    if chapter == '4' and image.compare_image(self, 'main_story_finish-stone4', 0, 0.9):
        self.click(915, 160)
        self.exit('清手动完成决战')
        return

    retry = 30
    if chapter == '4' and image.compare_image(self, 'main_story_finish-seven', 0, 0.9):
        retry = 300

    momo_talk.skip_plot(self)

    if is_fight:
        ends = ('fight_start-task', 'fight_force-attack')
        end = image.detect(self, ends)

        if end == 'fight_force-attack':
            handle_force_attack(self)
        else:
            exp_normal_task.wait_over(self)
            area = image.get_box(self, 'main_story_stage')
            stage_index = int(ocr.screenshot_get_text(self, area, self.ocrNum))
            gk = 'F-{0}-{1}'.format(chapter, stage_index)
            self.stage_data = stage_data

            if gk not in stage_data:
                self.logger.critical('当前关卡（{0}）卡暂不支持开图，请联系奇犽揍敌客x'.format(gk))
                self.exit(0)

            exp_normal_task.to_tart_task_page(self)
            self.logger.info('开始: {0}'.format(gk))
            exp_normal_task.start_fight(self, 0, gk)

    settle_story_playback(self)
    return start_admission(self, chapter)


def check_momo_talk(self):
    if image.compare_image(self, 'momo_talk_confirm-skip', 0, 0.5):
        self.click(770, 520, False)

    if image.compare_image(self, 'momo_talk_begin-relationship', 0, 0.5):
        self.click(920, 568, False)
        time.sleep(5)
        image.compare_image(self, 'momo_talk_confirm-skip', threshold=0.5, cl=(1212, 114))

    if image.compare_image(self, 'main_story_get-prize', 0, 0.5):
        self.click(644, 634, False)
        time.sleep(1)
        self.click(770, 520, False)


def handle_force_attack(self):
    prepare_force_attack_team(self)
    if image.compare_image(self, 'fight_force-attack', 3, 0.7):
        self.click(1163, 658, False)
        time.sleep(2)
    if self.game_server == 'cn':
        auto_fight(self)
        time.sleep(3)
    else:
        auto_fight(self)
        self.click(1235, 97)
        time.sleep(1)
        self.click(772, 500)


def prepare_force_attack_team(self):
    self.click(1200, 180, False)
    time.sleep(1)
    self.click(940, 600, False)
    time.sleep(1)
    self.click(1170, 600, False)
    time.sleep(2)


def close_story_reward(self, ss=None):
    if ss is None:
        ss = self.get_screenshot_array()
    if (image.compare_image(self, 'main_story_get-prize', 0, 0.5, ss=ss)
            or image.compare_image(self, 'cm_get-prize', 0, 0.6, ss=ss)):
        self.click(640, 635, False)
        time.sleep(0.8)
        return True
    if ocr.screenshot_check_text(self, '点击继续', (560, 610, 720, 655), 1):
        self.click(640, 635, False)
        time.sleep(0.8)
        return True
    return False


def settle_story_playback(self, timeout=300):
    t_start = time.time()
    while time.time() - t_start < timeout:
        self.latest_img_array = self.get_screenshot_array()

        if image.compare_image(self, 'main_story_choose-plot', 0, 0.7, ss=self.latest_img_array):
            reset_battle_auto_state(self)
            return True

        if close_story_reward(self, self.latest_img_array):
            reset_battle_auto_state(self)
            t_start = time.time()
            continue

        if image.compare_image(self, 'fight_fail', 0, 0.6, ss=self.latest_img_array):
            reset_battle_auto_state(self)
            self.click(647, 655, False)
            time.sleep(2)
            t_start = time.time()
            continue

        if image.compare_image(self, 'fight_pass-confirm', 0, 0.7, ss=self.latest_img_array):
            reset_battle_auto_state(self)
            self.click(1170, 666, False)
            time.sleep(2)
            t_start = time.time()
            continue

        if (image.compare_image(self, 'fight_force-attack', 0, 0.7, ss=self.latest_img_array)
                or image.compare_image(self, 'main_story_plot-attack', 0, 0.7, ss=self.latest_img_array)):
            handle_force_attack(self)
            t_start = time.time()
            continue

        if (has_text_in_area(self, '\u4e0b\u4e00\u8bdd', (560, 290, 720, 345), self.latest_img_array)
                or has_text_in_area(self, '\u8bdd', (560, 290, 720, 345), self.latest_img_array)):
            self.click(640, 635, False)
            time.sleep(1)
            t_start = time.time()
            continue

        if battle_auto_button_visible(self, self.latest_img_array):
            ensure_auto_enabled(self, self.latest_img_array)
            time.sleep(3)
            t_start = time.time()
            continue

        if image.compare_image(self, 'momo_talk_confirm-skip', 0, 0.5, ss=self.latest_img_array):
            self.click(770, 516, False)
            time.sleep(1)
            t_start = time.time()
            continue

        if image.compare_image(self, 'momo_talk_menu', 0, 0.8, ss=self.latest_img_array):
            momo_talk.skip_plot(self)
            time.sleep(1)
            t_start = time.time()
            continue

        if image.compare_image(self, 'main_story_continue', 0, 0.5, ss=self.latest_img_array):
            self.click(505, 520, False)
            time.sleep(1)
            t_start = time.time()
            continue

        if image.compare_image(self, 'main_story_skip-story', 0, 0.5, ss=self.latest_img_array):
            self.click(770, 520, False)
            time.sleep(1)
            t_start = time.time()
            continue

        check_momo_talk(self)
        time.sleep(1)

    self.logger.warning('等待剧情播放收束超时')
    return False


def wait_fight_over(self):
    exp_normal_task.to_end_over(self)
    while True:
        if image.compare_image(self, 'momo_talk_begin-relationship', 0, 0.5):
            self.click(920, 568, False)
        pos = {
            'main_story_get-prize': (644, 634),
            'main_story_continue': (505, 520),
            'main_story_skip-story': (770, 520),
        }
        end = image.detect(self, 'main_story_choose-plot', pos, 1, 600)
        if end == 'main_story_continue' or end == 'main_story_skip-story':
            return


def check_jp_continue(self):
    image.compare_image(self, 'main_story_skip-story2', threshold=0.5, cl=(757, 451))


def skip_main_story_plot(self):
    image.compare_image(self, 'fight_fail', retry=5, cl=(647, 655), rate=1, n=True)
    image.compare_image(self, 'main_story_continue', retry=5, cl=(505, 520), rate=1)
    image.compare_image(self, 'main_story_continue', retry=5, cl=(505, 520), rate=1, n=True)
    image.compare_image(self, 'main_story_skip-story', retry=5, cl=(770, 520), rate=1)
    image.compare_image(self, 'main_story_skip-story', retry=5, cl=(770, 520), rate=1, n=True)


def change_acc_auto(self):
    image.compare_image(self, 'fight_confirm2', threshold=0.5, cl=(1163, 658), rate=1)
    image.compare_image(self, 'fight_confirm2', threshold=0.5, cl=(1163, 658), rate=1, n=True)
    image.compare_image(self, 'main_story_skip-story', retry=5, cl=(770, 520), rate=1)
    image.compare_image(self, 'main_story_skip-story', retry=5, cl=(770, 520), rate=1, n=True)


def auto_fight_put_skill(self):
    reset_battle_auto_state(self)
    ensure_auto_enabled(self)
    self.click(1123, 545, False)
    ensure_auto_enabled(self)

    for i in range(100):
        if image.compare_image(self, 'fight_tasking', 0, 0.6):
            return
        time.sleep(1)


def ensure_auto_enabled(self, ss=None):
    if ss is None:
        ss = self.get_screenshot_array()
    if battle_auto_enabled(self, ss):
        return True

    if getattr(self, '_battle_auto_clicked', False):
        return False

    if not battle_auto_button_visible(self, ss):
        return False

    self.click(*AUTO_BATTLE_BUTTON, False)
    self._battle_auto_clicked = True
    time.sleep(2)
    return battle_auto_enabled(self)


def auto_fight(self, time_out=20, **kwargs):
    if 's' in kwargs:
        time_out = kwargs['s']
    reset_battle_auto_state(self)
    image.compare_image(self, 'fight_confirm', retry=3, threshold=0.7, cl=(1163, 658), rate=1)
    image.compare_image(self, 'fight_tasking', retry=1)
    image.compare_image(self, 'fight_tasking', retry=time_out, n=True)


def start_story(self):
    stages = self.tc.get('config', {}).get('stage', [])
    if isinstance(stages, str):
        stages = [stages]
    if not stages:
        self.logger.warning('未配置主线剧情关卡')
        return

    for stage_name in stages:
        part, chapter = parse_story_stage(stage_name)
        select_story_cn(self, part, chapter)
        skip_main_story_plot(self)
        start_admission(self, chapter)


def parse_story_stage(stage_name):
    parts = str(stage_name).strip().upper().split('-', 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError('主线剧情配置格式错误，应为 篇章-章节，例如 1-1、3-2、F-3')
    part, chapter = parts[0], parts[1]
    if part not in part_position:
        raise ValueError('暂不支持的主线剧情篇章: {0}'.format(part))
    if not chapter.isdigit():
        raise ValueError('主线剧情章节必须是数字: {0}'.format(stage_name))
    chapter_index = int(chapter)
    if chapter_index not in chapter_position:
        raise ValueError('暂不支持的主线剧情章节: {0}'.format(stage_name))
    return part, chapter


def select_part_and_chapter(self, part, chapter):
    self.click(*part_position[part], False)
    self.click(*chapter_position[chapter])


def select_story_cn(self, part='1', chapter='1'):
    to_main_story(self)
    select_part_and_chapter(self, part, int(chapter))
    to_choose_story(self)
