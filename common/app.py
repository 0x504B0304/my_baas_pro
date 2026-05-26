import json
import os
import sys

import yaml


def _resource_path(relative_path):
    if hasattr(sys, 'frozen'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

version = 'v6.0.0.1'

_YAML_TEMPLATE = (
    '# BAAS Pro 应用配置文件\n'
    '# 此文件由程序自动维护，也可手动编辑\n'
    '\n'
    '# 版本号：记录上次已查看的版本，用于判断是否弹出更新日志\n'
    '# 请勿手动修改，否则每次启动都会弹出更新日志\n'
    'version: {version}\n'
    '\n'
    '# 账号配置排序：决定侧边栏中账号的显示顺序\n'
    '# 列表中未出现的账号会按字母顺序追加到末尾\n'
    '# 示例：\n'
    '#   config_order:\n'
    '#     - 账号A\n'
    '#     - 账号B\n'
    'config_order:{config_order}\n'
    '\n'
    '# 自动启动：启动脚本时自动运行的账号配置列表\n'
    '# 示例：\n'
    '#   auto_start:\n'
    '#     - 账号A\n'
    'auto_start:{auto_start}\n'
    '\n'
    '# 日志显示：true = 显示实时日志，false = 关闭日志轮询（节省性能）\n'
    'log_show: {log_show}\n'
    '\n'
    '# 界面主题：true = 暗色主题，false = 亮色主题\n'
    'dark_theme: {dark_theme}\n'
    '\n'
    '# 窗口位置和大小（由程序自动维护，请勿手动修改）\n'
    'geometry: {geometry}\n'
    '\n'
    '# 关闭窗口行为：null = 每次询问，tray = 隐藏到托盘，quit = 直接退出\n'
    'close_action: {close_action}\n'
)


def _app_file() -> str:
    return _resource_path('configs/app.yaml')


def _read_app_data() -> dict:
    try:
        with open(_app_file(), 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if content.startswith('{'):
            data = json.loads(content)
            _write_app_data(data)
            return data
        result = yaml.safe_load(content)
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def _write_app_data(data: dict):
    try:
        ver = data.get('version', '')
        order = data.get('config_order', [])
        auto_start = data.get('auto_start', [])
        dark_theme = data.get('dark_theme', False)

        def _item(n):
            s = str(n)
            if s.lstrip('-').isdigit():
                return f'"{s}"'
            return s

        def _list_str(lst):
            return '\n' + '\n'.join(f'  - {_item(n)}' for n in lst) if lst else ' []'

        log_show = data.get('log_show', True)
        geo = data.get('geometry')
        if isinstance(geo, dict):
            geo_str = '{x: %d, y: %d, w: %d, h: %d}' % (
                geo.get('x', 100),
                geo.get('y', 100),
                geo.get('w', 1280),
                geo.get('h', 800),
            )
        else:
            geo_str = 'null'

        close_action = data.get('close_action')
        if close_action in ('tray', 'quit'):
            close_action_str = f'"{close_action}"'
        else:
            close_action_str = 'null'

        content = _YAML_TEMPLATE.format(
            version=f'"{ver}"',
            config_order=_list_str(order),
            auto_start=_list_str(auto_start),
            log_show='true' if log_show else 'false',
            dark_theme='true' if dark_theme else 'false',
            geometry=geo_str,
            close_action=close_action_str,
        )

        os.makedirs(os.path.dirname(_app_file()), exist_ok=True)
        with open(_app_file(), 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception:
        pass


def check_show_release() -> bool:
    data = _read_app_data()
    if data.get('version') == version:
        return False
    data['version'] = version
    _write_app_data(data)
    return True


def load_theme() -> bool:
    return _read_app_data().get('dark_theme', False)


def save_theme(dark: bool):
    data = _read_app_data()
    data['dark_theme'] = dark
    _write_app_data(data)


def load_log_show() -> bool:
    return _read_app_data().get('log_show', True)


def save_log_show(show: bool):
    data = _read_app_data()
    data['log_show'] = show
    _write_app_data(data)


def load_auto_start() -> list:
    return _read_app_data().get('auto_start', [])


def save_auto_start(accounts: list):
    data = _read_app_data()
    data['auto_start'] = accounts
    _write_app_data(data)


def load_config_order() -> list:
    return _read_app_data().get('config_order', [])


def save_config_order(order: list):
    data = _read_app_data()
    data['config_order'] = order
    _write_app_data(data)


def load_geometry() -> dict | None:
    return _read_app_data().get('geometry') or None


def save_geometry(x: int, y: int, w: int, h: int):
    data = _read_app_data()
    data['geometry'] = {'x': x, 'y': y, 'w': w, 'h': h}
    _write_app_data(data)


def reset_app_config():
    """将 app.yaml 重置为默认状态（保留 version 字段避免再次弹更新日志）。"""
    _write_app_data({'version': version})


def load_close_action() -> str | None:
    """返回 'tray'、'quit' 或 None（每次询问）。"""
    v = _read_app_data().get('close_action')
    if v in ('tray', 'quit'):
        return v
    return None


def save_close_action(action: str | None):
    data = _read_app_data()
    data['close_action'] = action
    _write_app_data(data)


def clear_geometry():
    data = _read_app_data()
    data.pop('geometry', None)
    _write_app_data(data)




def get_ordered_accounts() -> list:
    """返回按用户排序的账号列表（自动追加未排序的新账号）。"""
    from common.config import config_dir
    d = config_dir()
    if not os.path.exists(d):
        return []
    existing = set(
        os.path.splitext(f)[0]
        for f in os.listdir(d)
        if f.endswith('.json')
    )
    order = [str(n) for n in load_config_order()]
    result = [n for n in order if n in existing]
    result += sorted(existing - set(result))
    return result
