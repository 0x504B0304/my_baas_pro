import time
import numpy as np
from common import ocr, image
from modules.baas import home, fhx, restart


def start(self):
    """
    检查环境
    @param self:
    """
    check_ss(self)
    check_resolution(self)
    if self.game_server == 'cn':
        check_clarity(self)
        return
    return


def check_ss(self):
    self.log_title('️开始截图测试')
    app = self.d.app_current()
    if app['package'] != self.bc['baas']['base']['package']:
        restart.only_start(self)
    if image.compare_image(self, 'home_black', 2, 0.99):
        self.exit('模拟器设置有误! 如果是mumu模拟器，打开模拟器设置 -> 其他 -> 其他设置 -> 取消勾选(应用运行 -> 后台挂机时保持活跃运行) ')
        return
    return


def check_resolution(self):
    """
    检查分辨率，支持16:9且≥1280x720的分辨率
    @param self:
    @return:
    """
    self.log_title('️开始检查分辨率')
    try:
        sp = self.controller.init_scale_proxy()
    except RuntimeError as e:
        self.exit(str(e))
    self.logger.info('分辨率检查通过: 原始{0}x{1}, 视图窗口: {2}x{3}, 缩放系数: x{4:.2f} y{5:.2f}'.format(
        sp.raw_width, sp.raw_height, sp.view_width, sp.view_height,
        sp.scale_x, sp.scale_y))


def baohuo(self, count):
    self.log_title('️开始检查保活开关')
    home.back_home(self)
    box = image.get_box(self, 'cm_baohuo')
    time.sleep(0.5)
    prev = image.screenshot_cut(self, box, 0, False)
    restart.only_start(self)
    time.sleep(3)
    after = image.screenshot_cut(self, box, 0, False)
    if np.array_equal(prev, after):
        if count <= 3:
            baohuo(self, count + 1)
            return
        self.exit('模拟器设置有误，请打开MuMu模拟器:右上角设置->设置中心->其他-> 取消勾选:后台挂机时保持运行，然后重启模拟器！')
        return
    return


def check_clarity(self):
    """
    开始检查清晰度
    @param self:
    @return:
    """
    self.log_title('️开始检查清晰度')
    home.go_home(self)
    self.double_click(170, 144)
    ocr.screenshot_check_text(self, '成员', (226, 167, 277, 189), 1, before_wait=1)
    self.latest_img_array = self.get_screenshot_array()
    for i in range(1, 5):
        if image.compare_image(self, 'momo_talk_peach{0}'.format(i), 0, ss=self.latest_img_array):
            if i == 1:
                home.go_home(self)
                return
            self.logger.error('游戏分辨率太低! 打开BA->选项->图像-> 分辨率:最高 后期处理:ON 抗锯齿:ON')
            home.go_home(self)
            if self.game_server == 'cn':
                self.click(1223, 40)
                ocr.screenshot_check_text(self, '菜单', (611, 248, 670, 278))
                self.click(535, 340)
                ocr.screenshot_check_text(self, '选项', (605, 130, 677, 167))
                self.click(289, 277)
                ocr.screenshot_check_text(self, '分辨率', (421, 213, 486, 237))
                self.click(432, 280)
                check_clarity(self)
                return
    home.go_home(self)
    return


def check_fhx(self):
    if self.game_server != 'cn':
        return
    self.log_title('开始检查反和谐')
    home.go_home(self)
    if ocr.screenshot_check_text(self, '等级', (25, 25, 75, 50), 1):
        self.logger.error('检测到未开启反和谐')
        fhx.start(self)
        return check_fhx(self)
    return
