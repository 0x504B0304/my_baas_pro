import time
import numpy as np
from common import stage, color
from modules.baas import home
from common import stage, ocr, image, limit
import cv2

x = {
    'menu': (107, 9, 162, 36),
    'receive': (1094, 657, 1206, 681),
    'reward': (369, 134, 605, 182),
}

check_btn = [
    {'x': (1075, 680), 'cl': (1140, 641)},
    {'x': (945, 680), 'cl': (968, 666)},
]


def to_work_task(self):
    pos = {'home_student': (62, 236)}
    home.to_menu(self, 'work_task_menu', pos)


def get_work_prize(self):
    to_work_task(self)
    for btn in check_btn:
        while True:
            if color.check_rgb(self, btn['x'], (250, 236, 74)):
                self.click(*btn['cl'], False)
                stage.close_prize_info(self, True)
                self.click(1236, 79)
                break
            else:
                self.logger.warning('没有奖励可以领取')
                break
    home.go_home(self)


def get_shop_free_prize(self):
    if self.game_server != 'jp':
        return
    pos = {
        'home_student': (163, 233),
        'work_task_menu3-close': (907, 180),
    }
    ends = {('work_task_menu3-open', 0.95)}
    home.to_menu(self, ends, pos)
    img = self.get_screenshot_array()
    daily_free = image.get_img_data(self, 'work_task_daily-prize')
    result = cv2.matchTemplate(img, daily_free, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7
    locations = np.where(result >= threshold)
    for pt in zip(*locations[::-1]):
        if image.compare_image(self, 'work_task_daily-prize-ok', retry=3,
                               cl=(int(pt[0]) + 45, 489), threshold=0.5):
            self.click(760, 577)
            stage.close_prize_info(self, True)
            break
    home.go_home(self)


def get_right_down_prize(self, have_prize):
    while True:
        if color.check_rgb(self, (1270, 620), (250, 236, 74)):
            self.click(1270, 620, False)
            if have_prize:
                stage.close_prize_info(self, True)
            self.click(1236, 79)
        else:
            self.logger.warning('没有奖励可以领取')
            return


def get_big_month_prize(self):
    if self.game_server != 'jp':
        return
    pos = {
        'home_student': (400, 550),
        'work_task_big-month-menu': (383, 646),
    }
    home.to_menu(self, 'work_task_big-month-task', pos)
    get_right_down_prize(self, False)
    pos = {'work_task_big-month-task': (35, 40)}
    home.to_menu(self, 'work_task_big-month-menu', pos)
    get_right_down_prize(self, True)
    possible = {'work_task_big-month-menu': (1245, 40)}
    ends = ('home_setting', 'home_student')
    image.detect(self, ends, possible, rate=0.5)


def start(self):
    home.go_home(self)
    get_work_prize(self)
    get_shop_free_prize(self)
