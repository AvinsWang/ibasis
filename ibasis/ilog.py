import os
import logging
import traceback
import os.path as osp
from itime import iTime
base_dir = osp.dirname(osp.dirname(osp.abspath(__file__)))


def get_logger(name, log_path, level=logging.INFO):
    """获取日志对象"""
    logging.basicConfig(filename=log_path)
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(filename)s %(lineno)s |%(levelname)s %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(sh)
    return logger


class Logger:
    def __init__(self, name, log_path=None, level=logging.INFO):
        self._logger = logging.getLogger(name)
        self.handler = logging.FileHandler(log_path)
        # formatter = logging.Formatter('%(asctime)s %(funcName)s [line:%(lineno)d]  %(levelno)s %(levelname)s
        # threadID:%(thread)d threadName:%(threadName)s msg:%(message)s')
        formatter = logging.Formatter('%(asctime)s %(filename)s %(lineno)s |%(levelname)s %(message)s')
        self.handler.setFormatter(formatter)
        self._logger.addHandler(self.handler)
        self._logger.setLevel(level)
        logging.Logger.manager.loggerDict[name] = self
    
    def fmt(self, msg, level='INFO', stack_info=False, stacklevel=1):
        # sinfo = None
        # try:
        #     fn, lno, func, sinfo = self._logger.findCaller(stack_info, stacklevel)
        # except ValueError: # pragma: no cover
        #         fn, lno, func = "(unknown file)", 0, "(unknown function)"
        # record = self.makeRecord(self.name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)
        return self.handler.format(logging.makeLogRecord({'msg': msg, 'levelname': level}))

    def print(self, msg, level='INFO'):
        print(self.fmt(msg, level))

    def info(self, msg, is_print=False):
        if self._logger is not None:
            self._logger.info(msg)
        if is_print:
            self.print(msg, level='INFO')

    def warning(self, msg, is_print=False):
        if self._logger is not None:
            self._logger.warning(msg)
        if is_print:
            self.print(msg, level='WARNING')
    
    def debug(self, msg, is_print=False):
        if self._logger is not None:
            self._logger.debug(msg)
        if is_print:
            self.print(msg, level='DEBUG')

    def exception(self, e, is_print=False):
        if self._logger is not None:
            self._logger.exception(e)
        if is_print:
            self.print(traceback.format_exc(), level='EXCEPTION')
    
    def error(self, msg, is_print=False):
        if self._logger is not None:
            self._logger.error(msg)
        if is_print:
            self.print(msg, level='ERROR')

def __test():
    log = Logger('test', 'test.log')
    log.info('test', is_print=True)


if __name__ == '__main__':
    __test()