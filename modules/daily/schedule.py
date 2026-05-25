import time
from common import color, image, stage
from modules.baas import home

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


def to_schedule(self):
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
        pos = {
            'schedule_course-info': (1137, 118),
            'schedule_choose-course': (59, 36),
        }
        home.to_menu(self, 'schedule_menu', pos)


def to_college(self, college):
    if self.game_server == 'jp':
        stage.screen_swipe(self, college, 5, f=(911, 650, 911, 60, 0.5))
    else:
        stage.screen_swipe(self, college, 5)
    to_course_info(self, college)


def to_course_info(self, college):
    pos = {
        'schedule_menu': schedule_position[college],
        'schedule_choose-course': (1174, 666),
    }
    image.detect(self, 'schedule_course-info', pos)


def start_course_jp(self, course_x):
    pos = {
        'schedule_choose-course': (1174, 666),
        'schedule_course-info': course_x,
    }
    rst = image.detect(self, 'schedule_course-pop', pos, retry=5)
    if rst is not None:
        return True
    self.click(640, 546, False)
    time.sleep(2)
    return False


def start_course(self, course_x):
    pos = {
        'schedule_choose-course': (1174, 666),
        'schedule_course-info': course_x,
    }
    image.detect(self, 'schedule_course-pop', pos)
    self.click(640, 546, False)
    time.sleep(2)


def learn_course(self, schedule, count):
    self.logger.warning('开始检查课程...')
    i = 0
    completed_courses = set()
    while i < count:
        for c, p in curse_position[self.game_server].items():
            if i >= count:
                break
            if c in completed_courses:
                i += 1
                continue
            if color.check_rgb(self, p, (239, 239, 237), 20):
                self.logger.error('当前课程已完成')
                completed_courses.add(c)
                i += 1
                continue
            if self.game_server == 'cn':
                if not color.check_rgb(self, p, (255, 255, 255), 20):
                    self.logger.error(f'课程{c} 状态不可用')
                    continue
            self.logger.warning(f'开始学习课程{c}...')
            if self.game_server != 'cn':
                finish = start_course_jp(self, p)
                if finish:
                    self.logger.error('当前课程已完成')
                    completed_courses.add(c)
                    i += 1
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
            }
            image.detect(self, 'schedule_course-info', pos, cl=(774, 141))
            i = 0
            completed_courses.add(c)
