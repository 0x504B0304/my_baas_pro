import sys
import time
from common import image, limit

source = 'killua'


class RestartTaskException(Exception):
    """抛出此异常以重新执行当前任务（不更新 next 时间）"""
    pass


def only_stop(self):
    pkg = self.bc['baas']['base']['package']
    self.log_title('开始关闭BA')
    self.d.app_stop(pkg)


activity_list = {
    'intl': 'com.nexon.bluearchive.MxUnityPlayerActivity',
    'jp': 'com.yostarjp.bluearchive.MxUnityPlayerActivity',
    'cn': None,
}


def only_start(self):
    pkg = self.bc['baas']['base']['package']
    try:
        self.log_title('开始打开BA')
        self.d.app_start(pkg, activity_list[self.game_server])
    except Exception as e:
        self.logger.critical('启动游戏失败,默认为国服官包。如果你是其他服务器，请点击菜单Baas->Baas设置 选择对应游戏服务器！')
        self.exit(e)
        return


def check_running(self, retry):
    running_apps = self.d.app_list_running()
    if self.game_server != 'jp' and self.bc['baas']['base']['package'] not in running_apps:
        for i in range(10):
            self.logger.critical('游戏发生闪退，开始重启任务！')
        if self.bc['baas']['notify']['failure']:
            limit.send_msg(self, '4', '游戏发生闪退，开始重启任务❌'.format(
                self.con), '配置：{0}'.format(self.con))
        raise RestartTaskException('游戏闪退，重启任务')

    atx_retry = 500
    task_retry = 200
    if hasattr(self, 'tc') and self.tc['task'] == 'total_war':
        atx_retry += 200
        task_retry += 200

    if retry >= atx_retry and self.compare_count <= 3:
        for i in range(10):
            self.logger.critical('ATX卡死，开始重启ATX！')
        if self.bc['baas']['notify']['failure']:
            limit.send_msg(self, '4', 'ATX卡死，开始重启ATX❌'.format(
                self.con), '配置：{0}'.format(self.con))
        if self.bc['baas']['base']['error_restart_game']:
            only_stop(self)
            only_start(self)
        self.init_atx()
        raise RestartTaskException('ATX卡死，重启任务')

    if retry >= task_retry:
        for i in range(10):
            self.logger.critical('任务卡死，开始重启任务！')
        if self.bc['baas']['base']['error_restart_game']:
            only_stop(self)
            only_start(self)
        if self.bc['baas']['notify']['failure']:
            limit.send_msg(self, '4', '任务卡死，开始重启任务❌'.format(
                self.con), '配置：{0}'.format(self.con))
        raise RestartTaskException('任务卡死，重启任务')

    return


def start(self):
    only_stop(self)
    only_start(self)
    time.sleep(10)
    start_fn = {
        'cn': start_cn,
        'intl': start_intl,
        'jp': start_jp,
    }
    start_fn[self.game_server](self)


def start_jp(self):
    pos = {
        'restart_menu': (624, 373),
        'restart_maintain': (640, 500),
        'restart_update': (769, 501),
        'restart_update2': (769, 555),
        'home_news': (1142, 104),
        'cm_agreement': (740, 490),
        'cm_get-prize': (350, 560),
    }
    image.detect(self, 'home_student', pos, cl=(1233, 11), rate=1)


def start_cn(self):
    pos = {
        'restart_menu': (624, 373),
        'restart_maintain': (640, 500),
        'restart_update': (769, 501),
        'home_news': (1142, 104),
        'cm_agreement': (740, 490),
        'cm_get-prize': (350, 560),
    }
    image.detect(self, 'home_student', pos, cl=(1233, 11), rate=1)


def start_intl(self):
    pos = {
        'restart_menu': (624, 373),
        'restart_update': (769, 501),
        'restart_news': (1232, 42),
        'home_news': (1142, 104),
        'home_news-intl': (1226, 54),
        'cm_get-prize': (350, 560),
    }
    end = image.detect(self, ('home_student', 'restart_maintain'), pos, (1233, 11))
    if end == 'restart_maintain':
        self.click(640, 500)
        self.logger.info('游戏维护中,1分钟后重启游戏')
        time.sleep(60)
        return start_intl(self)
    return
