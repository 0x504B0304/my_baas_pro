from common import ocr, color, image
from common import stage
from modules.attack import hard_task
from modules.baas import home
from modules.exp.normal_task import exp_normal_task
from modules.story import main_story

normal_position = {
    1: (1120, 240),
    2: (1120, 340),
    3: (1120, 440),
    4: (1120, 540),
    5: (1120, 616),
    6: (1120, 569),
}

normal_position_third = {
    1: {
        1: (1120, 240),
        2: (1120, 440),
        3: (1120, 615),
        4: (1120, 480),
        5: (1120, 570),
    },
    2: {
        1: (1120, 240),
        2: (1120, 440),
        3: (1120, 540),
        4: (1120, 480),
        5: (1120, 570),
    },
    3: {
        1: (1120, 336),
        2: (1120, 440),
        3: (1120, 540),
        4: (1120, 480),
        5: (1120, 570),
    },
}


def to_choose_region(self):
    pos = {
        'home_student': (1200, 573),
        'normal_task_menu': (816, 263),
        'normal_task_task-info-window': (1130, 110),
        'normal_task_a-quest': (1130, 140),
    }
    home.to_menu(self, 'normal_task_choose-region', pos)


def open_task_info_window(self, task_x):
    pos = {
        'normal_task_choose-region': task_x,
    }
    image.detect(self, 'normal_task_task-info-window', pos)


def start(self):
    home.go_home(self)
    to_choose_region(self)
    change_task(self)
    start_scan(self)
    home.go_home(self)


def change_task(self):
    if 'hard_task' in self.tc['task']:
        color.wait_rgb_similar(self, (1000, 150), (198, 66, 66), (1062, 154), cl=True)
        return
    color.wait_rgb_similar(self, (700, 150), (44, 65, 86), (803, 156), cl=True)


def start_scan(self):
    sl = ['scan', 'scan2']
    for l in sl:
        if not self.tc[l]['enable']:
            continue
        for tk in stage.stage_convert(self.tc[l]['stage']):
            choose_region(self, tk['region'])

            if str(tk['stage']) == 'tr':
                start_tr_scan(self, tk)
                continue

            if self.tc['task'] == 'hard_task':
                open_task_info_window(self, hard_task.hard_position[tk['stage']])
            else:
                stage.screen_swipe(self, tk['stage'], 7)
                open_task_info_window(self, normal_position[tk['stage']])

            rst = stage.confirm_scan(self, tk['stage'], tk['count'], 99, 'special', t=True)

            if rst == 'return':
                break


def start_tr_scan(self, tk):
    for i in range(tk['count']):
        stage.screen_swipe(self, 0, 0)
        tr_win = 'fight_force-edit-tr'
        image.compare_image(self, 'normal_task_tr-quest', (1117, 340), 1, cl=True, rate=True)
        image.compare_image(self, tr_win, (645, 511), 1, cl=True, rate=True)
        exp_normal_task.start_choose_side_team(self)
        image.compare_image(self, tr_win)
        image.compare_image(self, tr_win, 0.6, (1171, 670), 1, True, threshold=True, cl=True, rate=True, n=True)
        self.logger.info('开始教程关卡...')
        main_story.auto_fight_put_skill(self)
        exp_normal_task.to_task_menu(self)


def choose_region(self, region):
    try:
        cu_region = int(ocr.screenshot_get_text(self, (122, 178, 163, 208), self.ocrNum))
        self.logger.warning('当前区域{0}，需要前往区域{1}...'.format(cu_region, region))
    except Exception:
        cu_region = 0

    if cu_region == region:
        return

    if cu_region > region:
        self.click(40, 360, False, cu_region - region, 0.1)
    else:
        self.click(1245, 360, False, region - cu_region, 0.1)

    return choose_region(self, region)
