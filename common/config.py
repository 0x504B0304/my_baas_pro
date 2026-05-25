# Decompiled from common/config.pyc (Python 3.11, PyInstaller bundle)
# BAAS Pro - Configuration management core module

import json
import os
import sys

# Relative path prefixes that are bundled inside the frozen executable
_BUNDLED_PREFIXES = ('assets/', 'web/')


def load_ba_config(con):
    with open(config_filepath(con), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def save_ba_config(con, data):
    with open(config_filepath(con), 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False, sort_keys=False))


def get_froze_path(fp):
    base_path = ''
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    return os.path.join(base_path, fp)


def resource_path(relative_path):
    if hasattr(sys, 'frozen'):
        if hasattr(sys, '_MEIPASS') and any(
            relative_path.startswith(p) for p in _BUNDLED_PREFIXES
        ):
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            return os.path.join(
                os.path.dirname(sys.executable), relative_path
            )
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, relative_path)


def config_filepath(con):
    return os.path.join(
        resource_path('configs'), '{0}.json'.format(con)
    )


def config_dir():
    return resource_path('configs')


def get_runtime_path():
    return resource_path('runtime')


def get_ss_path(self):
    return os.path.join(
        get_runtime_path(), 'ss_{0}.png'.format(self.con)
    )


def delete_keys_from_destination(src, dst):
    if isinstance(dst, dict):
        keys_to_delete = [key for key in dst if key not in src]
        for key in keys_to_delete:
            del dst[key]
        for key, value in src.items():
            if isinstance(value, dict) and isinstance(dst.get(key), dict):
                delete_keys_from_destination(value, dst[key])


def config_deep_update(source, destination):
    """
    递归地更新嵌套字典和列表结构。

    Parameters:
    source (dict): 源数据，包含要更新或添加到目标数据中的键值对。
    destination (dict): 目标数据，将被源数据更新。
    """
    delete_keys_from_destination(source, destination)

    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            config_deep_update(value, node)
        elif isinstance(value, list) and all(
            isinstance(item, dict) for item in value
        ):
            existing = destination.get(key)
            if existing:
                for i, dest_item in enumerate(existing):
                    if i < len(value):
                        config_deep_update(value[i], dest_item)
            else:
                destination[key] = value.copy()
        else:
            try:
                destination.setdefault(key, value)
            except AttributeError as e:
                print(e)

    return destination


def config_migrate(con, file_path1):
    with open(file_path1, 'r', encoding='utf-8') as f:
        src_data = json.load(f)
    dst_data = load_ba_config(con)
    updated_dst_data = config_deep_update(src_data, dst_data)
    save_ba_config(con, updated_dst_data)
