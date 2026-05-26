import os
import sys
import time

import cv2
import numpy as np
from skimage.metrics import structural_similarity

from common import stage, config
from common.position import get_box
from modules.baas import restart


def screenshot_cut_old(self, name, ss_path=None, ss_file='', box=None):
    if box is None:
        box = get_box(self, name)
    if ss_path is None:
        ss_path = config.get_runtime_path()
    if not os.path.exists(ss_path):
        os.makedirs(ss_path)
    ss_img = screenshot_cut(self, box, 0, False)
    cv2.imwrite(ss_file, ss_img)


def screenshot_cut(self, area, before_wait=0, need_loading=True, ss=None):
    """
    截图并裁剪图片
    @param self:
    @param area: 剪切区域
    @param before_wait: 前置等待时间
    @param need_loading: 等待加载
    """
    if before_wait > 0:
        time.sleep(before_wait)
    if need_loading:
        stage.wait_loading(self)
    if len(area) == 0:
        return self.get_screenshot_array()
    if ss is None:
        self.latest_img_array = self.get_screenshot_array()
        return self.latest_img_array[area[1]:area[3], area[0]:area[2], :]
    return ss[area[1]:area[3], area[0]:area[2], :]


def show_and_hide(self, name, show_cl, hide_cl, rate=None, retry=999):
    compare_image(self, name, cl=show_cl, rate=rate, retry=retry)
    compare_image(self, name, cl=hide_cl, rate=rate, n=True, retry=retry)


def compare_image(self, name, retry=999, threshold=0.7, nl=False,
                  mis_fu=None, mis_argv=None, rate=None, n=False,
                  box=None, ss=None, cl=None, i=1):
    """
    对图片坐标内的图片和资源图片是否匹配
    @param self:
    @param name: 资源名称
    @param retry: 重试次数
    @param threshold: 匹配程度1为
    """
    if rate is None:
        rate = self.bc['baas']['base']['ss_rate']

    if nl:
        stage.wait_loading(self)

    if box is None:
        box = get_box(self, name)

    ss_img = screenshot_cut(self, box, 0, False, ss=ss)

    res_img = get_img_data(self, name)

    if type(res_img) == bool:
        return False

    height1, width1 = ss_img.shape[:2]
    height2, width2 = res_img.shape[:2]

    if width1 != width2 or height1 != height2:
        self.logger.warning(
            f"Image dimensions mismatch (get {width1}x{height1} => target {width2}x{height2}) name:{name}, auto-resizing screenshot crop"
        )
        ss_img = cv2.resize(ss_img, (width2, height2), interpolation=cv2.INTER_AREA)

    compare = compare_image_data(self, ss_img, res_img, threshold, name, n, i)

    if compare:
        if self.compare_count <= 10:
            self.compare_count += 1

    if not compare and retry > 0:
        if i >= 10 and i % 10 == 0:
            self.logger.warning(
                '卡识别了? 模拟器DPI:240 游戏图像分辨率:最高; 渲染模式:兼容; 后期处理:开; 抗锯齿:开; 国际服:繁中语言;')
            restart.check_running(self, i)

        if mis_fu is not None:
            mis_fu(mis_argv)

        if cl is not None:
            self.click(*cl, False)

        time.sleep(rate)

        return compare_image(self, name, retry - 1, threshold, nl,
                             mis_fu, mis_argv, rate, n, box, ss, cl, i + 1)

    return compare


def compare_image_data(self, ss_img, res_img, threshold=0.7, name='', n=False, i=1):
    """
    对比两个图片数据是否相同
    """
    ss_gray = cv2.cvtColor(ss_img, cv2.COLOR_BGR2GRAY)
    res_gray = cv2.cvtColor(res_img, cv2.COLOR_BGR2GRAY)

    ssim = structural_similarity(ss_gray, res_gray)

    compare = ssim >= threshold

    if n:
        compare = not compare

    self.logger.info('CI:%s S:%.2f I:%d R:%s', name, ssim, i, compare)

    return compare


def detect(self, end, possibles=None, cl=None, pre_func=None, pre_argv=None, retry=999, rate=None):
    """
    图片探索 执行对应事件
    @param self:
    @param end: 结束出现的位置 可以是str 或 tuple(str,str...) tuple(str,int) 或 tuple(tuple
    """
    if rate is None:
        rate = self.bc['baas']['base']['ss_rate']

    if cl is not None:
        self.click(cl[0], cl[1])
        time.sleep(rate)

    i = 0
    c = 0

    while True:
        if i >= retry:
            return None

        i += 1
        c += 1

        self.logger.info('开始第 {0}/{1} 次图片检索 end:{2}'.format(i, c, end))

        if c >= 10 and c % 10 == 0:
            self.logger.warning(
                '卡识别了? 模拟器DPI:240 游戏图像分辨率:最高; 渲染模式:兼容; 后期处理:开; 抗锯齿:开; 国际服:繁中语言;')
            restart.check_running(self, c)

        stage.wait_loading(self)

        self.latest_img_array = self.get_screenshot_array()

        if pre_func is not None:
            res = pre_func(*pre_argv)
            if res:
                if res[0] == 'end':
                    return res[1]
                elif res[0] == 'click':
                    time.sleep(rate)
                    continue

        if type(end) is str:
            if compare_image(self, end, 0, 0.7, nl=False, ss=self.latest_img_array):
                return end
        else:
            for asset in end:
                if type(asset) is str:
                    asset = (asset, 0.7)
                threshold = asset[1]
                if compare_image(self, asset[0], 0, threshold, nl=False, ss=self.latest_img_array):
                    return asset[0]

        if possibles is not None:
            for asset, obj in possibles.items():
                threshold = 0.7
                if len(obj) >= 3:
                    threshold = obj[2]
                if compare_image(self, asset, 0, threshold, nl=False, ss=self.latest_img_array):
                    c = 0
                    if type(obj[0]) is int:
                        self.click(obj[0], obj[1], False)
                        time.sleep(rate)
                    else:
                        if obj[0](*obj[1]):
                            return asset

        if cl is not None:
            self.click(cl[0], cl[1])

        time.sleep(rate)


loaded_images = {}


def get_img_data(self, key):
    """
    获取图片数据，如果图片尚未加载，则加载图片
    @param self: self
    @param key: 图片资源的key
    @return: 图片数据
    """
    ck = f"{self.game_server}_{key}"

    if ck in loaded_images:
        return loaded_images[ck]

    base_path = ''

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS

    if hasattr(self, 'test'):
        assets_dir = os.path.join(os.path.dirname(__file__), '../assets/images', self.game_server)
    else:
        assets_dir = os.path.join(base_path, 'assets/images', self.game_server)

    module_name, file_name = key.rsplit('_', 1)
    file_path = os.path.join(assets_dir, module_name, f"{file_name}.png")

    if not os.path.isfile(file_path):
        return False

    image_data = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    loaded_images[ck] = image_data

    return loaded_images[ck]


def find_img(self, img, name, x_add=0, y_add=0):
    template = get_img_data(self, name)

    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

    threshold = 0.8
    locations = np.where(result >= threshold)

    seen = set()
    for pt in zip(*locations[::-1]):
        center_pt = (
            int(pt[0] + template.shape[1] / 2 + x_add),
            int(pt[1] + template.shape[0] / 2 + y_add)
        )
        seen.add(center_pt)

    return list(seen)
