from common import stage, image
from modules.baas import home

meet_position = {'cnd': (1000, 200), 'ghn': (1000, 300), 'qxn': (1000, 400)}

lv_position = {1: (1116, 185), 2: (1116, 285), 3: (1116, 385), 4: (1116, 485)}

def to_exchange_meeting(self):
    pos = {
        'home_student': (1200, 573),
        'home_bus': (715, 595),
        'normal_task_task-info-window': (60, 40),
        'exchange_meeting_stage-list': (60, 40),
        'exchange_meeting_help': (1020, 133),
    }
    home.to_menu(self, 'exchange_meeting_menu', pos)

def start(self):
    home.go_home(self)
    choose_meet(self)
    home.go_home(self)

def choose_meet(self):
    fns = ['cnd', 'ghn', 'qxn']
    for fn in fns:
        tk = self.tc[fn]
        if not tk['enable']:
            continue
        to_exchange_meeting(self)
        image.compare_image(self, 'wanted_stage-list', cl=meet_position[fn], rate=1)
        rst = stage.confirm_scan(self, tk['stage'], tk['count'], 99, cl=lv_position[tk['stage']])
        if rst == 'delay':
            self.finish_seconds = 1800
            self.logger.error('没体力了，30分钟后重新执行该任务')
            return
        elif rst == 'return':
            return
