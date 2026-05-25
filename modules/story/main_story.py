import time
import time
import numpy as np
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
    home.to_menu(self, ends, pos, 1)


def to_choose_story(self):
    pos = {
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
    image.detect(self, 'main_story_choose-plot', pos)


def start(self):
    home.go_home(self)
    start_story(self)
    home.go_home(self)


def check_finish(self):
    ends = ('main_story_clearance', 'main_story_current-clearance')
    return image.detect(self, ends, 3)


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
        image.compare_image(self, 'main_story_lianhe-edit-force', 0.6, (640, 580), 1)
        image.compare_image(self, 'main_story_lianhe-edit-force', 0.6, (1171, 670), 1, True)
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

    cl = (1170, 250)
    if image.compare_image(self, 'main_story_first-lock', 5, 0.6, 0.5):
        cl = (1110, 355)

    if not image.compare_image(self, 'main_story_plot-info', cl, 1, 5):
        home.click_house_under(self)
        return start_admission(self, chapter)

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
            image.compare_image(self, 'fight_force-attack', self.click, (1163, 658), 1, True)
            if self.game_server == 'cn':
                auto_fight(self)
                time.sleep(30)
            else:
                auto_fight(self)
                self.click(1235, 97)
                time.sleep(1)
                self.click(772, 500)
        else:
            exp_normal_task.wait_over(self)
            area = image.get_box(self, 'main_story_stage')
            stage_index = int(ocr.screenshot_get_text(self, area, self.ocrNum))
            gk = 'F-{0}-{1}'.format(chapter, stage_index)
            self.stage_data = stage_data

            if gk in stage_data:
                self.logger.critical('当前关卡（{0}）卡暂不支持开图，请联系奇犽揍敌客x'.format(gk))
                self.exit(0)

            exp_normal_task.to_tart_task_page(self)
            self.logger.info('开始: {0}'.format(gk))
            exp_normal_task.start_fight(self, 0, gk)

    check_momo_talk(self)
    return start_admission(self, chapter)


def check_momo_talk(self):
    if image.compare_image(self, 'momo_talk_confirm-skip', 0, 0.5):
        self.click(770, 520, False)

    if image.compare_image(self, 'momo_talk_begin-relationship', 0, 0.5):
        self.click(920, 568, False)
        time.sleep(5)
        image.compare_image(self, 'momo_talk_confirm-skip', 0.5, self.click, (1212, 114, False))

    if image.compare_image(self, 'main_story_get-prize', 0, 0.5):
        self.click(644, 634, False)
        time.sleep(1)
        self.click(770, 520, False)


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
    image.compare_image(self, 'main_story_skip-story2', 0.5, self.click, (757, 451))


def skip_main_story_plot(self):
    image.compare_image(self, 'fight_fail', 5, self.click, (647, 655), 1, True)
    image.compare_image(self, 'main_story_continue', 5, self.click, (505, 520), 1)
    image.compare_image(self, 'main_story_continue', 5, self.click, (505, 520), 1, True)
    image.compare_image(self, 'main_story_skip-story', 5, self.click, (770, 520), 1)
    image.compare_image(self, 'main_story_skip-story', 5, self.click, (770, 520), 1, True)


def change_acc_auto(self):
    image.compare_image(self, 'fight_confirm2', 0.5, self.click, (1163, 658), 1)
    image.compare_image(self, 'fight_confirm2', 0.5, self.click, (1163, 658), 1, True)
    image.compare_image(self, 'main_story_skip-story', 5, self.click, (770, 520), 1)
    image.compare_image(self, 'main_story_skip-story', 5, self.click, (770, 520), 1, True)


def auto_fight_put_skill(self):
    image.compare_image(self, 'fight_auto-over', 0.6, self.click, (1082, 599), 2)
    self.click(1123, 545, False)
    image.compare_image(self, 'fight_auto-over', 0.6, self.click, (1082, 599), 2)

    for i in range(100):
        if image.compare_image(self, 'fight_tasking', 0, 0.6):
            return
        time.sleep(1)


def auto_fight(self, time_out=20):
    image.compare_image(self, 'fight_confirm', 0.7, self.click, (1163, 658), 1)
    image.compare_image(self, 'fight_tasking', True, wait=1)
    image.compare_image(self, 'fight_tasking', True, wait=time_out)


def start_story(self):
    select_story_cn(self)
    skip_main_story_plot(self)
    start_admission(self, '1')


def select_part_and_chapter(self, part, chapter):
    self.click(part_position[part])
    self.click(chapter_position[chapter])


def select_story_cn(self):
    to_main_story(self)
    to_choose_story(self)
    select_part_and_chapter(self, '1', 1)
    to_choose_story(self)
    select_part_and_chapter(self, '1', 2)
    to_choose_story(self)
