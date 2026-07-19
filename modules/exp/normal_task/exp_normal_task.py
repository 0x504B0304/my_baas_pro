import importlib
import time
import cv2
import numpy as np
from common import ocr, color, image, stage, limit
from modules.attack import normal_task
from modules.baas import home
from modules.story import main_story

normal_position = {
    1: (1120, 240),
    2: (1120, 340),
    3: (1120, 440),
    4: (1120, 540),
    5: (1120, 568),
}

force_position = {
    1: (124, 195),
    2: (124, 277),
    3: (124, 354),
    4: (124, 429),
}


def to_end_over(self):
    pos = {'fight_tasking': (1172, 668)}
    image.detect(self, 'fight_confirm', pos)


def to_task_menu(self):
    possible = {
        'fight_pass-confirm': (1170, 666),
        'fight_task-finish-confirm': (1033, 666),
        'fight_prize-confirm': (776, 655),
        'fight_unlock': (645, 500),
        'fight_fn-unlock': (530, 500),
    }
    ht_unlock = 'fight_ht-unlock'
    ends = (ht_unlock, 'normal_task_choose-region')
    end = image.detect(self, ends, possible, 2)
    if end == ht_unlock:
        self.logger.error('游戏解锁了困难模式。自动开始过教程。。。')
        hard_task_unlock(self)
        normal_task.change_task(self)
    stage.wait_loading(self)


def hard_task_unlock(self):
    time.sleep(5)
    position = [
        (760, 100, False, 5, 0.5),
        (40, 355, False, 3, 0.5),
        (1070, 150, False, 5, 0.5),
        (1120, 250, False, 5, 0.5),
        (945, 535, False, 20, 0.2),
        (55, 35, False, 2, 2),
    ]
    for pos in position:
        self.click(*pos)


def to_force_edit_page(self, x):
    pos = {'fight_start-task': x}
    image.detect(self, 'fight_force-edit', pos)
    return


def to_tart_task_page(self):
    time.sleep(0.5)
    pos = {
        'fight_confirm': (770, 500),
        'fight_fighting-task-info': (520, 20),
        'fight_force-edit': (1162, 658),
        'normal_task_get-box': (520, 20),
    }
    image.detect(self, ('fight_start-task', 'fight_tasking'), pos)


def start(self):
    home.go_home(self)
    normal_task.to_choose_region(self)
    normal_task.change_task(self)
    region_list = self.tc['config']['region_list']
    for region in region_list:
        normal_task.to_choose_region(self)
        region = int(region)
        self.stage_data = get_stage_data(self, region)
        if self.stage_data is None:
            home.go_home(self)
            return
        start_fight(self, region)
    home.go_home(self)


def start_task(self):
    pos = {'normal_task_task-info-window': (947, 540)}
    image.detect(self, 'fight_start-task', pos)


def auto_choose(self):
    p = {'fight_force-edit': (1200, 185)}
    image.detect(self, 'cm_bonus-tzbd', p)
    time.sleep(1)
    self.double_click(650, 600, False)
    image.compare_image(self, 'cm_bonus-tzbd', cl=(1150, 590), n=True)


def start_fight(self, region, gk=None):
    gk_none = gk is None
    if gk_none:
        normal_task.choose_region(self, region)
        gk = calc_need_fight_stage(self, region)
        if gk is None:
            self.logger.critical('本区域没有需要开图的任务关卡...')
            return
    if gk != 'side':
        if self.tc['config']['easy_mode']:
            self.click(900, 180, False)
        else:
            self.click(388, 180, False)
        time.sleep(0.5)
    if gk == 'side' or gk == 'tr-no-pass':
        self.click(645, 511)
    else:
        self.click(947, 540, False)
        time.sleep(0.5)
        self.click(770, 500, False)
    stage.wait_loading(self)
    time.sleep(1)
    ends = ('fight_force-edit', 'fight_start-task', 'fight_force-edit-tr')
    pos = {'fight_new-effect': (1015, 135)}
    end = image.detect(self, ends, pos)
    dz_fight = end == 'fight_force-edit' or end == 'fight_force-edit-tr'
    if dz_fight:
        start_choose_side_team(self)
        image.compare_image(self, end)
        image.compare_image(self, end, threshold=0.6, cl=(1171, 670), rate=1, n=True)
    else:
        if gk not in self.stage_data:
            self.logger.critical('本关卡{0}尚未支持开图，正在全力研发中...'.format(gk))
            return
        starts = get_gk_data(gk, self.stage_data, 'start')
        for n, p in starts.items():
            if n == 'sleep':
                time.sleep(p)
            elif 'swipe' in n:
                self.swipe(p[0], p[1], p[2], p[3], duration=0.1)
                time.sleep(0.5)
            else:
                start_choose_team(self, gk, n, p)
        start_mission(self)
        action = check_skip_auto_over(self)
        start_action(self, gk, self.stage_data, action)

    if region <= 4 and end == 'fight_force-edit-tr':
        self.logger.info('开始教程关卡...')
        main_story.auto_fight_put_skill(self)
    else:
        main_story.auto_fight(self)
        self.logger.info('强制等待20秒...')
        time.sleep(20)

    to_task_menu(self)
    if region > 1:
        normal_task.choose_region(self, region - 1)
    else:
        time.sleep(3)
        normal_task.choose_region(self, region)
    if gk_none:
        return start_fight(self, region)
    return


def check_skip_auto_over(self):
    time.sleep(1)
    image.compare_image(self, 'fight_auto-over', threshold=0.6, cl=(1082, 599), rate=2)
    ends = ('fight_skip-fight', 'fight_not-skip')
    end = image.detect(self, ends, cl=(1123, 545), rate=2, retry=5)
    ns = end == 'fight_not-skip'
    if self.tc['task'] == 'exp_hard_task' and ns:
        self.exit('请先通关普通任务5-5解锁跳过战斗后,在运行困难自动推图...')
    if ns:
        self.click(650, 500, False)
        return 'action-ns'
    return 'action'


def get_stage_data(self, region):
    if 'hard_task' in self.tc['task']:
        module_path = 'modules.exp.hard_task.stage_data.ht_{0}'.format(region)
    else:
        module_path = 'modules.exp.normal_task.stage_data.nt_{0}'.format(region)
    try:
        stage_module = importlib.import_module(module_path)
        stage_data = getattr(stage_module, 'stage_data', None)
        return stage_data
    except ModuleNotFoundError:
        self.logger.critical('当前区域 {0} 尚未支持开图，正在全力研发中...'.format(region))
        return


def check_task_state(self):
    wait_task_info(self)
    time.sleep(1)
    self.latest_img_array = self.get_screenshot_array()
    if image.compare_image(self, 'normal_task_tr-quest', 0, ss=self.latest_img_array):
        if image.compare_image(self, 'normal_task_tr-quest-first', 0, ss=self.latest_img_array):
            return 'tr-no-pass'
        return 'tr-pass'
    if image.compare_image(self, 'normal_task_side-quest', 0, ss=self.latest_img_array):
        return 'side'
    if self.tc['task'] == 'exp_hard_task' and image.compare_image(self, 'normal_task_box', 0, ss=self.latest_img_array):
        return 'box'
    if image.compare_image(self, 'normal_task_task-scan', 0, ss=self.latest_img_array):
        return 'sss'
    if image.compare_image(self, 'normal_task_task-scan2', 0, ss=self.latest_img_array):
        return 'sss'
    if image.compare_image(self, 'normal_task_a-task-scan', 0, ss=self.latest_img_array):
        return 'sss'
    if image.compare_image(self, 'normal_task_no-pass', 0, ss=self.latest_img_array):
        return 'no-pass'
    return 'pass'


def wait_task_info(self, open_task=False, max_retry=30):
    while max_retry > 0:
        if image.compare_image(self, 'normal_task_task-info-window', 0):
            return 'main'
        if image.compare_image(self, 'normal_task_side-quest', 0):
            return 'side'
        if image.compare_image(self, 'normal_task_tr-quest', 0):
            return 'side'
        if image.compare_image(self, 'normal_task_a-quest', 0):
            return 'side'
        time.sleep(0.1)
        if open_task:
            if self.tc['task'] == 'exp_normal_task':
                stage.screen_swipe(self, 0, 0)
            self.click(1118, 239)
            time.sleep(1)
        max_retry -= 1
        self.logger.error('max_retry {0}'.format(max_retry))
    return None


def calc_need_fight_stage(self, region):
    wait_task_info(self, True)
    stage_index = 1
    while True:
        task_state = check_task_state(self)
        self.logger.warning('当前关卡状态为:{0}'.format(task_state))

        if task_state == 'tr-pass':
            self.logger.warning('已通关教程')
            stage_index -= 1

        if task_state == 'tr-no-pass':
            self.logger.warning('未通关教程关卡，开始教程战斗')
            return task_state

        if task_state == 'side':
            self.logger.warning('未通关支线，开始支线战斗')
            return task_state

        if task_state == 'a-task':
            self.logger.warning('未通关A任务，开始A任务战斗')
            return task_state

        current_stage = get_stage(self, region, task_state, stage_index)

        if task_state == 'no-pass':
            if '-6' in current_stage:
                self.logger.warning('未通关A任务，开始A任务战斗')
                return 'a-task'
            self.logger.warning('{0} 未通关主线，开始主线战斗'.format(current_stage))
            return current_stage

        if task_state == 'box':
            self.logger.warning('{0} 发现星辉石宝箱，开始主线战斗'.format(current_stage))
            return current_stage

        if self.tc['config']['mode'] == 2:
            if task_state != 'sss' and task_state != 'tr-pass':
                self.logger.warning('{0} 未三星通关，开始主线战斗'.format(current_stage))
                return current_stage

        self.logger.warning('{0} 不满足战斗条件,查找下一关'.format(current_stage))
        self.click(1172, 358)
        stage_index += 1

        mc = 4 if self.tc['task'] == 'exp_hard_task' else 6
        a_task = region in (3, 6, 9, 12, 15, 18, 21, 24, 27)
        if a_task and mc == 6 and self.game_server != 'cn':
            mc = 7

        if stage_index >= mc:
            if image.compare_image(self, 'normal_task_a-quest', 0):
                continue
            area = (140, 200, 164, 228)
            if self.game_server != 'cn' or a_task:
                area = (145, 228, 165, 260)
            if region >= 10:
                area = (142, 200, 183, 230)
                if self.game_server != 'cn' or a_task:
                    area = (145, 230, 185, 258)
            cu_region = ocr.screenshot_get_text(self, area, self.ocrNum, 10)
            if str(region) != cu_region:
                return None


def get_stage(self, region, task_state, stage_index):
    s = '{0}-{1}'.format(region, stage_index)
    if task_state == 'box':
        return s + '-box'
    return s


def start_action(self, gk, stage_data, attr='action'):
    actions = get_gk_data(gk, stage_data, attr)
    last_i = len(actions) - 1
    for i, act in enumerate(actions):
        if 'before' in act:
            self.logger.info('前置等待{0}秒'.format(act['before']))
            time.sleep(act['before'])
        config = self.tc.get('config', {})
        before = config.get('before', 1)
        if before > 0:
            self.logger.warning('当前设置: 每回合等待时间{0}秒'.format(before))
            time.sleep(before)
        msg = '开始 {0} 次行动：{1}'.format(i + 1, act['t'])
        self.logger.info(msg)
        if act['t'] == 'exchange':
            self.logger.info('更换部队')
            self.click(83, 557)
            time.sleep(1)
        elif act['t'] == 'click':
            self.click(*act['p'])
        elif act['t'] == 'click_move':
            self.logger.info('点击并确认移动部队')
            click_and_move(self, act['p'])
        elif act['t'] == 'click_not_move':
            self.logger.info('点击并不移动部队')
            click_and_not_move(self, act['p'])
        elif act['t'] == 'click_change':
            self.click(*act['p'])
            time.sleep(1)
            self.click(act['p'][0] - 100, act['p'][1])
        elif act['t'] == 'close_skip':
            image.compare_image(self, 'fight_skip-fight', cl=(1123, 545), rate=2, retry=5, n=True)
        elif act['t'] == 'open_skip':
            image.compare_image(self, 'fight_skip-fight', cl=(1123, 545), rate=2, retry=5)
        elif act['t'] == 'abort_fight':
            image.compare_image(self, 'fight_stop', cl=(1230, 40), rate=1)
            time.sleep(1)
            self.click(906, 510)
            time.sleep(1)
            self.click(770, 500)
            image.compare_image(self, 'main_story_fight-fail', cl=(770, 500), rate=1)
            time.sleep(1)
            self.click(650, 650)
        elif act['t'] == 'end-turn':
            self.logger.info('结束回合')
            to_end_over(self)
            to_tart_task_page(self)

        if 'f' in act:
            for c in range(act['f']):
                fight_to_fight_menu(self, gk == '2-1')

        if i != last_i and 'not-wait' not in act:
            self.logger.info('等待行动结束...')
            wait_over(self)
            to_tart_task_page(self)

    self.logger.warning('行动结束,等待进入Boss战斗...')
    image.compare_image(self, 'fight_tasking', retry=1)


def fight_to_fight_menu(self, is_click=True):
    self.logger.warning('开始进入道中战斗...')
    image.compare_image(self, 'fight_tasking', retry=1)
    stage.wait_loading(self)
    if is_click:
        time.sleep(5)
        self.click(666, 356, False, 5, 0.5)
    main_story.auto_fight(self, time_out=10)
    possible = {
        'fight_pass-confirm': (1170, 666),
        'fight_pass-confirm2': (640, 660),
    }
    image.detect(self, 'fight_tasking', possible, 1)


def click_and_move(self, show_cl):
    image.show_and_hide(self, 'fight_confirm', show_cl, (770, 500), 2)


def click_and_not_move(self, show_cl):
    image.show_and_hide(self, 'fight_confirm', show_cl, (520, 500), 2)


def get_gk_data(gk, stage_data, attr):
    return get_gk_entry(gk, stage_data)[attr]


def get_gk_entry(gk, stage_data):
    data = stage_data[gk]
    while isinstance(data, str):
        data = stage_data[data]
    return data


def start_choose_team(self, gk, n, start_position=None):
    stage_data = self.stage_data
    team_names = get_gk_entry(gk, stage_data).get(n, [n])
    for team_name in team_names:
        if team_name == 'bonus':
            start_bonus_team(self, gk, start_position)
        elif team_name == 'side':
            start_choose_side_team(self)
        elif isinstance(team_name, str) and team_name[0] == '@':
            start_choose_team_yushe(self, team_name)
        else:
            choose_team_and_start_action(self, team_name, start_position)


def start_choose_team_yushe(self, team_name):
    self.logger.error('当前使用预设队伍：{0}'.format(team_name))
    choose_yushe_and_start_action(self, team_name)
    time.sleep(0.5)


def choose_yushe_and_start_action(self, team_name):
    self.logger.error('当前使用预设队伍：{0}'.format(team_name))
    image.compare_image(self, 'fight_team-lock', threshold=0.8, cl=(1201, 670), rate=2)
    time.sleep(2)
    self.click(1200, 183)
    time.sleep(1)
    self.click(1200, 183)
    self.press('back')
    time.sleep(1)
    image.compare_image(self, 'fight_team-lock', cl=(1120, 500))
    return


def choose_team_and_start_action(self, team_name, start_position=None):
    self.logger.info('当前使用队伍：{0}'.format(team_name))
    if start_position is None:
        start_mission(self)
        return
    deploy_team_to_start(self, start_position, team_name)


def start_bonus_team(self, gk, start_position=None):
    self.logger.warning('当前使用加成队伍：{0}'.format(gk))
    if start_position is not None:
        deploy_team_to_start(self, start_position)
        return
    auto_choose(self)
    start_mission(self)


def start_bonus_single_intl(self, gk):
    if self.game_server != 'intl':
        return
    self.logger.warning('当前使用加成队伍：{0}'.format(gk))
    time.sleep(1)
    image.compare_image(self, 'cm_bonus-tzbd', cl=(1200, 185))
    start_mission(self)
    time.sleep(1)
    stage.wait_loading(self)


def start_bonus_single(self, gk):
    self.logger.warning('当前使用加成队伍：{0}'.format(gk))
    start_mission(self)


def choose_bonus_and_start_action(self, team_name, bonus_index=None):
    self.logger.info('当前使用加成队伍：{0}'.format(team_name))
    image.compare_image(self, 'cm_bonus-tzbd', cl=(1140, 670))
    stage.wait_loading(self)


def start_choose_side_team(self):
    self.logger.info('开始选择副队')
    self.click(640, 500)


def select_force_fight(self, index=None):
    positions = [force_position[index]] if index in force_position else force_position.values()
    for pos in positions:
        self.click(*pos)
        time.sleep(0.5)
        self.click(640, 500)
    image.detect(self, 'fight_start-task', {})


def wait_over(self):
    stage.wait_loading(self, False)
    image.compare_image(self, 'fight_pass-confirm', cl=(770, 500), rate=2)


def start_mission(self):
    self.click(1200, 660)
    stage.wait_loading(self)


def deploy_team_to_start(self, start_position, team_name=None):
    for target in resolve_start_positions(self, start_position):
        self.click(*target)
        time.sleep(0.5)

        if self.game_server != 'cn':
            self.click(1175, 655)
            time.sleep(2)
            wait_tactical_map_ready(self)
            return

        if image.compare_image(self, 'fight_team-undeploy', retry=3, threshold=0.85):
            self.press('back')
            time.sleep(1)
            wait_tactical_map_ready(self)
            continue

        if image.compare_image(self, 'fight_team-deploy', retry=10, threshold=0.85, rate=0.5):
            image.compare_image(self, 'fight_team-deploy', retry=20, threshold=0.85,
                                cl=(1175, 655), rate=0.5, n=True)
            wait_tactical_map_ready(self)
            return

        wait_tactical_map_ready(self)


def resolve_start_positions(self, start_position):
    if self.game_server != 'cn':
        return [start_position]

    ss = self.get_screenshot_array()
    candidates = find_start_cells(self, ss)
    if not candidates:
        return [start_position]

    sx, sy = start_position
    ordered = sorted(candidates, key=lambda p: (p[0] - sx) ** 2 + (p[1] - sy) ** 2)
    nearby = [
        p for p in ordered
        if (p[0] - sx) ** 2 + (p[1] - sy) ** 2 <= 260 ** 2
    ]
    if nearby:
        self.logger.info('start position candidates for %s: %s', start_position, nearby)
        return nearby
    return [start_position]


def wait_tactical_map_ready(self, retry=40):
    if self.game_server != 'cn':
        stage.wait_loading(self)
        return

    for _ in range(retry):
        stage.wait_loading(self)
        ss = self.get_screenshot_array()
        if find_start_cells(self, ss):
            return
        time.sleep(0.5)


def find_start_cells(self, ss=None, threshold=0.7):
    if ss is None:
        ss = self.get_screenshot_array()
    template = image.get_img_data(self, 'fight_start-cell')
    if type(template) == bool:
        return []

    result = cv2.matchTemplate(ss, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    candidates = []
    for pt in zip(*locations[::-1]):
        center = (
            int(pt[0] + template.shape[1] / 2),
            int(pt[1] + template.shape[0] / 2),
        )
        if any(abs(center[0] - p[0]) < 10 and abs(center[1] - p[1]) < 10
               for p in candidates):
            continue
        candidates.append(center)
    return candidates
