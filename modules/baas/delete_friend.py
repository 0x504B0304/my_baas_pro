import time
from common import image, limit
from modules.baas import home


def start(self):
    if self.game_server != 'cn':
        self.logger.error('当前功能仅国服支持')
        return
    home.go_home(self)
    to_friend_manage(self)
    delete_friend(self)
    home.go_home(self)


def to_friend_manage(self):
    pos = {
        'home_student': (535, 640),
        'group_guide': (650, 377),
        'delete_friend_fri-manage': (535, 465),
    }
    home.to_menu(self, 'delete_friend_menu', pos)


def delete_friend(self):
    if image.compare_image(self, 'delete_friend_del-fri', 0):
        self.logger.warning('没有需要删除的好友')
        return
    self.click(1125, 260)
    image.detect(self, 'delete_friend_del-notice')
    self.click(772, 500)
    time.sleep(0.5)
    return delete_friend(self)
