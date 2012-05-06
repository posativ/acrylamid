# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import glob
import traceback

from os.path import dirname, basename, join
sys.path.insert(0, dirname(__file__))


def get_tasks(ext_dir='tasks/'):

    tasks = dict()
    files = glob.glob(join(dirname(__file__), "*.py"))

    for mem in [basename(x).replace('.py', '') for x in files]:
        if mem.startswith('_'):
            continue
        try:
            _module = __import__(mem)
            tasks[mem] = _module
            for alias in _module.aliases:
                tasks[alias] = _module
        except (ImportError, Exception):
            traceback.print_exc(file=sys.stdout)

    return tasks
