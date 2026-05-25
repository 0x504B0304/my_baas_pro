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
    # 已禁用许可检测
    return


def get_fn_state(self):
    # 已禁用许可检测，始终返回 active
    return 'active'


def check_fn_limit(self, prefix="<b style='color:red;font-size:20px'>当前功能试用次数已用光！请升级为赞助版本或关闭该任务,谢谢~</b>"):
    # 已禁用许可检测限制
    return False


def register():
    # 已禁用许可注册检测
    global user_type, source, user_id, ca, price
    user_type = 'support'
    source = ''
    user_id = ''
    ca = 0
    price = 0
    return 'ok'


def get_price():
    # 已禁用许可检测
    return {'price': '0.00', 'time': ''}


def send_msg(self, priority, title, content):
    # 已禁用许可检测，跳过消息推送
    return


def check_limit(self):
    # 已禁用许可检测
    self.guid = 'disabled'
    return
