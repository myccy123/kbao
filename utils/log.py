import logging
from logging import handlers


class LevelTypeException(Exception):
    def __init__(self, x):
        # 调用基类的__init__进行初始化
        Exception.__init__(self, x)
        self.x = x


class Logger:
    LEVEL_MAP = dict()
    LEVEL_MAP['notset'] = logging.NOTSET
    LEVEL_MAP['debug'] = logging.DEBUG
    LEVEL_MAP['info'] = logging.INFO
    LEVEL_MAP['warning'] = logging.WARNING
    LEVEL_MAP['warn'] = logging.WARNING
    LEVEL_MAP['error'] = logging.ERROR
    LEVEL_MAP['critical'] = logging.CRITICAL

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        fmt = '%(asctime)s %(name)s[%(lineno)d] %(levelname)s: %(message)s'
        self.formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S")
        self.handler = logging.StreamHandler()
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def get_logger(self):
        return self.logger

    def set_level(self, level: str):
        if self.LEVEL_MAP.get(level.lower()):
            self.logger.setLevel(self.LEVEL_MAP.get(level.lower()))
        else:
            raise LevelTypeException(level)

    def add_file_handler(self, filename=None, when='D', interval=1):
        if filename is None:
            filename = self.name
        file_handler = logging.handlers.TimedRotatingFileHandler(filename,
                                                                 when=when,
                                                                 interval=interval)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
