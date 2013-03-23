# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import sys
import logging
import warnings
from logging import INFO, WARN, DEBUG
from acrylamid.colors import bold, red, green, yellow, black

SKIP = 15
logger = fatal = critical = warn = info = skip = debug = error = exception = None


class TerminalHandler(logging.StreamHandler):
    """A handler that logs everything >= logging.WARN to stderr and everything
    below to stdout."""

    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.stream = None  # reset it; we are not going to use it anyway

    def emit(self, record):
        if record.levelno >= logging.WARN:
            self.__emit(record, sys.stderr)
        else:
            self.__emit(record, sys.stdout)

    def __emit(self, record, strm):
        self.stream = strm
        logging.StreamHandler.emit(self, record)


class ANSIFormatter(logging.Formatter):
    """Implements basic colored output using ANSI escape codes.  Currently acrylamid
    uses nanoc's color and information scheme: skip, create, identical, update,
    re-initialized, removed.

    If log level is greater than logging.WARN the level name is printed red underlined.
    """

    def __init__(self, fmt='[%(levelname)s] %(name)s: %(message)s'):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):

        keywords = {'create': green, 'update': yellow, 'skip': black, 'identical': black,
            're-initialized': yellow, 'remove': black, 'notice': black, 'execute': black}

        if record.levelno in (SKIP, INFO):
            for item in keywords:
                if record.msg.startswith(item):
                    record.msg = record.msg.replace(item, ' '*2 + \
                                    keywords[item](bold(item.rjust(9))))
        elif record.levelno >= logging.WARN:
            record.levelname = record.levelname.replace('WARNING', 'WARN')
            record.msg = ''.join([' '*2, u"" + red(bold(record.levelname.lower().rjust(9))),
                                  '  ', record.msg])

        return logging.Formatter.format(self, record)


class SkipHandler(logging.Logger):
    """Adds ``skip`` as new log item, which has a value of 15

    via <https://github.com/Ismael/big-brother-bot/blob/master/b3/output.py>"""
    def __init__(self, name, level=logging.NOTSET):
        logging.Logger.__init__(self, name, level)

    def skip(self, msg, *args, **kwargs):
        self.log(15, msg, *args, **kwargs)


def init(name, level, colors=True):

    global logger, critical, fatal, warn, info, skip, debug, error, exception

    logging.setLoggerClass(SkipHandler)
    logger = logging.getLogger(name)

    handler = TerminalHandler()
    if colors:
        handler.setFormatter(ANSIFormatter('%(message)s'))

    logger.addHandler(handler)
    logger.setLevel(level)

    error = logger.error
    fatal = logger.fatal
    critical = logger.critical
    warn = logger.warn
    info = logger.info
    skip = logger.skip
    debug = logger.debug
    exception = logger.exception

    warnings.resetwarnings()
    warnings.showwarning = showwarning if level == DEBUG else lambda *x: None


def setLevel(level):
    global logger
    logger.setLevel(level)


def level():
    global logger
    return logger.level


def showwarning(msg, cat, path, lineno):
    print path + ':%i' % lineno
    print '%s: %s' % (cat().__class__.__name__, msg)


__all__ = ['fatal', 'warn', 'info', 'skip', 'debug', 'error',
           'WARN', 'INFO', 'SKIP', 'DEBUG', 'setLevel', 'level']
