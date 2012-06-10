# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import glob
import traceback
import argparse

from os.path import dirname, basename, join
sys.path.insert(0, dirname(__file__))

# we get them from acrylamid/__init__.py
subparsers, default = None, None

# here we collect aliases to their function
collected = {}


def initialize(_subparsers, _default, ext_dir='tasks/'):

    global subparsers, default
    subparsers, default = _subparsers, _default

    for mem in glob.glob(join(dirname(__file__), "*.py")):
        if mem.startswith('__'):
            continue
        try:
            mem = __import__(basename(mem).rsplit('.', 1)[0])
        except Exception:
            traceback.print_exc(file=sys.stdout)


def register(aliases, arguments=[], help=argparse.SUPPRESS, func=lambda *z: None, parents=True):

    global subparsers, default, collected

    if isinstance(aliases, basestring):
        aliases = [aliases, ]

    parser = subparsers.add_parser(
        aliases[0],
        help=help,
        parents=[default] if parents else [])

    for arg in arguments:
        parser.add_argument(*arg.args, **arg.kwargs)

    for alias in aliases:
        subparsers._name_parser_map[alias] = parser
        collected[alias] = func


def argument(*args, **kwargs):
    return type('Argument', (object, ), {'args': args, 'kwargs': kwargs})
