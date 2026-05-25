# BAAS Pro — Python 架构文档

BAAS Pro 是碧蓝档案 (Blue Archive) 游戏的自动化脚本工具，通过 uiautomator2 控制安卓模拟器、OCR 文字识别、图像模板匹配实现游戏日常任务自动化。

## 环境

- **Python 3.11**
- **GUI**: PySide6 (Qt 6)
- **设备控制**: uiautomator2
- **OCR**: cnocr + 内置 ONNX 模型
- **图像处理**: OpenCV (cv2), numpy, scikit-image
- **ML 框架**: PyTorch, ONNX Runtime

---

## 目录结构

```
baas_source/
├── main.py                     # 程序入口
├── launcher.py                 # Git 更新器 / 启动辅助
│
├── common/                     # 核心公共模块
│   ├── baas.py                 # 主引擎类 (Baas) — 任务调度、设备控制
│   ├── process.py              # 进程管理、IPC 通信
│   ├── config.py               # 配置读写、路径解析 (frozen/source)
│   ├── stage.py                # 游戏关卡操作 (scan、loading等待、阶段转换)
│   ├── image.py                # 图像模板匹配、SSIM 对比、detect() 探测
│   ├── color.py                # RGB 颜色距离计算与检测
│   ├── ocr.py                  # OCR 文字识别封装
│   ├── limit.py                # 授权验证、速率限制、消息推送
│   ├── app.py                  # 应用状态、bilibili 视频检测
│   ├── log.py                  # 日志系统
│   ├── encrypt.py              # 加密/哈希工具
│   ├── device.py               # 设备 ID/硬件信息获取
│   └── position.py             # UI 坐标数据模块加载器
│
├── gui/                        # PySide6 图形界面
│   ├── main_window.py          # 主窗口 (MainWindow, _TitleBar, 托盘、关闭对话框)
│   ├── sidebar.py              # 侧边栏 (Sidebar, 账号列表、菜单导航)
│   ├── home_widget.py          # 首页 (赞助/帮助/配置管理/主题设置)
│   ├── dashboard_widget.py     # 仪表盘 (任务面板、日志输出、调度计划)
│   ├── config_panel.py         # 配置面板 (JSON 编辑器、各模块参数设置)
│   ├── widgets.py              # 自定义控件 (SpinnerWidget, ToggleSwitchWidget)
│   ├── styles.py               # QSS 样式表 (light/dark 主题)
│   └── release_dialog.py       # 版本更新日志对话框
│
├── web/                        # 内嵌 Web 服务
│   └── configs.py              # Web 配置初始化与迁移
│
├── modules/                    # 游戏自动化任务模块
│   ├── activity/               # 活动模块
│   │   ├── cn_activity.py      # 国服通用活动
│   │   ├── jp_activity.py      # 日服通用活动
│   │   ├── intl_activity.py    # 国际服通用活动
│   │   ├── activity_story.py   # 活动剧情
│   │   ├── cn_jmjh.py          # 国服金麻将号
│   │   ├── god_cross.py        # 神名十字
│   │   └── alive.py            # ALIVE 活动
│   │
│   ├── attack/                 # 战斗/攻击模块
│   │   ├── arena.py            # 战术对抗赛
│   │   ├── total_war.py        # 总力战
│   │   ├── tactics_test.py     # 战术测试
│   │   ├── wanted.py           # 通缉悬赏
│   │   ├── normal_task.py      # 扫荡普通关卡
│   │   ├── hard_task.py        # 扫荡困难关卡
│   │   ├── special_entrust.py  # 特殊委托
│   │   └── exchange_meeting.py # 学园交流会
│   │
│   ├── daily/                  # 日常模块
│   │   ├── cafe.py             # 咖啡厅
│   │   ├── group.py            # 小组
│   │   ├── schedule.py         # 日程
│   │   └── make.py             # 制造
│   │
│   ├── baas/                   # 基础辅助模块
│   │   ├── home.py             # 回首页
│   │   ├── restart.py          # 重启游戏
│   │   ├── env_check.py        # 环境检查
│   │   ├── fhx.py              # 反和谐
│   │   └── delete_friend.py    # 删除好友
│   │
│   ├── shop/                   # 商店模块
│   │   ├── shop.py             # 商店购买
│   │   └── buy_ap.py           # 购买体力
│   │
│   ├── reward/                 # 奖励模块
│   │   ├── work_task.py        # 工作任务
│   │   └── mailbox.py          # 领取邮箱
│   │
│   ├── story/                  # 剧情模块
│   │   ├── main_story.py       # 主线剧情
│   │   └── momo_talk.py        # 桃信
│   │
│   ├── task/                   # 挑战模块
│   │   ├── challenge_hard_task.py  # 困难关卡挑战
│   │   └── challenge_normal_task.py # 普通关卡挑战
│   │
│   └── exp/                    # 推图/开图模块
│       ├── hard_task/exp_hard_task.py     # 困难关卡开图
│       └── normal_task/exp_normal_task.py # 普通关卡开图
│
└── assets/                     # 资源文件
    ├── icon/          (*)       # 亮色主题图标 (PNG)
    ├── icon_white/    (*)       # 暗色主题图标 (PNG)
    ├── images/        (*)       # 应用图标/图片资源 (PNG/ICO)
    ├── file/          (*)       # 其他文件
    └── position/                # UI 坐标数据 (按服务器分区)
        ├── cn/                  # 国服坐标
        ├── jp/                  # 日服坐标
        └── intl/                # 国际服坐标
```

(*) 非 Python 文件，为运行时加载的图像资源。

---

## 核心类与模块

### `Baas` (common/baas.py)

继承自 `object`，是整个自动化引擎的核心。每个游戏账号对应一个 `Baas` 实例。

**关键属性**:
- `con` — 配置名 (如 `"baas1"`)
- `d` — uiautomator2 设备连接
- `bc` — 配置数据 (`baas config` 完整 JSON)
- `tc` — 当前执行任务的配置子节点
- `ocr` / `ocrEN` / `ocrNum` — CnOcr 实例 (多语言/数字识别)
- `game_server` — 服务器判断 (`"cn"` / `"jp"` / `"intl"`)
- `logger` — 日志记录器
- `processes_task` — 多进程共享的任务状态字典
- `stage_data` — 关卡缓存数据
- `latest_img_array` — 最新截图 (numpy array, BGR)

**关键方法**:

| 方法 | 说明 |
|------|------|
| `__init__(con, processes_task)` | 初始化日志、加载配置、连接设备、初始化 OCR |
| `dashboard()` | **主循环** — 获取任务、执行、完成标记 |
| `get_task()` | 从配置中选择下一个待执行任务 |
| `task_schedule(run_task)` | 计算任务调度状态 (running/waiting/queue/closed) |
| `click(x, y, wait, count, rate)` | 模拟点击 |
| `double_click(x, y, ...)` | 模拟双击 |
| `swipe(fx, fy, tx, ty, duration)` | 模拟滑动 |
| `get_screenshot_array()` | 获取当前屏幕截图 (BGR numpy array)，自动纠正竖屏 |
| `click_condition(x, y, cond, fn, ...)` | 条件点击（循环直到 fn 返回 cond） |
| `connect_serial()` | 连接模拟器 |
| `init_ocr()` | 初始化 OCR 模型 |
| `init_atx()` | 初始化 ATX 代理 |
| `fix_ocr()` / `fix_ocr1()` | OCR 模型自动修复 |
| `fix_atx()` | ATX 代理自动修复 |
| `load_config()` / `save_config()` | 配置读写 |
| `sleep(n)` | 睡眠 (含 ss_rate 倍率) |
| `exit(msg)` | 退出并推送通知 |
| `check_close_game()` | 空闲时关闭游戏（免费版限制） |
| `finish_task(fn)` | 任务完成 — 更新下次执行时间、保存配置 |
| `find_exec_task()` | 查找关联任务 (link_task) |
| `calc_game_server()` | 根据 package 判断服务器 |
| `calc_channel()` | 根据 package 判断渠道 (bilibili/official) |
| `config_path()` | 获取当前账号配置文件的完整路径 |

### `func_dict` (common/baas.py)

模块级字典，将任务名映射到对应模块的 `start` 函数:
```python
func_dict = {
    "arena": arena.start,
    "cafe": cafe.start,
    ...
}
```

`dashboard()` 主循环通过该字典分发任务执行。

---

## 进程模型 (common/process.py)

- 主进程运行 GUI (`main_window.py`)
- 每个账号配置在独立子进程中运行 `Baas.dashboard()`
- 进程间通过 `multiprocessing.Manager().dict()` 共享任务状态 (`processes_task`)
- `process.m.state_process(con)` 获取进程运行状态

---

## 图像检测流程 (common/image.py)

1. `detect()` — 核心探测循环：
   - 循环截图 (`get_screenshot_array()`)
   - 等待 loading 消失 (`stage.wait_loading()`)
   - 模板匹配 (`compare_image()`) 检查目标图片是否出现
   - 地图导航 (`possibles` 字典) — 点击导航坐标后继续探测
   - 返回匹配到的图片名
2. `compare_image()` — 单张图片模板匹配（支持重试、条件点击）
3. `compare_image_data()` — SSIM 结构相似度对比
4. `get_img_data()` — 加载并缓存图片资源

---

## 坐标系统 (assets/position/)

每个 UI 元素按 `键名 = (x1, y1, x2, y2)` 存储边界框坐标，按服务器分区：
- `assets/position/cn/` — 国服
- `assets/position/jp/` — 日服
- `assets/position/intl/` — 国际服

运行时 `common/position.py` 的 `get_box()` 函数根据游戏服务器和元素名动态加载对应模块，支持服务器差异覆盖（国服为基础，其他服加载后 `{**cn, **region}` 合并）。

---

## 配置管理 (common/config.py)

- `load_ba_config(con)` / `save_ba_config(con, data)` — 读写 JSON 配置
- `config_migrate(con, file_path)` — 从模板迁移新字段到用户配置
- `resource_path(relative_path)` — 跨 frozen/source 路径解析
- `config_deep_update(source, destination)` — 递归深度合并配置（字典+字典列表）
- `delete_keys_from_destination(src, dst)` — 清理目标中多余的键

配置目录: `resource_path("configs")` → `<app_root>/configs/`
配置文件: `{con}.json` (如 `baas1.json`)

---

## GUI 架构 (gui/)

- **MainWindow** — 无边框主窗口，自定义标题栏 `_TitleBar`
  - `_TitleBar` — 最小化/最大化/关闭按钮、面包屑导航、主题切换
  - `_SidebarSplitter` — 可拖拽侧边栏分隔器
  - 系统托盘支持 (`QSystemTrayIcon`)
  - 关闭行为选择 (直接退出/隐藏托盘/每次询问)
- **Sidebar** — 左侧导航栏
  - 账号列表 (`QListWidget`)
  - 菜单树 (`QTreeWidget`) — 功能导航
  - 账号切换、重命名、删除
- **HomeWidget** — 首页容器
  - `_HomeTab` — 主题设置、重置配置、清理日志、更新日志
  - `_SupportTab` — 赞助/付费页面
  - `_HelpTab` — 帮助/教程页面
  - `_ConfigMgmtTab` — 配置排序、重命名、删除、自动启动管理
- **DashboardWidget** — 运行仪表盘
  - `_TaskPanel` — 任务分类面板 (运行中/队列/等待/已关闭)
  - `_LogStrip` — 实时日志滚动输出
  - `compute_schedule()` — 独立函数，计算任务调度状态
- **ConfigPanel** — JSON 编辑器 + 模块参数表单

---

## 任务调度逻辑

### `get_task()` 返回下一个待执行任务:
1. 优先检查 `link_task`（关联任务）
2. 遍历所有配置项：
   - 跳过 `baas` 自身
   - 跳过 `disabled` 任务
   - 跳过 `enabled && end_time < now`（已过期）
   - 跳过 `next_time >= now`（未到执行时间）
3. 按 `(index, next_time)` 排序，取第一个

### `task_schedule()` 分类所有任务:
- **running** — 指定正在执行的任务
- **closed** — `disabled` 或 `enabled && expired`
- **waiting** — `next_time > now`（未来执行）
- **queue** — 其余待执行任务

### `finish_task()` 完成标记:
1. 计算下次执行时间 (`next = now + interval` 或 `tomorrow 05:00`)
2. 处理 `link_task` 关联跳转
3. 保存配置

---

## 关键数据流

```
main.py
 ├── 导入 QApplication, MainWindow
 ├── 初始化 multiprocessing.Manager
 ├── 创建 MainWindow(migrate_errors)
 └── 启动 threading.Thread(target=limit.register)
     └── QApplication.exec()

对每个账号配置:
process.baas_dashboard(con, processes_task)
  └── Baas(con, processes_task)
       ├── load_config()
       ├── connect_serial()
       ├── init_ocr()
       └── dashboard()
            └── while True:
                 ├── get_task() → (fn, tc)
                 └── func_dict[fn](self)
                      └── 各模块 start(self)
```
