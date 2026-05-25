from common import stage, color
from modules.baas import home


def start(self):
    home.go_home(self)
    pos = {'home_student': (1144, 37)}
    home.to_menu(self, 'mailbox_menu', pos)
    if color.check_rgb(self, (1090, 683)):
        self.logger.warning('开始领取奖励')
        self.click(1136, 669)
        stage.close_prize_info(self, False, True)
    else:
        self.logger.info('没有需要领取的奖励')
    home.go_home(self)
