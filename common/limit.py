# BAAS Pro - Stub module (licensing removed)

user_type = 'support'
user_id = ''
source = ''
ca = 0
price = 0


def check_fn(self):
    # 已禁用许可检测
    return


def get_fn_state(self):
    # 已禁用许可检测，始终返回 active
    return 'active'


def check_fn_limit(self, prefix=""):
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
