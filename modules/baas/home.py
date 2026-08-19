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


def wake_home_ui(self):
    # The CN client can enter a full-screen idle secretary view after a long
    # period with no input. A normal in-screen tap restores the home UI.
    self.click(640, 360, False)
    time.sleep(0.3)


def to_menu(self, end, pos, cl=None, rate=None, retry=999):
    possible = {
        'restart_news': (1232, 42),
        'home_news': (1140, 100),
        'home_news2': (1140, 100),
        'home_news-intl': (1226, 54),
        'home_store-error': (641, 501),
        'work_task_big-month-menu': (1245, 40),
    }
    possible.update(pos)
    result = image.detect(self, end, possible, cl=cl, rate=rate, retry=retry)
    if result is None:
        raise restart.RestartTaskException(
            '进入菜单失败，超过{0}次图片检索: {1}'.format(retry, end)
        )
    return result


def click_house_under(self):
    self.double_click(1268, 58, False)


def _story_choice_y(screenshot):
    """Return the first visible story choice row, if any."""
    for y in (260, 304, 348):
        inside = screenshot[y - 20:y + 21, 230:1050]
        left = screenshot[y - 20:y + 21, 40:170]
        right = screenshot[y - 20:y + 21, 1110:1240]
        if not inside.size or not left.size or not right.size:
            continue
        inside_bright = ((inside > 200).all(axis=2)).mean()
        outside_bright = max(
            ((left > 200).all(axis=2)).mean(),
            ((right > 200).all(axis=2)).mean(),
        )
        if inside_bright >= 0.75 and inside_bright - outside_bright >= 0.5:
            return y
    return None


def recover_story_playback(self):
    screenshot = self.latest_img_array
    if image.compare_image(
            self, 'momo_talk_confirm-skip', 0, 0.5, ss=screenshot):
        self.logger.info('回首页时检测到剧情跳过确认')
        self.click(770, 516, False)
        return 'click', 'story_confirm_skip', 'progress'

    if image.compare_image(self, 'momo_talk_skip', 0, 0.7, ss=screenshot):
        self.logger.info('回首页时检测到剧情快进按钮')
        self.click(1212, 116, False)
        return 'click', 'story_skip', 'progress'

    if not image.compare_image(
            self, 'momo_talk_menu', 0, 0.75, ss=screenshot):
        return None

    choice_y = _story_choice_y(screenshot)
    if choice_y is not None:
        self.logger.info('回首页时检测到剧情分支选项:y=%s', choice_y)
        self.click(640, choice_y, False)
        return 'click', 'story_choice', 'progress'

    self.logger.info('回首页时检测到剧情播放界面，展开菜单')
    self.click(1205, 42, False)
    return 'click', 'story_menu', 'progress'


def recursion_click_house(self):
    """
    递归点击首页按钮，如果返回False则返回首页失败，反之返回首页成功
    """
    wake_home_ui(self)

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
    rst = image.detect(
        self,
        ends,
        pos,
        cl=(1233, 11),
        pre_func=recover_story_playback,
        pre_argv=(self,),
        retry=500,
    )
    if rst is None:
        self.logger.info('多次返回首页失败! 开始重启')
        return False
    return True
