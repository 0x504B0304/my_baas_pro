# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包脚本 — BAAS Pro"""

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, copy_metadata

# 自动收集 cnocr 数据文件 (label_cn.txt, label_number.txt 等)
cnocr_datas = collect_data_files('cnocr')
# 自动收集 rapidocr 数据文件 (default_models.yaml 等)
rapidocr_datas = collect_data_files('rapidocr')
# 自动收集 rapidocr_onnxruntime
try:
    onnx_datas = collect_data_files('rapidocr_onnxruntime')
except Exception:
    onnx_datas = []
# 自动收集 cnstd
try:
    cnstd_datas = collect_data_files('cnstd')
except Exception:
    cnstd_datas = []

a = Analysis(
    ['main.py'],

    pathex=[],
    binaries=[],

    datas=[
        # 图像资源
        ('assets/images', 'assets/images'),
        ('assets/position', 'assets/position'),
        ('assets/icon', 'assets/icon'),
        ('assets/icon_white', 'assets/icon_white'),
        ('assets/file', 'assets/file'),
        # minitouch 二进制 (含 maatouch JAR)
        ('assets/minitouch', 'assets/minitouch'),
        # Web 静态资源 (渲染 schema, 默认配置, OCR 模型)
        ('web/static/render.json', 'web/static'),
        ('web/static/baas.json', 'web/static'),
        ('web/static/default_app.yaml', 'web/static'),
        ('web/static/atx-agent_0.10.0_linux_386.tar.gz', 'web/static'),
        ('web/static/ocr', 'web/static/ocr'),
        ('web/static/cnocr.zip', 'web/static'),
        # cnocr 数据标签文件
        *cnocr_datas,
        # rapidocr 模型配置
        *rapidocr_datas,
        *onnx_datas,
        *cnstd_datas,
    ],

    # --- 隐式导入 (动态 import/__import__ 的模块) ---
    hiddenimports=[
        # GUI
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        # OpenCV
        'cv2',
        # NumPy / scikit-image
        'numpy',
        'skimage',
        'skimage.metrics',
        # OCR
        'cnocr',
        'onnxruntime',
        # 设备控制
        'uiautomator2',
        'adbutils',
        # 工具
        'yaml',
        'fuzzywuzzy',
        # 通用
        'json',
        're',
        'datetime',
        'threading',
        'multiprocessing',
        'subprocess',
        'getpass',
        'shutil',
        'zipfile',
        'copy',
        'collections',
        # common 子模块
        'common.baas',
        'common.process',
        'common.config',
        'common.stage',
        'common.image',
        'common.color',
        'common.ocr',
        'common.limit',
        'common.app',
        'common.log',
        'common.encrypt',
        'common.device',
        'common.position',
        'common.controller',
        'common.controller_scale',
        'common.controller_u2',
        'common.controller_adb',
        'common.controller_minitouch',
        'common.controller_maatouch',
        # gui 子模块
        'gui.main_window',
        'gui.sidebar',
        'gui.home_widget',
        'gui.dashboard_widget',
        'gui.config_panel',
        'gui.widgets',
        'gui.styles',
        'gui.release_dialog',
        # web
        'web.configs',
        # modules — baas 基础
        'modules.baas.home',
        'modules.baas.restart',
        'modules.baas.env_check',
        'modules.baas.fhx',
        'modules.baas.delete_friend',
        # modules — 日常
        'modules.daily.cafe',
        'modules.daily.group',
        'modules.daily.schedule',
        'modules.daily.make',
        # modules — 攻击/战斗
        'modules.attack.arena',
        'modules.attack.total_war',
        'modules.attack.tactics_test',
        'modules.attack.wanted',
        'modules.attack.normal_task',
        'modules.attack.hard_task',
        'modules.attack.special_entrust',
        'modules.attack.exchange_meeting',
        # modules — 活动
        'modules.activity.cn_activity',
        'modules.activity.jp_activity',
        'modules.activity.intl_activity',
        'modules.activity.activity_story',
        'modules.activity.cn_jmjh',
        'modules.activity.god_cross',
        # modules — 奖励
        'modules.reward.work_task',
        'modules.reward.mailbox',
        # modules — 商店
        'modules.shop.shop',
        'modules.shop.buy_ap',
        # modules — 剧情
        'modules.story.momo_talk',
        'modules.story.main_story',
        # modules — 任务
        'modules.task.challenge_hard_task',
        'modules.task.challenge_normal_task',
        # modules — 推图
        'modules.exp.normal_task.exp_normal_task',
        'modules.exp.hard_task.exp_hard_task',
        # stage_data (动态 __import__)
        'modules.exp.normal_task.stage_data',
    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 递归收集 assets/position 和 modules/exp 下的所有 stage_data 模块
for root, dirs, files in os.walk('assets/position'):
    for f in files:
        if f.endswith('.py') and f != '__init__.py':
            mod = os.path.splitext(os.path.join(root, f).replace(os.sep, '.'))[0]
            a.hiddenimports.append(mod)

for root, dirs, files in os.walk('modules/exp/normal_task/stage_data'):
    for f in files:
        if f.endswith('.py') and f != '__init__.py':
            mod = 'modules.exp.normal_task.stage_data.' + os.path.splitext(f)[0]
            a.hiddenimports.append(mod)

for root, dirs, files in os.walk('modules/exp/hard_task/stage_data'):
    for f in files:
        if f.endswith('.py') and f != '__init__.py':
            mod = 'modules.exp.hard_task.stage_data.' + os.path.splitext(f)[0]
            a.hiddenimports.append(mod)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='baas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/common/ba.ico',
)

if os.environ.get('BAAS_ONEFILE') == '1':
    # onefile: EXE 已内嵌全部依赖，无需 COLLECT
    pass
else:
    # onedir: 薄壳 EXE + 外部依赖目录 (增量构建快)
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=False,
        name='baas',
    )
