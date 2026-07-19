import ctypes
import os
import sys
import traceback
from multiprocessing import Process

from common import log, encrypt, limit
from modules.baas import restart


def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def baas_dashboard(con, pt, source, log_enabled):
    from common.baas import Baas

    log._log_enabled = log_enabled
    b = None
    restart.source = source
    try:
        b = Baas(con, pt)
        b.dashboard()
    except Exception as e:
        if b is not None:
            logger = b.logger
        else:
            logger = log.create_logger(con)
        stack_trace = traceback.format_exc()
        logger.critical('Exception occurred: {0}'.format(e))
        logger.critical('Stack trace:\n{0}'.format(stack_trace))

        try:
            if b.bc['baas']['notify']['failure']:
                limit.send_msg(b, '5', '【{0}】失败❌'.format(con), str(e))
        except Exception as e:
            pass

        if pt is not None:
            task_name = pt.get(encrypt.md5(con), '')
            if isinstance(task_name, dict):
                task_name = task_name.get('task', '')
            pt[encrypt.md5(con)] = {'task': task_name, 'error': True}
    return None


manager = None
processes_task = None


class Main:
    def __init__(self):
        self.processes = {}

    def start_process(self, con):
        if encrypt.md5(con) in self.processes and self.processes[encrypt.md5(con)].is_alive():
            return None
        if encrypt.md5(con) in processes_task:
            del processes_task[encrypt.md5(con)]
        self.processes[encrypt.md5(con)] = Process(
            target=baas_dashboard,
            args=(con, processes_task, restart.source, log._log_enabled)
        )
        self.processes[encrypt.md5(con)].start()
        return None

    def set_log_enabled(self, enabled: bool):
        log.set_log_enabled(enabled)

    def stop_process(self, con):
        if encrypt.md5(con) not in self.processes or not self.processes[encrypt.md5(con)].is_alive():
            return None
        self.processes[encrypt.md5(con)].terminate()
        self.processes[encrypt.md5(con)].join()
        log.create_logger(con).info('停止运行')
        if encrypt.md5(con) in processes_task:
            del processes_task[encrypt.md5(con)]
            return None
        return None

    def state_process(self, con):
        if encrypt.md5(con) in self.processes:
            return self.processes[encrypt.md5(con)].is_alive()
        return False

    def run_task(self, con):
        if encrypt.md5(con) in processes_task:
            v = processes_task[encrypt.md5(con)]
            if isinstance(v, dict):
                if v.get('error'):
                    return None
                return v.get('task')
            return v
        return None

    def error_task(self, con):
        if encrypt.md5(con) in processes_task:
            v = processes_task[encrypt.md5(con)]
            if isinstance(v, dict) and v.get('error'):
                return v.get('task', '')
        return None


m = Main()
