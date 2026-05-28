# Decompiled from common/baas.pyc (Python 3.11, PyInstaller bundle)
# BAAS Pro - Core automation engine (Baas class)

import getpass
import json
import os
import shutil
import sys
import time
from datetime import datetime, timedelta

import cv2
import numpy as np
from cnocr import CnOcr

from common import stage, process, config, log, encrypt, limit
from common.config import get_froze_path
from common.controller import create_controller, Controller

from modules.activity import (
    god_cross, cn_activity, cn_jmjh,
    intl_activity, jp_activity, activity_story,
)
from modules.baas.restart import RestartTaskException
from modules.attack import (
    exchange_meeting, special_entrust, wanted, arena,
    normal_task, hard_task, total_war, tactics_test,
)
from modules.baas import restart, fhx, env_check, delete_friend
from modules.daily import group, cafe, schedule, make
from modules.exp.hard_task import exp_hard_task
from modules.exp.normal_task import exp_normal_task
from modules.reward import work_task, mailbox
from modules.shop import shop, buy_ap
from modules.story import momo_talk, main_story
from modules.task import challenge_hard_task, challenge_normal_task


func_dict = {
    'god_cross': god_cross.start,
    'cn_activity': cn_activity.start,
    'jp_activity': jp_activity.start,
    'intl_activity': intl_activity.start,
    'activity_story': activity_story.start,
    'cn_jmjh': cn_jmjh.start,
    'arena': arena.start,
    'exchange_meeting': exchange_meeting.start,
    'hard_task': hard_task.start,
    'normal_task': normal_task.start,
    'special_entrust': special_entrust.start,
    'wanted': wanted.start,
    'total_war': total_war.start,
    'tactics_test': tactics_test.start,
    'env_check': env_check.start,
    'fhx': fhx.start,
    'restart': restart.start,
    'delete_friend': delete_friend.start,
    'cafe': cafe.start,
    'group': group.start,
    'make': make.start,
    'schedule': schedule.start,
    'exp_hard_task': exp_hard_task.start,
    'exp_normal_task': exp_normal_task.start,
    'mailbox': mailbox.start,
    'work_task': work_task.start,
    'buy_ap': buy_ap.start,
    'shop': shop.start,
    'momo_talk': momo_talk.start,
    'main_story': main_story.start,
    'challenge_hard_task': challenge_hard_task.start,
    'challenge_normal_task': challenge_normal_task.start,
}


class Baas:
    ocr: CnOcr
    ocrEN: CnOcr
    ocrNum: CnOcr
    controller: Controller
    bc: dict
    tc: dict
    game_server: str
    next_task: str
    md: dict
    guid: str
    compare_count: int

    def __init__(self, con, processes_task):
        self.flag_run = True
        self.click_time = 0.0
        self.latest_img_array = None
        self.con = con
        self.compare_count = 0
        self.controller = None

        if processes_task is None:
            return

        self.logger = log.create_logger(con)
        self.load_config()
        self.game_server = self.calc_game_server()
        self.connect_serial()
        self.d = self.controller
        self.d._wait_loading = lambda: stage.wait_loading(self)
        self.init_ocr()
        env_check.check_resolution(self)
        env_check.baohuo(self, 1)

        self.processes_task = processes_task
        self.next_task = ''
        self.stage_data = {}

    def log_title(self, msg):
        self.logger.info(log.title(msg))

    def sleep(self, n):
        time.sleep(n)
        s = self.bc['baas']['base']['ss_rate'] * 5
        if s >= 3:
            s = 3
        time.sleep(s)

    def show_ocr_error(self):
        self.logger.error(
            'windows:解决方法1: 删除 C:\\Users\\你的用户名\\AppData\\Roaming\\cnocr\\2.2 目录 '
            '重新运行脚本会重新下载(可能要用梯子上网)'
        )
        self.logger.error(
            'windows:解决方法2-1: 到QQ群下载《异常问题文件下载/2.2.7z》 压缩包,'
            '解压到 C:\\Users\\你的用户名\\AppData\\Roaming\\cnocr\\2.2 目录里面'
        )
        self.logger.error(
            'windows:解决方法2-2: 到QQ群下载《异常问题文件下载/1.2.zip》 压缩包,'
            '解压到 C:\\Users\\你的用户名\\AppData\\Roaming\\cnstd\\1.2 目录里面'
        )

    def init_atx(self):
        self.log_title('开始初始化ATX')
        try:
            self.controller.app_stop('com.github.uiautomator')
            self.controller.app_start('com.github.uiautomator')
        except Exception as e:
            self.logger.error('ATX初始化失败:{0}'.format(e))
            return

    def init_ocr(self):
        self.log_title('开始初始化OCR')
        try:
            path = get_froze_path('web/static/ocr')
            # 共享检测模型：ch_PP-OCRv5_det（所有语言通用）
            det_fp = path + '/ch_PP-OCRv5_det_infer.onnx'
            # 英文 OCR：en_PP-OCRv4 识别模型
            self.ocrEN = CnOcr(
                rec_model_name='en_PP-OCRv4',
                rec_model_fp=path + '/en_PP-OCRv4_rec_infer.onnx',
                det_model_name='ch_PP-OCRv5_det',
                det_model_fp=det_fp,
            )
            if self.game_server == 'cn':
                # 中文 OCR：densenet_lite_136-gru 识别模型
                self.ocr = CnOcr(
                    rec_model_name='densenet_lite_136-gru',
                    rec_model_fp=path + '/cnocr-v2.3-densenet_lite_136-gru-epoch=004-ft-model.onnx',
                    det_model_name='ch_PP-OCRv5_det',
                    det_model_fp=det_fp,
                )
            else:
                self.ocr = self.ocrEN
            # 数字 OCR：number-densenet_lite_136-fc 识别模型
            self.ocrNum = CnOcr(
                rec_model_name='number-densenet_lite_136-fc',
                rec_model_fp=path + '/cnocr-v2.3-number-densenet_lite_136-fc-epoch=023.onnx',
                det_model_name='naive_det',
                det_model_fp=det_fp,
            )
        except Exception as e:
            self.show_ocr_error()
            self.logger.error('OCR初始化失败:{0}'.format(e))
            self.exit('OCR初始化失败，程序终止')

    def connect_serial(self):
        self.fix_atx()
        serial = self.bc['baas']['base']['serial']
        try:
            self.log_title('开始连接模拟器:{0}'.format(serial))
            ctype = self.bc['baas']['base'].get('controller_type', 'u2')
            self.controller = create_controller(ctype)
            self.controller.set_logger(self.logger)
            self.controller.connect(serial)
            self.logger.info(
                '模拟器连接成功:{0}'.format(self.controller.device_info.get('serial', serial))
            )
        except Exception as e:
            self.logger.critical(
                '模拟器连接失败，必须打开模拟器! '
                '然后设置对应模拟器端口 Baas->Baas设置->模拟器Serial'
            )
            self.logger.critical(
                '如果模拟器多开，ADB端口会不一样。'
                '点击模拟器问题诊断->查看ADB调试端口'
            )
            self.exit(e)

    def fix_atx(self):
        if os.name != 'nt':
            return
        self.log_title('开始检查ATX')
        try:
            user_name = getpass.getuser()
            ocr_zip = config.get_froze_path(
                'web/static/atx-agent_0.10.0_linux_386.tar.gz'
            )
            ocr_size = os.path.getsize(ocr_zip)
            atx_path = (
                f'C:\\Users\\{user_name}'
                '\\.uiautomator2\\cache\\atx-agent_0.10.0_linux_386.tar.gz-1f8cdf3239'
            )
            if not os.path.exists(atx_path):
                os.makedirs(atx_path, exist_ok=True)
            file_path = os.path.join(atx_path, 'atx-agent_0.10.0_linux_386.tar.gz')
            if os.path.exists(file_path):
                osize = os.path.getsize(file_path)
                if osize == ocr_size:
                    self.log_title('ATX检查完毕，无需修复')
                    return
                os.remove(file_path)
            self.logger.warning('正在修复{0}...'.format(user_name))
            shutil.copy(ocr_zip, atx_path)
            self.log_title('ATX修复完成...')
        except Exception as e:
            self.logger.error(str(e))

    def click(self, x, y, wait=True, count=1, rate=0):
        if wait:
            stage.wait_loading(self)
        self.controller.click(x, y, wait=False, count=count, rate=rate)

    def get_screenshot_array(self, raw=False):
        return self.controller.screenshot(raw=raw)

    def click_condition(self, x, y, cond, fn, fn_args, wait=True, rate=0):
        if wait:
            stage.wait_loading(self)
        self.controller.click(x, y, wait=False)
        while cond != fn(self, *fn_args):
            time.sleep(rate)
            self.controller.click(x, y, wait=False)

    def double_click(self, x, y, wait=True, count=1, rate=0):
        if wait:
            stage.wait_loading(self)
        self.controller.double_click(x, y, wait=False, count=count, rate=rate)

    def swipe(self, fx, fy, tx, ty, duration=None):
        self.controller.swipe(fx, fy, tx, ty, duration=duration)

    def long_click(self, x, y, duration=2):
        self.controller.long_click(x, y, duration=duration)

    def press(self, key):
        self.controller.press(key)

    def pinch_in(self, x, y, distance, duration=0.3):
        self.controller.pinch_in(x, y, distance, duration=duration)

    def exit(self, msg):
        if msg != '':
            if self.bc['baas']['notify']['failure']:
                limit.send_msg(
                    self, '4', '【{0}】失败'.format(self.con), str(msg)
                )
            self.logger.critical(msg)
        if hasattr(self, 'processes_task') and encrypt.md5(self.con) in self.processes_task:
            del self.processes_task[encrypt.md5(self.con)]
        sys.exit(1)

    def check_close_game(self):
        if self.bc['baas']['close_game']['enable']:
            try:
                app = self.controller.app_current()
                if app['package'] != self.bc['baas']['base']['package']:
                    return True
            except Exception as e:
                self.logger.error(e)
                self.init_atx()
                return self.check_close_game()
            wait = self.task_schedule(None)['waiting'][0]
            next_time = datetime.strptime(wait['next'], '%Y-%m-%d %H:%M:%S')
            if next_time >= datetime.now() + timedelta(seconds=600):
                self.logger.warning(
                    '当前已开启 无任务时 关闭游戏开关，节约电脑资源. '
                    '如需关闭到:Baas->Baas设置->禁用 关闭游戏设置'
                )
                restart.only_stop(self)
                return True
        return False

    def dashboard(self):
        self.log_title('BA启动')
        no_task = False
        first = True
        while True:
            fn, tc = self.get_task()
            if fn is None:
                if not no_task:
                    if self.bc['baas']['notify']['finish_all']:
                        limit.send_msg(
                            self, '4', '全部完成', '配置：{0}'.format(self.con)
                        )
                    self.log_title('任务全部执行成功')
                no_task = True
                time.sleep(3)
                if self.check_close_game():
                    time.sleep(57)
                continue
            if first:
                env_check.check_resolution(self)
                first = False
            no_task = False
            if fn == 'cn_activity':
                tc['base']['text'] = '国服-通用活动'
            if fn == 'jp_activity':
                tc['base']['text'] = '日服-通用活动'
            if fn == 'intl_activity':
                tc['base']['text'] = '国际服-通用活动'
            if fn in func_dict:
                self.processes_task[encrypt.md5(self.con)] = fn
                self.tc = tc
                self.tc['task'] = fn
                self.finish_seconds = 0
                self.md = None
                self.log_title('开始执行【' + tc['base']['text'] + '】')
                try:
                    func_dict[fn](self)
                except RestartTaskException:
                    self.log_title('重启任务【' + tc['base']['text'] + '】')
                    continue
                if self.bc['baas']['notify']['finish_single']:
                    limit.send_msg(
                        self, '3',
                        '【{0}】完成'.format(tc['base']['text']),
                        '配置：{0}'.format(self.con),
                    )
                self.log_title('执行完成【' + tc['base']['text'] + '】')
                self.finish_task(fn)
                del self.processes_task[encrypt.md5(self.con)]
            else:
                self.logger.error('函数不存在:' + fn)

    def config_path(self):
        return config.config_filepath(self.con)

    def load_config(self):
        with open(self.config_path(), 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.bc = data

    def calc_game_server(self):
        pkg = self.bc['baas']['base']['package']
        if pkg == 'com.nexon.bluearchive':
            return 'intl'
        if pkg == 'com.YostarJP.BlueArchive':
            return 'jp'
        return 'cn'

    def calc_channel(self):
        pkg = self.bc['baas']['base']['package']
        if pkg == 'com.nexon.bluearchive':
            return 'intl'
        if pkg == 'com.YostarJP.BlueArchive':
            return 'jp'
        if pkg == 'com.RoamingStar.BlueArchive.bilibili':
            return 'bilibili'
        return 'official'

    def save_config(self):
        with open(self.config_path(), 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.bc, indent=4, ensure_ascii=False, sort_keys=False))

    def get_task(self):
        self.load_config()
        queue = []
        if hasattr(self, 'next_task') and self.next_task != '':
            nt = self.next_task
            self.next_task = ''
            self.log_title('执行关联任务【{0}】'.format(self.bc[nt]['base']['text']))
            return nt, self.bc[nt]
        for ba_task, con in self.bc.items():
            if ba_task == 'baas':
                continue
            if con['base']['next'] == '' or con['base']['next'] is None:
                con['base']['next'] = datetime.now().strftime('%Y-%m-%d 00:00:00')
            try:
                next_time = datetime.strptime(con['base']['next'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                next_time = datetime.now() - timedelta(days=1)
                con['base']['next'] = datetime.now().strftime('%Y-%m-%d 00:00:00')
            try:
                if con['base']['end'] is None:
                    con['base']['end'] = ''
                else:
                    end_time = datetime.strptime(con['base']['end'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                end_time = datetime.now() + timedelta(days=1)
                con['base']['end'] = ''
            if not con['base']['enable']:
                continue
            if con['base']['end'] != '' and end_time < datetime.now():
                continue
            if next_time >= datetime.now():
                continue
            task = {
                'index': con['base']['index'],
                'next': con['base']['next'],
                'task': ba_task,
                'con': con,
            }
            queue.append(task)
        queue.sort(key=lambda x: (x['index'], datetime.strptime(x['next'], '%Y-%m-%d %H:%M:%S')))
        if len(queue) > 0:
            return queue[0]['task'], queue[0]['con']
        return None, None

    def task_schedule(self, run_task):
        self.load_config()
        running = []
        waiting = []
        queue = []
        closed = []
        for ba_task, con in self.bc.items():
            if ba_task == 'baas':
                continue
            if ba_task == 'cn_activity':
                con['base']['text'] = '国服-通用活动'
            if ba_task == 'jp_activity':
                con['base']['text'] = '日服-通用活动'
            if ba_task == 'intl_activity':
                con['base']['text'] = '国际服-通用活动'
            if not con['base']['next'] or con['base']['next'] == '':
                con['base']['next'] = datetime.now().strftime('%Y-%m-%d 00:00:00')
            try:
                next_time = datetime.strptime(con['base']['next'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                next_time = datetime.now() - timedelta(days=1)
                con['base']['next'] = datetime.now().strftime('%Y-%m-%d 00:00:00')
            try:
                if con['base']['end'] and con['base']['end'] != '':
                    end_time = datetime.strptime(con['base']['end'], '%Y-%m-%d %H:%M:%S')
                else:
                    raise ValueError
            except (ValueError, TypeError):
                end_time = datetime.now() + timedelta(days=1)
                con['base']['end'] = ''
            task = {
                'next': con['base']['next'],
                'task': ba_task,
                'text': con['base']['text'],
                'index': con['base']['index'],
            }
            if run_task is not None and run_task == ba_task:
                running.append(task)
                continue
            if not con['base']['enable']:
                closed.append(task)
                continue
            if con['base']['end'] != '' and end_time < datetime.now():
                closed.append(task)
                continue
            if next_time > datetime.now():
                waiting.append(task)
                continue
            queue.append(task)
        waiting.sort(key=lambda x: (datetime.strptime(x['next'], '%Y-%m-%d %H:%M:%S'), x['index']))
        queue.sort(key=lambda x: (x['index'], datetime.strptime(x['next'], '%Y-%m-%d %H:%M:%S')))
        return {
            'running': running,
            'waiting': waiting,
            'queue': queue,
            'closed': closed,
            'run_state': process.m.state_process(self.con),
        }

    def find_exec_task(self):
        if 'link_task' in self.tc['base']:
            self.next_task = self.tc['base']['link_task']

    def finish_task(self, fn):
        self.load_config()
        now = datetime.now()
        if self.finish_seconds > 0:
            future = now + timedelta(seconds=self.finish_seconds)
        elif 'interval' in self.tc['base'] and self.tc['base']['interval'] > 0:
            future = now + timedelta(seconds=self.tc['base']['interval'])
        else:
            future = now + timedelta(days=1)
            future = datetime(future.year, future.month, future.day, 5, 0)
        if self.md is not None:
            del self.md['task']
            self.bc[fn].update(self.md)
        self.bc[fn]['base']['next'] = future.strftime('%Y-%m-%d %H:%M:%S')
        if 'task' in self.tc:
            del self.tc['task']
        self.save_config()
        self.find_exec_task()
