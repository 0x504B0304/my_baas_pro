from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser

_RELEASE_HTML = '\n<h1>BAAS Pro更新日志</h1>\n\n<hr/>\n<div>\n<h1>v6.0.0.5 2026年5月26日</h1>\n<h3>🚀 新功能</h3>\n<ol>\n  <li><b>多触控后端</b> 新增触控抽象层，支持四种后端切换：uiautomator2、ADB shell、Minitouch、MaaTouch；GUI 配置面板可选，首次使用自动推送二进制</li>\n  <li><b>多分辨率支持</b> 不再强制 1280x720，支持 16:9 且 ≥720p 的任意分辨率，截图自动缩放、坐标自动映射</li>\n  <li><b>双指捏合</b> 咖啡厅打开后自动缩小视图，多触点同步注入</li>\n</ol>\n<h3>🐛 Bug修复</h3>\n<ol>\n  <li>修复 uiautomator2 以外后端 app_current 检测不准确的问题</li>\n  <li>修复特定模拟器下后台子进程弹出控制台窗口的问题</li>\n</ol>\n</div>\n\n<hr/>\n<div>\n<h1>v6.0.0.1 2026年4月30日</h1>\n<h3>🐛 Bug修复</h3>\n<ol>\n  <li><b>特殊委托</b> 修复日服通缉悬赏和特殊委托导航坐标与国服/国际服不一致导致点击偏移的问题，三服独立坐标配置</li>\n  <li><b>购买体力</b> 修正日服首页到购买体力入口的点击坐标</li>\n  <li><b>打包</b> 修复打包后 SVG 图标路径解析失败的问题</li>\n  <li><b>主窗口</b> 关闭窗口时自动终止所有账号子进程</li>\n</ol>\n<h3>🖼️ 图像资源更新</h3>\n<ol>\n  <li>更新日服多处界面截图（任务信息窗口、通缉悬赏购票、首页设置/学生按钮、小组引导、特殊委托菜单）</li>\n  <li>新增日服学园交流会帮助页图片</li>\n</ol>\n</div>\n\n<hr/>\n<div>\n<h1>v6.0.0 2026年4月17日</h1>\n<h3>🚀 架构重构</h3>\n<ol>\n  <li><b>全面迁移至CS架构</b> 移除 浏览器依赖，改为原生桌面应用，内存占用大幅降低，启动速度更快</li>\n  <li><b>全新主窗口</b> 新增自定义标题栏、面包屑导航，窗口位置/大小跨会话记忆</li>\n  <li><b>侧边栏导航</b> 全新可折叠侧边栏，支持多账号列表、功能菜单树形结构，左侧菜单可收起</li>\n  <li><b>亮色/暗色主题</b> 支持一键切换，偏好持久化保存，全局样式统一</li>\n</ol>\n<h3>✨ 新功能</h3>\n<ol>\n  <li><b>总览页面</b> 新增账号总览面板，实时展示各任务状态、下次执行时间，支持单任务快捷操作</li>\n  <li><b>实时日志面板</b> 总览页内嵌日志流，支持自动滚动开关、一键清空，可折叠显示/隐藏</li>\n  <li><b>配置管理</b> 新增配置文件管理页，支持新增、重命名、删除、排序、复制来源，一键打开文件目录</li>\n  <li><b>自动启动</b> 每个账号可独立设置开机/启动时自动运行，多账号按序依次启动</li>\n  <li><b>可视化配置编辑器</b> 配置面板支持可视化表单与 JSON 双模式切换，JSON 模式带语法高亮</li>\n  <li><b>多选控件</b> 配置项支持多选 Tag 模式，操作体验更直观</li>\n  <li><b>关闭行为设置</b> 可配置关闭窗口时最小化到托盘还是直接退出，支持记住选择</li>\n  <li><b>日志写入开关</b> 支持动态开启/关闭日志文件写入，父子进程通过共享内存同步状态</li>\n  <li><b>还原设置</b> 一键重置窗口、主题、排序、自动启动等应用配置，不影响账号数据</li>\n  <li><b>清理日志</b> 主页支持查看日志目录占用大小并一键清理</li>\n</ol>\n<h3>⚡ 性能优化</h3>\n<ol>\n  <li><b>进程架构</b> 每个账号独立子进程运行，互不影响，崩溃自动隔离</li>\n  <li><b>日志渲染</b> 日志面板按行增量渲染，大量日志不再卡顿</li>\n  <li><b>配置读写</b> 配置持久化改为 YAML 格式，读写效率更高，注释友好</li>\n  <li><b>主题切换</b> 切换亮暗模式无需重启，实时应用无闪烁</li>\n</ol>\n<h3>🐛 Bug修复</h3>\n<ol>\n  <li><b>国际服-购买体力</b> 修复因游戏更新导致的卡识别BUG</li>\n  <li><b>国际服-日程</b> 修复因游戏更新导致的卡识别BUG</li>\n  <li><b>国际服-商店</b> 修复因游戏更新导致的卡识别BUG</li>\n  <li><b>国服-日程</b> 修复因游戏更新导致的卡识别BUG</li>\n  <li><b>竞技场</b> 修复国服/国际服 AP 限制识别异常</li>\n  <li><b>主线剧情</b> 修复国服/国际服进入剧情菜单偶发卡住的问题</li>\n  <li><b>删除好友</b> 修复删除通知识别偏移问题</li>\n</ol>\n</div>\n'


class ReleaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('更新日志')
        self.resize(860, 720)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(_RELEASE_HTML)
        layout.addWidget(browser, 1)


def show_release(parent=None):
    dlg = ReleaseDialog(parent)
    dlg.exec()
