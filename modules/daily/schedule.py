import time
import cv2
import numpy as np

from common import image, ocr, stage
from modules.baas import home


COURSE_INFO_TITLE_AREA = (400, 60, 880, 190)
COURSE_INFO_CLOSE_POS = (964, 114)

schedule_position = {
    1: (908, 182),
    2: (908, 285),
    3: (908, 397),
    4: (908, 502),
    5: (908, 606),
    6: (908, 155),
    7: (908, 240),
    8: (908, 340),
    9: (908, 450),
    10: (908, 555),
    11: (908, 645),
}

curse_position = {
    'cn': {
        1: (640, 516),
        2: (300, 516),
        3: (990, 360),
        4: (640, 360),
        5: (300, 360),
        6: (990, 210),
        7: (640, 210),
        8: (300, 210),
    },
    'intl': {
        1: (640, 516),
        2: (300, 516),
        3: (990, 360),
        4: (640, 360),
        5: (300, 360),
        6: (990, 210),
        7: (640, 210),
        8: (300, 210),
    },
    'jp': {
        1: (710, 520),
        2: (400, 520),
        3: (990, 360),
        4: (1030, 360),
        5: (700, 360),
        6: (1030, 210),
        7: (700, 210),
        8: (330, 210),
    },
}


curse_avatar_box = {
    'cn': {
        1: (500, 562, 557, 614),
        2: (155, 562, 212, 614),
        3: (845, 410, 902, 462),
        4: (500, 410, 557, 462),
        5: (155, 410, 212, 462),
        6: (845, 258, 902, 310),
        7: (500, 258, 557, 310),
        8: (155, 258, 212, 310),
    },
}


def to_schedule(self):
    close_course_info(self)
    pos = {
        'home_student': (212, 656),
        'schedule_choose-course': (59, 36),
    }
    home.to_menu(self, 'schedule_menu', pos)


def start(self):
    home.go_home(self)
    to_schedule(self)
    if (image.compare_image(self, 'schedule_surplus', 0, 0.9)
            or image.compare_image(self, 'schedule_surplus2', 0, 0.9)):
        self.logger.warning('当前持有日程券为0')
        home.go_home(self)
        return
    choose_course(self)
    home.go_home(self)


def choose_course(self):
    for tk in self.tc['config']:
        to_college(self, tk['schedule'])
        if learn_course(self, tk['schedule'], tk['count']):
            return
        to_schedule(self)


def to_college(self, college):
    if self.game_server == 'jp':
        stage.screen_swipe(self, college, 5, f=(911, 650, 911, 60, 0.5))
    else:
        stage.screen_swipe(self, college, 5)
    to_course_info(self, college)


def to_course_info(self, college):
    pos = {
        'schedule_menu': schedule_position[college],
    }
    image.detect(self, 'schedule_course-info', pos)


def open_all_course(self):
    pos = {
        'schedule_course-info': (1174, 666),
    }
    image.detect(self, 'schedule_all-course', pos)


def course_info_popup_visible(self):
    if self.game_server != 'cn' or getattr(self, 'ocr', None) is None:
        return False
    return ocr.screenshot_check_text(
        self,
        '日程信息',
        COURSE_INFO_TITLE_AREA,
        0,
        0,
        False,
    )


def close_course_info(self):
    if not course_info_popup_visible(self):
        return False
    self.click(*COURSE_INFO_CLOSE_POS, False)
    time.sleep(0.5)
    return True


def close_all_course(self):
    if image.compare_image(self, 'schedule_all-course', 0):
        self.click(1138, 100, False)
        time.sleep(0.5)


def all_course_ticket_empty(self):
    ss = self.get_screenshot_array()
    crop = ss[135:162, 665:690]
    crop = cv2.resize(crop, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    out = self.ocrNum.ocr(crop)
    text = ''.join(item.get('text', '') for item in out)
    digits = ''.join(ch for ch in text if ch.isdigit())
    self.logger.info('schedule all-course ticket left text:%s digits:%s', text, digits)
    return digits.startswith('0')


def course_exists(self, course, point):
    x, y = point
    ss = self.get_screenshot_array()
    h, w = ss.shape[:2]
    x1, y1 = max(0, x - 150), max(0, y - 32)
    x2, y2 = min(w, x + 150), min(h, y + 35)
    roi = ss[y1:y2, x1:x2]
    if roi.size == 0:
        return False
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    white_ratio = float(np.mean(gray > 245))
    mean = float(np.mean(gray))
    self.logger.info('schedule course:%s card_white_ratio:%.2f card_mean:%.2f', course, white_ratio, mean)
    return white_ratio > 0.45 and mean > 225


def course_finished(self, course):
    box = curse_avatar_box.get(self.game_server, {}).get(course)
    if box is None:
        return False
    ss = self.get_screenshot_array()
    x1, y1, x2, y2 = box
    roi = ss[y1:y2, x1:x2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    brightness = np.percentile(gray, 75)
    self.logger.info('schedule course:%s avatar_brightness_p75:%.2f', course, brightness)
    return brightness < 165


def start_course_jp(self, course_x):
    pos = {
        'schedule_all-course': course_x,
        'schedule_course-info': (1174, 666),
    }
    rst = image.detect(self, 'schedule_course-pop', pos, retry=5)
    if rst is not None:
        return True
    self.click(640, 546, False)
    time.sleep(2)
    return False


def start_course(self, course_x):
    pos = {
        'schedule_all-course': course_x,
        'schedule_course-info': (1174, 666),
    }
    image.detect(self, 'schedule_course-pop', pos)
    self.click(640, 546, False)
    time.sleep(2)


def learn_course(self, schedule, count):
    self.logger.warning('开始检查课程...')
    learned_count = 0
    completed_courses = set()
    while learned_count < count:
        open_all_course(self)
        if all_course_ticket_empty(self):
            self.logger.error('没有门票了')
            close_all_course(self)
            return True
        progressed = False
        for c, p in curse_position[self.game_server].items():
            if learned_count >= count:
                break
            if c in completed_courses:
                continue
            if not course_exists(self, c, p):
                self.logger.error('当前课程位置为空')
                completed_courses.add(c)
                continue
            if course_finished(self, c):
                self.logger.error('当前课程已完成')
                completed_courses.add(c)
                continue
            self.logger.warning(f'开始学习课程{c}...')
            if self.game_server != 'cn':
                finish = start_course_jp(self, p)
                if finish:
                    self.logger.error('当前课程已完成')
                    completed_courses.add(c)
                    continue
            else:
                start_course(self, p)
            if (image.compare_image(self, 'schedule_limited', 0, 0.9)
                    or image.compare_image(self, 'schedule_limited2', 0)):
                self.logger.error('没有门票了')
                return True
            image.compare_image(self, 'schedule_course-report', cl=(774, 141))
            pos = {
                'schedule_course-report': (641, 550),
                'schedule_all-course': (1138, 100),
            }
            image.detect(self, 'schedule_course-info', pos, cl=(774, 141))
            learned_count += 1
            completed_courses.add(c)
            progressed = True
            break
        if not progressed:
            close_all_course(self)
            self.logger.error('当前区域没有可执行日程')
            return False
