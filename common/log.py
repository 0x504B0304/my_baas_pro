import logging
import os
import sys
from datetime import datetime
from multiprocessing import Value

from common import config, app

_log_enabled: Value = Value('b', 1)


def set_log_enabled(enabled: bool):
    _log_enabled.value = 1 if enabled else 0


def init_log_enabled():
    _log_enabled.value = 1 if app.load_log_show() else 0


class ConditionalFileHandler(logging.FileHandler):
    def emit(self, record):
        if _log_enabled.value:
            super().emit(record)


class PlainTextFormatter(logging.Formatter):
    """Plain-text formatter – no HTML, no &nbsp;."""
    LEVEL_PAD = 9

    def format(self, record):
        record.asctime = self.formatTime(record, '%m-%d %H:%M:%S')
        padded = record.levelname.ljust(self.LEVEL_PAD)
        record.levelname = f'{app.version}  {padded}'
        return super().format(record)

    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        return ct.strftime('%m-%d %H:%M:%S')


class StreamToLogger:
    """Redirect stdout/stderr to the logger."""
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != '':
            self.logger.log(self.level, message.rstrip())

    def flush(self):
        pass


def pad_string(s):
    length = len(s)
    if length < 10:
        s += ' ' * (10 - length)
    return s


def create_logger(con, html_logger=True):
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)
    if html_logger and not logger.handlers:
        log_dir_path = config.resource_path('runtime/logs')
        if not os.path.exists(log_dir_path):
            os.makedirs(log_dir_path)
            print(f'The directory {log_dir_path} was created.')
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_path = config.resource_path(f'runtime/logs/{current_date}_{con}.log')
        file_handler = ConditionalFileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        formatter = PlainTextFormatter('%(levelname)s %(asctime)s │ %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        stdout_logger_handler = StreamToLogger(logger, logging.INFO)
        stderr_logger_handler = StreamToLogger(logger, logging.ERROR)
        sys.stdout = stdout_logger_handler
        sys.stderr = stderr_logger_handler
        logger.info(title('日志初始化成功'))
    return logger


def title(msg):
    bar = '═══════════════════════════════════════════════════════════════════════════════════════════'
    return f'\n{bar}\n{msg:^91}\n{bar}'
