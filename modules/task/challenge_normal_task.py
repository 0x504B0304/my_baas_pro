import time
from common import image, limit, stage
from modules.attack import normal_task, hard_task
from modules.baas import home
from modules.exp.normal_task import exp_normal_task
from modules.story import main_story


def start(self):
    home.go_home(self)
    normal_task.to_choose_region(self)
    normal_task.change_task(self)
    stage_list = self.tc['config']['stage']
    result = []
    for task in stage_list:
        if '-' not in task:
            for i in range(1, 6):
                result.append('{0}-{1}'.format(task, i))
        else:
            result.append(task)
    self.load_config()
    self.md = self.tc
    self.md['config']['stage'] = result
    self.bc[self.tc['task']].update(self.md)
    self.save_config()
    for task in result[:]:
        gk = task
        self.logger.error('开始执行普通开图:{0}'.format(gk))
        region, lv = task.split('-')
        self.stage_data = exp_normal_task.get_stage_data(self, region)
        if gk not in self.stage_data:
            self.logger.critical('本关卡{0}尚未支持挑战任务，正在全力研发中...'.format(gk))
            continue
        normal_task.choose_region(self, int(region))
        stage.screen_swipe(self, 0, 0, threshold2=False, reset=False, f=(911, 610, 911, 40, 0.55))
        if int(region) in normal_task.normal_position_third:
            stage.screen_swipe(self, int(lv), 3, threshold2=False, reset=False, f=(911, 610, 911, 40, 0.55))
            normal_task.open_task_info_window(self, normal_task.normal_position_third[int(region)][int(lv)])
        else:
            normal_task.open_task_info_window(self, normal_task.normal_position[int(lv)])
        state = check_stage(self)
        if state == 'continue':
            continue
        if state == 'break':
            break
        exp_normal_task.choose_team_and_start_action(self, gk)
        main_story.auto_fight(self)
        self.logger.info('强制等待25秒...')
        time.sleep(25)
        exp_normal_task.to_task_menu(self)
        self.load_config()
        self.md = self.tc
        self.md['config']['stage'].remove(task)
        self.bc[self.tc['task']].update(self.md)
        self.save_config()
    home.go_home(self)


def check_stage(self):
    ends = ('normal_task_buy-hard-count', 'normal_task_buy-ap-window', 'fight_start-task')
    pos = {'normal_task_task-info-window': (947, 540)}
    end = image.detect(self, ends, pos)
    if end == 'normal_task_buy-hard-count':
        home.click_house_under(self)
        return 'continue'
    if end == 'normal_task_buy-ap-window':
        return 'break'
    return 'ok'
