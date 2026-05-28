import time

from common import ocr, image, color

from modules.baas import home

position = {'add_special': (1015, 330), 'max_special': (1085, 330), 'add_normal': (1015, 300), 'max_normal': (1085, 300)}


def confirm_scan(self, stage, ct, max_count, cl=None, t='normal'):
    self.logger.warning('开始扫荡第 {0} 关'.format(stage))
    ends = ('wanted_task-info-window', 'normal_task_task-info-window')

    image.detect(self, ends, cl=cl, rate=1)

    is_max = type(ct) == str and ct == 'max'

    if is_max or int(ct) >= max_count:
        self.click(*position['max_' + t], False)
    else:
        self.click(*position['add_' + t], False, int(ct) - 1, 0.6)

    self.click(938, 403, False)

    ends = ('wanted_buy-ticket', 'normal_task_buy-hard-count', 'normal_task_buy-ap-window', 'normal_task_task-info-notice', 'exchange_meeting_no-ticket', 'god_cross_no-score')

    end = image.detect(self, ends)

    if end == 'normal_task_buy-ap-window' and self.tc['task'] == 'exchange_meeting':
        return 'delay'

    if end == 'wanted_buy-ticket':
        self.click(56, 38, 0, 3)
        return 'return'

    if end == 'normal_task_buy-hard-count' or end == 'god_cross_no-score':
        home.click_house_under(self)
        return None

    if end == 'normal_task_buy-ap-window' or end == 'exchange_meeting_no-ticket':
        return 'return'

    if end != 'normal_task_task-info-notice':
        return None

    start_scan(self)
    return 'nothing'


def start_scan(self):
    pos = {'normal_task_task-info-notice': (770, 500), 'normal_task_scan-skip': (647, 506)}

    image.detect(self, 'normal_task_scan-confirm', pos)

    self.click(643, 586)

    home.click_house_under(self)


def get_ap(self):
    area = image.get_box(self, 'cm_ap')
    return int(ocr.screenshot_get_text(self, area, self.ocrNum))


def get_activity_hb(self):
    area = image.get_box(self, 'cm_activity-hb')
    return int(ocr.screenshot_get_text(self, area, self.ocrNum))


def choose_role(self, index):
    index = str(index)

    position = {'1': (170, 160), '2': (320, 160), '3': (480, 160), '4': (650, 160)}

    pos = {'normal_task_force-edit': (1200, 485)}

    if not image.detect(self, 'fight_yushe', pos, 10, retry=10):
        return None

    color.wait_rgb_similar(self, (position[index][0] - 100, position[index][1]), (46, 74, 114), cl=position[index])

    pos = {'fight_yushe': (1150, 325), 'fight_yushe-confirm': (768, 576)}

    image.detect(self, 'normal_task_force-edit', pos)


def close_prize_info(self, ap_check=False, mail_check=False, retry=99):
    if retry <= 0:
        return None

    text_box = {'intl': ('CON', '因超出持有上限'), 'cn': ('点击继续', '因超出持有上限')}

    text_box['jp'] = text_box['intl']
    tb = text_box[self.game_server]

    if image.compare_image(self, 'cm_get-prize', 3, 0.6):
        self.click(640, 635)
        time.sleep(0.5)
        return None

    if self.game_server != 'cn':
        if image.compare_image(self, 'arena_ap-limited', 0) or image.compare_image(self, 'arena_ap-limited2', 0):
            home.click_house_under(self)
            self.finish_seconds = 180
            return None

    ar = (577, 614, 704, 648)
    if self.game_server == 'intl':
        ar = (620, 620, 680, 650)

    if ocr.screenshot_check_text(self, tb[0], ar, 1):
        self.click(640, 635)
        time.sleep(0.5)
        return None

    if ap_check and self.game_server == 'cn' and ocr.screenshot_check_text(self, tb[1], (532, 282, 724, 314), 1):
        self.click(650, 501)
        return None

    if mail_check and image.compare_image(self, 'mailbox_limited', 0):
        self.click(642, 527)
        return None

    return close_prize_info(self, ap_check, mail_check, retry - 1)


def wait_loading(self):
    t_start = time.time()
    color_list = (((930, 666), (243, 243, 243)), ((961, 666), (243, 243, 243)), ((971, 664), (243, 243, 243)), ((1043, 668), (83, 113, 162)), ((1093, 666), (61, 101, 157)), ((1111, 666), (61, 101, 157)))
    if self.game_server == 'cn':
        color_list = (((967, 672), (243, 243, 243)), ((998, 652), (243, 243, 243)), ((1028, 670), (4, 71, 133)), ((1043, 662), (4, 71, 133)), ((1062, 671), (243, 243, 243)), ((1102, 665), (243, 243, 243)))
    s = 0.1
    while True:
        ss = self.get_screenshot_array()
        matches = sum(1 for c in color_list if color.check_rgb(self, c[0], c[1], 50, ss, True))
        if matches < 5:
            return None
        t_load = time.time() - t_start
        self.logger.info(f'Now Loading {t_load:.0f} seconds...')
        time.sleep(s)
        if s < 1:
            s += 0.1


def convert_string(s):
    s = s.lower().replace(' ', '').replace('—', '-').replace('_', '-')
    parts = s.split('-')
    region = int(parts[0])
    stage = parts[1]
    if stage != 'tr':
        stage = int(parts[1])
    count = parts[2] if parts[2] == 'max' else int(parts[2])
    return {'region': region, 'stage': stage, 'count': count}


def stage_convert(stage_list):
    return [convert_string(s) for s in stage_list]


def screen_swipe(self, stage=1, threshold1=0, threshold2=999, reset=True, f=(911, 650, 911, 40, 0.55)):
    if reset:
        self.swipe(911, 199, 911, 600, 0.5)
        self.swipe(911, 199, 911, 600, 0.5)
    if stage > threshold1:
        time.sleep(0.5)
        self.swipe(*f)
    if stage > threshold2:
        time.sleep(0.5)
        self.swipe(*f)
    time.sleep(0.5)
