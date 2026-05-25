import time
from fuzzywuzzy import fuzz
from common import ocr, stage, color, image, limit
from modules.baas import home

make_position = {
    1: (975, 279),
    2: (975, 410),
    3: (975, 551),
}

priority_position = {
    1: (174, 552),
    2: (303, 527),
    3: (414, 473),
    4: (505, 388),
    5: (569, 275),
}


def to_make(self):
    pos = {'home_student': (701, 645)}
    home.to_menu(self, 'make_menu', pos)


def to_immediately(self):
    pos = {
        'make_choose-node': (1120, 650),
        'make_start-make2': (1120, 650),
        'make_confirm-start': (769, 500),
    }
    image.detect(self, 'make_immediately', pos, rate=1)


def to_receive(self):
    pos = {
        'make_immediately': (1128, 278),
        'make_confirm-acc': (771, 478),
    }
    image.detect(self, 'make_receive', pos)


def to_workshop(self):
    pos = {'make_first-stage-start': (1120, 650)}
    image.detect(self, 'make_workshop', pos)


def start(self):
    if self.game_server != 'cn':
        self.logger.critical('外服此功能待开发...')
        return
    home.go_home(self)
    to_make(self)
    if empty_make(self):
        if self.tc['config']['quick']:
            start_quick_make(self)
        else:
            start_make(self)
    home.go_home(self)


def empty_make(self):
    ends = ('cm_get-prize', 'make_receive', 'make_immediately', 'make_start-make')
    end = image.detect(self, ends, None)
    if end == 'make_receive':
        receive_prize(self)
    elif end == 'make_immediately':
        return make_immediately(self)
    return True


def receive_prize(self):
    image.compare_image(self, 'make_receive', cl=(1122, 275), rate=1, n=True)
    stage.close_prize_info(self)


def make_immediately(self):
    if not self.tc['config']['use_acc_ticket']:
        self.logger.error('当前配置为：不使用加速券...')
        return False
    to_receive(self)
    receive_prize(self)
    return True


def start_quick_make(self):
    for i in range(self.tc['config']['count']):
        pos = {
            'make_menu': (888, 616),
            'make_quick-make': (1111, 580),
        }
        image.detect(self, 'make_con-quick-make', pos)
        time.sleep(0.1)
        self.click(760, 500)
        time.sleep(0.1)
        if not make_immediately(self):
            return


def start_make(self):
    for i in range(self.tc['config']['count']):
        image.detect(self, 'make_list', cl=(975, 264))
        if not choose_tone(self):
            return
        to_workshop(self)
        choose_item(self)
        to_immediately(self)
        if not make_immediately(self):
            return


def choose_item(self):
    time.sleep(3)
    self.click(445, 552, False)
    check_index = get_high_priority(self)
    self.click(priority_position[check_index + 1])
    return check_index


def get_high_priority(self):
    items = []
    for i, position in priority_position.items():
        self.click(position)
        item = ocr.screenshot_get_text(self, (720, 204, 1134, 269))
        items.append(item)
    check_item = None
    check_index = 0
    for i, item in enumerate(items):
        for priority in self.tc['config']['priority']:
            ratio = fuzz.ratio(item, priority)
            if ratio < 80:
                continue
            if (check_item is None
                    or self.tc['config']['priority'].index(priority)
                    < self.tc['config']['priority'].index(check_item)):
                check_item = priority
                check_index = i
    return check_index


def choose_tone(self):
    time.sleep(1)
    self.click(769, 200, False)
    time.sleep(1)
    if color.check_rgb(self, (995, 631)):
        return True
    self.click(908, 199, False, 10)
    time.sleep(1)
    return color.check_rgb(self, (995, 631))
