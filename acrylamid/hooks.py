# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import re
import multiprocessing

from os.path import isfile, getmtime
from functools import partial

from acrylamid import log
from acrylamid.utils import hash
from acrylamid.helpers import event, memoize

from acrylamid.lib.async import Threadpool

pool = None


def modified(src, dest):
    return not isfile(dest) or getmtime(src) > getmtime(dest)


def simple(pool, pattern, normalize, action, ns, path):
    """
    :param pool: threadpool
    :param pattern: if pattern matches `path`, queue action
    :param action: task to run
    """
    if re.match(pattern, normalize(path)):
        pool.add_task(action, ns, normalize(path))


def advanced(pool, pattern, force, normalize, action, translate, ns, path):
    """
    :param force: re-run task even when the source has not been modified
    :param pattern: a regular expression to match the original path
    :param func: function to run
    :param translate: path translation, e.g. /images/*.jpg -> /images/thumbs/*.jpg
    """
    if not re.match(pattern, normalize(path)):
        return

    if force or modified(path, translate(path)):
        pool.add_task(action, ns, path, translate(path))
    else:
        log.info('skip  %s', translate(path))


def initialize(conf, env):

    global pool

    hooks = conf.get('hooks', {})
    pool = Threadpool(multiprocessing.cpu_count(), wait=False)

    force = False
    # force = memoize('hooks', hash(hooks.keys(), *map(getmtime, imports(env.options.conf))))
    normalize = lambda path: path.replace(conf['output_dir'], '')

    for pattern, action in hooks.iteritems():
        if hasattr(action, '__call__'):
            event.register(
                callback=partial(simple, pool, pattern, normalize, action),
                to=['create', 'update'] if not force else event.events)
        else:
            event.register(
                callback=partial(advanced, pool, pattern, force, normalize, *action),
                to=event.events)


def shutdown():

    global pool
    pool.wait_completion()
