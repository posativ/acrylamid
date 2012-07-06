# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# acrylamid.tasks can add additional tasks to argument parser and execution

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
    """Add a task to a new subcommand parser, that integrates into `acrylamid --help`.

    :param aliases: a string or list of names for this task, the first is shown in ``--help``
    :param arguments: a list of :func:`argument`
    :param help: short help about this command
    :param func: function to run when the user chooses this task
    :param parents: inherit default options like ``--verbose``
    :type parents: True or False
    """

    global subparsers, default, collected

    if isinstance(aliases, basestring):
        aliases = [aliases, ]

    if aliases[0] in collected:
        return

    parser = subparsers.add_parser(
        aliases[0],
        help=help,
        parents=[default] if parents else [])

    for arg in arguments:
        parser.add_argument(*arg.args, **arg.kwargs)

    for alias in aliases:
        subparsers._name_parser_map[alias] = parser
        collected[alias] = func


class task(object):
    """A decorator to ease task creation.

    .. code-block:: python

        @task("hello", help="say hello")
        def hello(conf, env, options):

            print 'Hello World!'
    """

    def __init__(self, *args, **kwargs):

        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):

        self.kwargs['func'] = func
        register(*self.args, **self.kwargs)


def argument(*args, **kwargs):
    """A :func:`make_option`-like wrapper, use it to create your arguments::

        arguments = [argument('-i', '--ini', nargs="+", default=0)]"""

    return type('Argument', (object, ), {'args': args, 'kwargs': kwargs})
