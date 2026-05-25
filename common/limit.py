import json
import os
import random
import uuid
import time
import datetime

import requests

from common import ocr, image, device, encrypt, app
from modules.baas import home, restart

salt = '?vupeR@.Q3<tV0dK4B*6sf1^POb~HC'

user_type = ''
user_id = ''
source = ''
ca = 0
price = 0

https_host = 'https://baas.killuaaa.cn'
http_host = 'http://baas.killuaaa.cn'


def check_fn(self):
    state = get_fn_state(self)
    if state == 'active':
        return
    if state == 'trial':
        for i in range(3, 0, -1):
            self.logger.error(f'正在试用...开通赞助版可永久解锁全部功能。。。{i}秒后开始运行')
            time.sleep(1)
        return
    check_fn_limit(self)


def get_fn_state(self):
    r = str(uuid.uuid4())
    device_id = device.get_deviceid()
    cid = device.get_cid()
    fn_type = 'support'
    data = json.dumps({
        'D': device_id,
        'D2': cid,
        'G': self.guid,
        'T': int(time.time()),
        'R': r,
        'F': self.tc['task'],
        'FT': fn_type,
        'C': '',
        'V': app.version,
        'S': os.name,
        'Source': restart.source,
    })
    sign = encrypt.md5(data + salt)
    for i in range(3):
        try:
            rst = requests.post(https_host + '/check-fn', data=data, headers={'S': sign})
        except Exception:
            try:
                rst = requests.post(http_host + '/check-fn', data=data, headers={'S': sign})
            except Exception:
                time.sleep(1)
                continue
        if rst.status_code != 200:
            return 'unknown'
        data = rst.json()
        if data['c'] != 200:
            self.logger.critical(data['m'])
            return 'unknown'
        if data['r'] != r:
            return 'unknown'
        decoded_json = rst.content.decode('utf-8')
        sign = encrypt.md5(decoded_json + salt)
        if sign != rst.headers['S']:
            return 'unknown'
        return data['fn_state']
    return 'unknown'


def check_fn_limit(self, prefix="<b style='color:red;font-size:20px'>当前功能试用次数已用光！请升级为赞助版本或关闭该任务,谢谢~</b>"):
    if user_type != 'support':
        link = "<br/><b><a style='color:red;font-size:20px;' target=\"_blank\" href=\"/support\">点击开通赞助版! 永久解锁全部功能!</a></b>"
        end_at = datetime.datetime.fromtimestamp(ca)
        now = datetime.datetime.now()
        diff = end_at - now
        if diff.total_seconds() > 0:
            hours, remainder = divmod(diff.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            hours = int(hours)
            minutes = int(minutes)
            seconds = int(seconds)
            yj = 50
            if price == '50':
                yj = 99
            self.log_title(
                f"{prefix}</br><b style='color:red;font-size: 22px;'><del>原价{yj}！</del>限时({hours}小时{minutes}分钟{seconds}秒)优惠仅需{price}元!</b>"
                + link
            )
        else:
            self.log_title(
                f"{prefix}</br><b style='color:red;font-size: 22px;'>付款50元 永久解锁赞助版本</b>"
                + link
            )
        self.exit('')
    return False


def register():
    guid = ''
    r = str(uuid.uuid4())
    device_id = device.get_deviceid()
    cid = device.get_cid()
    data = json.dumps({
        'D': device_id,
        'D2': cid,
        'G': guid,
        'T': int(time.time()),
        'R': r,
        'C': '',
        'V': app.version,
        'S': os.name,
        'Source': restart.source,
    })
    global user_type, source, user_id, ca, price
    sign = encrypt.md5(data + salt)
    for i in range(5):
        rst = None
        try:
            rst = requests.post(https_host + '/upload', data=data, headers={'S': sign})
        except Exception:
            try:
                rst = requests.post(http_host + '/upload', data=data, headers={'S': sign})
            except Exception:
                time.sleep(1)
                continue
        if rst.status_code != 200:
            time.sleep(1)
            continue
        data = rst.json()
        if data['c'] != 200:
            return data['m']
        if data['r'] != r:
            return 'se1'
        decoded_json = rst.content.decode('utf-8')
        sign = encrypt.md5(decoded_json + salt)
        if sign != rst.headers['S']:
            return 'se2'
        user_type = data['t']
        source = data['source']
        user_id = data['u']
        ca = data['ca']
        price = data['price']
        return 'ok'
    return '网络错误! 如果您开启了 全局代理/梯子/VPN 请关掉后重试!'


def get_price():
    if user_id == '':
        return {'price': '50.00', 'time': ''}
    data = json.dumps({'identity': user_id, 'T': int(time.time())})
    sign = encrypt.md5(data + salt)
    for i in range(5):
        try:
            rst = requests.post(https_host + '/get-price', data=data, headers={'S': sign})
        except Exception:
            try:
                rst = requests.post(http_host + '/get-price', data=data, headers={'S': sign})
            except Exception:
                time.sleep(1)
                continue
        if rst.status_code != 200:
            time.sleep(1)
            continue
        data = rst.json()
        data['price'] = '{:.2f}'.format(data['price'])
        return data
    return {'price': '50.00', 'time': ''}


def send_msg(self, priority, title, content):
    try:
        if user_id == '':
            register()
            if user_id == '':
                return
        if not self.bc['baas']['notify']['enable']:
            return
        if user_type != 'support':
            self.logger.error('只有赞助版可以发送消息推送！谢谢~')
            return
        task = ''
        if 'task' in self.tc:
            task = self.tc['task']
        data = json.dumps({
            'identity': user_id,
            'task': task,
            'channel': self.calc_channel(),
            'priority': priority,
            'title': title,
            'content': content,
            'T': int(time.time()),
        })
        sign = encrypt.md5(data + salt)
        for i in range(5):
            try:
                rst = requests.post(https_host + '/send-msg', data=data, headers={'S': sign})
            except Exception:
                try:
                    rst = requests.post(http_host + '/send-msg', data=data, headers={'S': sign})
                except Exception:
                    time.sleep(1)
                    continue
            if rst.status_code != 200:
                time.sleep(1)
                continue
            return
    except Exception:
        return
    return


def check_limit(self):
    home.go_home(self)
    pos = {
        'home_student': (50, 50),
        'home_items-expire': (925, 120),
        'home_items-expire2': (925, 120),
        'home_goods-update': (935, 97),
        'home_title': (640, 562),
        'cm_get-prize': (650, 640),
    }
    home.to_menu(self, 'home_account-info', pos)
    area = image.get_box(self, 'home_account-id')
    guid = ocr.screenshot_get_text(self, area, self.ocrNum)
    home.go_home(self)
    r = str(uuid.uuid4())
    device_id = device.get_deviceid()
    cid = device.get_cid()
    self.guid = guid
    data = json.dumps({
        'D': device_id,
        'D2': cid,
        'G': guid,
        'T': int(time.time()),
        'R': r,
        'C': self.calc_channel(),
        'V': app.version,
        'S': os.name,
    })
    global source, user_type, user_id, ca, price
    sign = encrypt.md5(data + salt)
    for i in range(5):
        rst = None
        try:
            rst = requests.post(https_host + '/upload', data=data, headers={'S': sign})
        except Exception:
            self.click(640, 345, False)
            try:
                rst = requests.post(http_host + '/upload', data=data, headers={'S': sign})
            except Exception:
                self.click(640, 345, False)
                time.sleep(1)
                continue
        if rst.status_code != 200:
            self.click(640, 345, False)
            time.sleep(1)
            continue
        data = rst.json()
        if data['c'] != 200:
            if data['c'] == 403:
                self.log_title(data['m'])
                self.exit('')
            else:
                self.exit(data['m'])
        if data['r'] != r:
            self.exit('se1')
        decoded_json = rst.content.decode('utf-8')
        sign = encrypt.md5(decoded_json + salt)
        if sign != rst.headers['S']:
            self.exit('se2')
        source = data['source']
        user_type = data['t']
        user_id = data['u']
        ca = data['ca']
        price = data['price']
        return
    self.exit('网络错误! 如果您开启了 全局代理/梯子/VPN 请关掉后重试!')
