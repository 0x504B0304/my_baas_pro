import time
from common import stage, image
from modules.baas import home

entrust_position = {
    'jdfy': (950, 200),
    'xyhs': (950, 310),
}

wanted_lv_position = {
    1: (1116, 185),
    2: (1116, 285),
    3: (1116, 385),
    4: (1116, 485),
    5: (1116, 585),
    6: (1116, 666),
    7: (1116, 430),
    8: (1116, 530),
    9: (1116, 630),
}

wanted_lv_position_jp = {
    1: (1116, 185),
    2: (1116, 285),
    3: (1116, 385),
    4: (1116, 485),
    5: (1116, 585),
    6: (1116, 666),
    7: (1116, 330),
    8: (1116, 430),
    9: (1116, 530),
    10: (1116, 630),
}

se_lv_position = {
    'cn': {
        1: (1116, 185),
        2: (1116, 285),
        3: (1116, 385),
        4: (1116, 485),
        5: (1116, 585),
        6: (1116, 666),
        7: (1116, 365),
        8: (1116, 150),
        9: (1116, 230),
        10: (1116, 330),
        11: (1116, 430),
        12: (1116, 530),
        13: (1116, 630),
    },
    'jp': {
        1: (1116, 185),
        2: (1116, 285),
        3: (1116, 385),
        4: (1116, 485),
        5: (1116, 585),
        6: (1116, 666),
        7: (1116, 365),
        8: (1116, 150),
        9: (1116, 230),
        10: (1116, 330),
        11: (1116, 430),
        12: (1116, 530),
        13: (1116, 630),
    },
    'intl': {
        1: (1116, 185),
        2: (1116, 285),
        3: (1116, 385),
        4: (1116, 485),
        5: (1116, 585),
        6: (1116, 666),
        7: (1116, 365),
        8: (1116, 150),
        9: (1116, 230),
        10: (1116, 330),
        11: (1116, 430),
        12: (1116, 530),
        13: (1116, 630),
    },
}

fns = {
    'special_entrust': ['jdfy', 'xyhs'],
    'wanted': ['gjgl', 'smtl', 'jt'],
}


def to_menu(self):
    if self.tc['task'] == 'special_entrust':
        to_special(self)
        return
    to_wanted(self)


def to_wanted(self):
    want_pos = {
        'jp': (750, 380),
        'cn': (745, 450),
        'intl': (745, 450),
    }
    pos = {
        'home_student': (1200, 573),
        'normal_task_menu': want_pos[self.game_server],
        'normal_task_task-info-window': (60, 40),
        'wanted_stage-list': (60, 40),
        'wanted_help': (1013, 130),
    }
    home.to_menu(self, 'wanted_menu', pos, rate=0.5)


def to_special(self):
    spe_pos = {
        'jp': (723, 450),
        'cn': (730, 537),
        'intl': (730, 537),
    }
    pos = {
        'home_student': (1200, 573),
        'normal_task_menu': spe_pos[self.game_server],
        'normal_task_task-info-window': (60, 40),
        'wanted_stage-list': (60, 40),
    }
    home.to_menu(self, 'special_entrust_menu', pos, rate=0.5)


def start(self):
    home.go_home(self)
    choose_entrust(self, entrust_position, 99)
    home.go_home(self)


def choose_entrust(self, position, max_count):
    for fn in fns[self.tc['task']]:
        tk = self.tc[fn]
        if not tk['enable']:
            continue

        to_menu(self)

        self.click(*position[fn])

        image.compare_image(self, 'wanted_stage-list')

        if tk['stage'] == 7:
            stage.screen_swipe(self, tk['stage'], 6, 11, f=(911, 650, 911, 200, 0.55))
            if self.tc['task'] == 'wanted':
                time.sleep(0.1)
                stage.screen_swipe(self, tk['stage'], 6, 11, False, f=(911, 650, 911, 200, 0.55))
        else:
            stage.screen_swipe(self, tk['stage'], 6, 99, f=(911, 650, 911, 40, 0.1))

        self.click(*get_lv_position(self, tk['stage']))

        rst = stage.confirm_scan(self, tk['stage'], tk['count'], max_count)

        if rst == 'return':
            return

        self.click(57, 36)
        time.sleep(1)


def get_lv_position(self, lv):
    if self.tc['task'] == 'special_entrust':
        return se_lv_position[self.game_server][lv]
    if self.game_server != 'cn':
        return wanted_lv_position_jp[lv]
    return wanted_lv_position[lv]
