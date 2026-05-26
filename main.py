# Decompiled from main.pyc (Python 3.11, PyInstaller bundle)
# BAAS Pro - Blue Archive Automation Script

import multiprocessing
import os
import sys

# Redirect stdout/stderr in frozen (PyInstaller) environment to avoid
# missing-console errors when the app has no attached terminal.
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')


def _no_window_create_process(application_name, command_line, proc_attrs,
                              thread_attrs, inherit_handles, creation_flags,
                              env_mapping, current_directory, startup_info):
    """Patch _winapi.CreateProcess to add CREATE_NO_WINDOW flag."""
    creation_flags = (creation_flags or 0) | 0x08000000  # CREATE_NO_WINDOW
    return _orig_create_process(
        application_name, command_line, proc_attrs, thread_attrs,
        inherit_handles, creation_flags, env_mapping,
        current_directory, startup_info)


# On Windows frozen builds, patch _winapi to suppress subprocess console windows.
if os.name == 'nt' and getattr(sys, 'frozen', False):
    import _winapi
    _orig_create_process = _winapi.CreateProcess
    _winapi.CreateProcess = _no_window_create_process


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from common import process, config
from web.configs import check_config


if __name__ == '__main__':
    # Record the main process PID (before fork/freeze_support)
    main_process_pid = os.getpid()
    multiprocessing.freeze_support()

    # Create shared manager and task dict (for inter-process communication)
    process.manager = multiprocessing.Manager()
    process.processes_task = process.manager.dict()

    # Only the original main process runs the GUI
    if os.getpid() == main_process_pid:
        migrate_errors = check_config()

        from gui.main_window import MainWindow

        # Set Windows taskbar icon/model ID (best-effort)
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    'BaasPro.BaasPro.1'
                )
            except Exception:
                pass

        # Create Qt application
        qt_app = QApplication(sys.argv)
        qt_app.setApplicationName('BAAS Pro')
        qt_app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)

        # Create and show the main window
        window = MainWindow(migrate_errors=migrate_errors)
        window.show()

        sys.exit(qt_app.exec())
