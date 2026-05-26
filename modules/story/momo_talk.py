import time
from common import stage, image, color, limit
from modules.baas import home


def to_momo_talk(self):
    pos = {'home_student': (171, 148), 'momo_talk_student': (177, 271)}
    home.to_menu(self, 'momo_talk_unread', pos)


def start(self):
    home.go_home(self)
    if not color.check_rgb(self, (183, 125), (232, 68, 0)):
        self.logger.warning('没有可以互动的学生')
        return
    to_momo_talk(self)
    check_sort(self)
    time.sleep(0.5)
    if not color.check_rgb(self, (657, 259), (251, 71, 25)):
        home.go_home(self)
        self.logger.info('没有可以互动的学生')
        return
    self.click(471, 251)
    start_chat(self)
    start(self)


def check_sort(self):
    """
    检查排序
    :param self:
    """
    set_unread_sort(self)
    image.compare_image(self, 'momo_talk_sort-direction', cl=(625, 180), rate=0.5)


def set_unread_sort(self):
    """
    设置未读排序
    :param self:
    """
    sd = {
        'cn': [(509, 175, False), (560, 294, False), (445, 470, False)],
        'intl': [(509, 175, False), (560, 294, False), (445, 470, False)],
        'jp': [(509, 175, False), (554, 296, False), (450, 480, False)],
    }
    if not image.compare_image(self, 'momo_talk_sort-field', 0):
        position = sd[self.game_server]
        for p in position:
            self.click(p)
            time.sleep(1)


def start_chat(self):
    """
    开始聊天
    :param self:
    """
    self.swipe(700, 600, 700, 100, 0.1)
    time.sleep(1)
    self.mm_i = 0
    while self.mm_i < 5:
        while True:
            self.latest_img_array = self.get_screenshot_array()
            rst = image.find_img(self, self.latest_img_array, 'momo_talk_reply', y_add=62)
            if len(rst) > 0:
                self.logger.warning('开始回消息... ')
                self.mm_i = 0
                for r in rst:
                    self.click(*r, False)
                break

            rst = image.find_img(self, self.latest_img_array, 'momo_talk_likable', y_add=62)
            if len(rst) > 0:
                self.logger.warning('开始好感故事...')
                self.mm_i = 0
                for r in rst:
                    self.click(*r, False)
                begin_relationship(self)
                break

            check_message(self)
            time.sleep(1)
            if not (self.mm_i < 5):
                return
        if self.mm_i >= 5:
            return


def check_message(self):
    """
    检查文字是否发生变动
    :param self:
    :return:
    """
    cu_ss = image.screenshot_cut(self, (769, 181, 807, 620))
    if hasattr(self, 'mm_prev') and image.compare_image_data(self, cu_ss, self.mm_prev):
        pass
    else:
        self.mm_i += 1
        self.logger.warning('当前聊天内容未发生变化...{0}'.format(self.mm_i))
    self.mm_prev = cu_ss


def begin_relationship(self):
    """
    开始好感故事
    :param self:
    """
    skip_plot(self)
    stage.close_prize_info(self, True)


def skip_plot(self):
    pos = {
        'main_story_join-chapter': (640, 515),
        'fight_pass-confirm': (1170, 666),
        'momo_talk_begin-relationship': (920, 568),
        'momo_talk_menu': (1205, 42),
        'momo_talk_skip': (1212, 116),
    }
    end = image.detect(self, ('momo_talk_confirm-skip', 'fight_fail'), pos)
    if end == 'fight_fail':
        return end
    self.click(770, 516, False)
