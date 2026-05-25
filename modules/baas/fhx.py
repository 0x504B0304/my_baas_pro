from common import config
from modules.baas import restart


def start(self):
    if self.game_server != 'cn':
        self.logger.error('不是国服,不用反和谐!')
        return
    self.log_title('开始反和谐')
    pkg = self.bc['baas']['base']['package']
    self.logger.warning('开始推送反和谐文件到模拟器中...')
    self.d.push(config.get_froze_path('assets/file/LocalizeConfig.txt'),
                '/sdcard/Android/data/{0}/files/'.format(pkg))
    self.logger.info('反和谐已完成，开始重启游戏')
    restart.only_stop(self)
    restart.start(self)
    return
