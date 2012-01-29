# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import logging
from logging import WARN, INFO, DEBUG

SKIP = 15
logger = fatal = critical = warn = warning = info = skip = debug = None


class ANSIFormatter(logging.Formatter):
    """Implements basic colored output using ANSI escape codes."""

    # $color + BOLD
    BLACK = '\033[1;30m%s\033[0m'
    RED = '\033[1;31m%s\033[0m'
    GREEN = '\033[1;32m%s\033[0m'
    YELLOW = '\033[1;33m%s\033[0m'
    GREY = '\033[1;37m%s\033[0m'
    RED_UNDERLINE = '\033[4;31m%s\033[0m'

    def __init__(self, fmt='[%(levelname)s] %(name)s: %(message)s', debug=False):
        logging.Formatter.__init__(self, fmt)
        self.debug = debug

    def format(self, record):

        keywords = {'skip': self.BLACK, 'create': self.GREEN, 'identical': self.BLACK,
                    'update': self.YELLOW, 're-initialized': self.YELLOW,
                    'removed': self.BLACK}

        if record.levelno in (SKIP, INFO):
            for item in keywords:
                if record.msg.startswith(item):
                    record.msg = record.msg.replace(item, ' '*2 + \
                                    keywords[item] % item.rjust(8))
        elif record.levelno >= logging.WARN:
            record.levelname = record.levelname.replace('WARNING', 'WARN')
            record.msg = ''.join([' '*2, self.RED % record.levelname.lower().rjust(8),
                                  '  ', record.msg])

        return logging.Formatter.format(self, record)


class SkipHandler(logging.Logger):
    """via <https://github.com/Ismael/big-brother-bot/blob/master/b3/output.py>"""
    def __init__(self, name, level=logging.NOTSET):
        logging.Logger.__init__(self, name, level)

    def skip(self, msg, *args, **kwargs):
        self.log(15, msg, *args, **kwargs)


def init(name, level, handler=logging.StreamHandler()):

    global logger, critical, fatal, warn, warning, info, skip, debug

    logging.setLoggerClass(SkipHandler)
    logger = logging.getLogger(name)

    fmt = ANSIFormatter('%(message)s')
    if level == logging.DEBUG:
        fmt = '%(msecs)d [%(levelname)s] %(name)s.py:%(lineno)s:%(funcName)s %(message)s'

    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(level)

    critical = logger.critical
    fatal = logger.fatal
    warn = logger.warn
    warning = logger.warning
    info = logger.info
    skip = logger.skip
    debug = logger.debug


def setLevel(level):
    global logger
    logger.setLevel(level)


__all__ = ['fatal', 'warn', 'info', 'skip', 'debug',
           'WARN', 'INFO', 'SKIP', 'DEBUG', 'setLevel']

if __name__ == '__main__':
    init('test', 20)
    setLevel(15)
    logger.warn('foo')
    logger.info('changed dich')
    logger.info('create kekse')
    logger.skip('skip unused')
