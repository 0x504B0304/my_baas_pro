# Decompiled from web/configs.pyc (Python 3.11, PyInstaller bundle)
# BAAS Pro - Web configuration management

import os
import shutil

from common import config


def check_config():
    config_dir = config.config_dir()

    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

        source_file = config.get_froze_path('web/static/baas.json')

        shutil.copy(
            config.get_froze_path('web/static/default_app.yaml'),
            os.path.join(config_dir, 'app.yaml'),
        )
        shutil.copy(source_file, os.path.join(config_dir, 'baas1.json'))
        shutil.copy(source_file, os.path.join(config_dir, 'baas2.json'))
        shutil.copy(source_file, os.path.join(config_dir, 'baas3.json'))

    return config_migrate()


def config_migrate():
    config_dir = config.config_dir()

    con_list = sorted([
        os.path.splitext(f)[0]
        for f in os.listdir(config_dir)
        if f.endswith('.json')
    ])

    failed = []
    for con in con_list:
        try:
            config.config_migrate(
                con, config.get_froze_path('web/static/baas.json')
            )
        except Exception:
            failed.append(con)

    return failed
