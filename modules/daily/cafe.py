import threading
import time
from collections import defaultdict
import cv2
import numpy as np
from common import stage, ocr, image, limit
from modules.baas import home

preset_position = {
    1: (808, 263),
    2: (808, 393),
    3: (808, 533),
    4: (812, 393),
    5: (812, 523),
}

fav_sort_position = {
    'cn': ((703, 149), (747, 264), (637, 393)),
    'intl': ((703, 149), (532, 319), (638, 392)),
    'jp': ((703, 149), (532, 319), (638, 392)),
}

selected_sort_position = {
    'cn': ((703, 149), (531, 320), (637, 393)),
    'intl': ((703, 149), (750, 320), (638, 392)),
    'jp': ((703, 149), (750, 320), (640, 395)),
}


def to_cafe(self):
    pos = {
        'home_student': (89, 653),
        'cafe_students-arrived': (922, 189),
        'cafe_inc-fav': (641, 537, 50),
        'cafe_need-storage': (886, 170),
    }
    home.to_menu(self, 'cafe_menu', pos, cl=(923, 186))


def start(self, seconds=False):
    if not seconds:
        home.go_home(self)
    to_cafe(self)
    get_cafe_money(self)
    invite_girl(self)
    init_window(self)
    drag_gift_click_girl(self)
    if not seconds:
        self.click(123, 100)
        time.sleep(2)
        self.click(255, 160)
        stage.wait_loading(self)
        start(self, True)
    home.go_home(self)


def match(self, img):
    res = []
    for i in range(1, 5):
        template = image.get_img_data(self, 'cafe_happy-face' + str(i))
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.6
        locations = np.where(result >= threshold)
        for pt in zip(*locations[::-1]):
            res.append([
                pt[0] + template.shape[1] / 2,
                pt[1] + template.shape[0] / 2 + 58,
            ])
    return res


def to_gift(self):
    pos = {
        'cafe_menu': (164, 640),
        'cafe_inc-fav': (641, 537, 0.6),
        'cafe_need-storage': (886, 170),
    }
    image.detect(self, 'cafe_give-gift', pos)


def shot(self):
    time.sleep(1)
    self.latest_img_array = self.get_screenshot_array()


def drag_gift_click_girl(self):
    for i in range(0, 3):
        to_gift(self)
        t1 = threading.Thread(target=shot, args=(self,))
        t1.start()
        self.d.click(131, 660)
        self.d.swipe(131, 660, 1280, 660, duration=0.5)
        t1.join()
        res = match(self, self.latest_img_array)
        result_list = list(set((int(x), min(int(y), 591)) for x, y in res))
        self.click(1237, 573)
        for x, y in result_list:
            self.double_click(x, y, wait=False)
        to_cafe(self)
        if i != 2:
            self.click(68, 636)
            time.sleep(1)
            self.click(1169, 90)
            time.sleep(1)


def empty_furniture_click_girl(self):
    preset = self.tc['config']['blank_preset']
    load_preset(self, preset)
    time.sleep(0.2)
    self.double_click(555, 622, False)
    i = 3
    while i > 0:
        click_girl_plus(self, i)
        if ocr.screenshot_check_text(self, '好感等级提升', (473, 593, 757, 644), 3):
            self.double_click(651, 285, False)
            time.sleep(0.5)
            i = 3
            continue
        i -= 1
    self.click(57, 624, False)
    recover_preset(self, preset)


def recover_preset(self, preset):
    open_preset_window(self, preset)
    self.click(*preset_position[preset], False)
    confirm_load_preset(self)


def load_preset(self, preset):
    open_preset_window(self, preset)
    save_preset(self, preset)
    self.click(455, 642, False, 1, 0.5)
    ocr.screenshot_check_text(self, '确认', (732, 482, 803, 518))
    self.click(769, 498, False)


def open_preset_window(self, preset):
    ocr.screenshot_check_text(self, '预设', (326, 656, 366, 677))
    self.click(360, 640)
    ocr.screenshot_check_text(self, '预设', (604, 127, 678, 157))
    stage.screen_swipe(self, preset, 3, False, f=(933, 586, 933, 50, 0.1))


def create_blank_preset(self, preset):
    save_preset(self, preset)
    self.click(455, 642, False, 1, 0.5)
    ocr.screenshot_check_text(self, '确认', (732, 482, 803, 518))
    self.click(769, 498, False)
    open_preset_window(self, preset)
    save_preset(self, preset)
    ocr.screenshot_check_text(self, '制造工坊', (732, 482, 803, 518), 0, 0, False)
    self.click(769, 498, False)


def save_preset(self, preset):
    area = preset_position[preset]
    self.click(area[0] - 250, area[1], False)
    confirm_load_preset(self)


def confirm_load_preset(self):
    ocr.screenshot_check_text(self, '确认', (732, 482, 803, 518))
    self.click(771, 500, False)
    ocr.screenshot_check_text(self, '预设', (604, 127, 678, 157))
    self.double_click(934, 146, False)


def init_window(self):
    self.d().pinch_in()
    self.swipe(392, 564, 983, 82)


def to_invitation_ticket(self):
    possible = {
        'cafe_menu': (888, 655),
        'cafe_inc-fav': (641, 537, 50),
    }
    return image.detect(self, 'cafe_invitation-ticket', possible)


def do_invite_girl(self):
    y = 140
    while True:
        if image.compare_image(self, 'cafe_menu', 0):
            return
        if image.compare_image(self, 'cafe_invitation-ticket', 0):
            if y >= 540:
                y = 140
            y += 80
            self.click(790, y, False)
        elif image.compare_image(self, 'cafe_inv-confirm', 0):
            self.click(706, 497, False)
        else:
            self.click(1268, 58, False)
        time.sleep(1)


def invite_girl(self):
    if not self.tc['invite']['enable']:
        self.logger.warning('当前设置为: 不邀请学生')
        return
    if not image.compare_image(self, 'cafe_invite-status', 0):
        self.logger.warning('当前不可邀请学生')
        return
    to_invitation_ticket(self)
    set_fav_sort(self)
    do_invite_girl(self)
    time.sleep(2)


def set_fav_sort(self):
    tp = self.tc['invite']['type']
    if tp == 'fav_desc' or tp == 'fav_asc':
        if not image.compare_image(self, 'cafe_inv-fav-level', 0):
            for p in fav_sort_position[self.game_server]:
                self.click(p, False)
                time.sleep(1)
        n = tp == 'fav_desc'
        image.compare_image(self, 'cafe_inv-fav-sort', self.click, (814, 151, False), 0.5, n)
        return
    if not image.compare_image(self, 'cafe_inv-sel-level', 0):
        for p in selected_sort_position[self.game_server]:
            self.click(p, False)
            time.sleep(1)
    image.compare_image(self, 'cafe_inv-fav-sort', self.click, (814, 151, False), 0.5, True)


def get_cafe_money(self):
    if not self.tc['ap']['enable']:
        self.logger.warning('当前设置为: 不领取体力')
        return
    pos = {
        'cafe_reward-text': (1152, 664),
        'cafe_students-arrived': (922, 189),
        'cafe_inc-fav': (641, 537, 50),
    }
    rst = image.detect(self, ('cafe_0.0', 'cafe_get-reward'), pos)
    if rst == 'cafe_0.0':
        self.logger.warning('没有可以体力领取')
        return
    self.click(641, 516)
    stage.close_prize_info(self, True)
    home.click_house_under(self)
    home.click_house_under(self)


def click_girl_plus(self, i):
    if i % 2 == 0:
        self.swipe(327, 512, 1027, 125)
    else:
        self.swipe(1008, 516, 300, 150)
    time.sleep(0.5)
    before = self.d.screenshot()
    time.sleep(1)
    after = self.d.screenshot()
    img1_data = np.array(before)
    img2_data = np.array(after)
    diff_pixels_coords = np.where(img1_data != img2_data)
    blocks = defaultdict(list)
    for p in zip(*diff_pixels_coords):
        x = int(p[1])
        y = int(p[0])
        block_coord = (y // 50, x // 50)
        blocks[block_coord].append((y, x))
    finial = []
    for block_coord, pixels in blocks.items():
        pixels.sort()
        mid_pixel = pixels[len(pixels) // 2]
        center_coord = (mid_pixel[0] * 1 + 0.5, mid_pixel[1] * 1 + 0.5)
        x = int(center_coord[1])
        y = int(center_coord[0])
        if y < 70:
            continue
        if y < 130 and x < 320:
            continue
        if y < 130 and x > 1170:
            continue
        if y > 570 and x < 100:
            continue
        if y > 570 and x > 770:
            continue
        finial.append(center_coord)
    np.random.shuffle(finial)
    for p in finial:
        self.click(int(p[1]), int(p[0]), False)
