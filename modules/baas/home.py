import time

from common import image
from modules.baas import restart


def back_home(self):
    self.press('home')


def only_start(self):
    app = self.d.app_current()
    if app['package'] != self.bc['baas']['base']['package']:
        restart.start(self)
        return
    return


def go_home(self):
    """
    回到首页
    """
    self.logger.warning('开始回到首页')
    app = self.d.app_current()
    if app['package'] != self.bc['baas']['base']['package']:
        restart.start(self)
        return
    if recursion_click_house(self):
        return
    restart.start(self)
    return


def to_menu(self, end, pos, cl=None, rate=None):
    possible = {
        'restart_news': (1232, 42),
        'home_news': (1140, 100),
        'home_news2': (1140, 100),
        'home_news-intl': (1226, 54),
        'home_store-error': (641, 501),
        'work_task_big-month-menu': (1245, 40),
    }
    possible.update(pos)
    image.detect(self, end, possible, cl=cl, rate=rate)


def click_house_under(self):
    self.double_click(1268, 58, False)


def recursion_click_house(self):
    """
    递归点击首页按钮，如果返回False则返回首页失败，反之返回首页成功
    """
    # The CN client can enter a full-screen idle secretary view after a long
    # period with no input. Edge taps may be ignored there, while a normal
    # in-screen tap restores the home UI.
    self.click(640, 360, False)
    time.sleep(0.3)

    cl = (769, 555)
    if self.game_server == 'intl':
        cl = (770, 500)
    pos = {
        'restart_menu': (624, 373),
        'home_skip': (780, 510),
        'restart_update': (770, 500),
        'restart_update2': cl,
        'home_fight': (510, 500),
        'restart_news': (1232, 42),
        'home_goods-update': (935, 97),
        'home_news': (1142, 104),
        'home_news2': (1142, 104),
        'home_news-intl': (1226, 54),
        'home_store-error': (641, 501),
        'work_task_big-month-menu': (1245, 40),
    }
    ends = ('home_setting', 'home_student')
    rst = image.detect(self, ends, pos, cl=(1233, 11), retry=500)
    if rst is None:
        self.logger.info('多次返回首页失败! 开始重启')
        return False
    self.click(1233, 11, False)
    self.double_click(851, 262, False)
    return True
