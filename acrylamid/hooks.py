# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import os
import io
import re
import types
import shutil
import multiprocessing

from os.path import isfile, getmtime, isdir, dirname
from tempfile import mkstemp
from functools import partial

from acrylamid import log
from acrylamid.utils import hash
from acrylamid.errors import AcrylamidException
from acrylamid.helpers import event, memoize, system
from acrylamid.lib.async import Threadpool

pool = None


def modified(src, dest):
    return not isfile(dest) or getmtime(src) > getmtime(dest)


def run(cmd, ns, src, dest=None):
    """Execute `cmd` such as `yui-compressor %1 -o %2` in-place.
    If `dest` is none, you don't have to supply %2."""

    assert '%1' in cmd
    cmd = cmd.replace('%1', src)

    if dest:
        assert '%2' in cmd
        cmd = cmd.replace('%2', dest)

        if not isdir(dirname(dest)):
            os.makedirs(dirname(dest))

    try:
        rv = system(cmd, shell=True)
    except (AcrylamidException, OSError):
        log.exception("uncaught exception during execution")
        return

    if dest is None:
        fd, path = mkstemp()
        with io.open(fd, 'w') as fp:
            fp.write(rv)
        shutil.move(path, src)
        log.info('update  %s', src)
    else:
        log.info('create  %s', dest)


def simple(pool, pattern, normalize, action, ns, path):
    """
    :param pool: threadpool
    :param pattern: if pattern matches `path`, queue action
    :param action: task to run
    """
    if re.match(pattern, normalize(path), re.I):
        if isinstance(action, basestring):
            action = partial(run, action)
        pool.add_task(action, ns, path)


def advanced(pool, pattern, force, normalize, action, translate, ns, path):
    """
    :param force: re-run task even when the source has not been modified
    :param pattern: a regular expression to match the original path
    :param func: function to run
    :param translate: path translation, e.g. /images/*.jpg -> /images/thumbs/*.jpg
    """
    if not re.match(pattern, normalize(path), re.I):
        return

    if force or modified(path, translate(path)):
        if isinstance(action, basestring):
            action = partial(run, action)
        pool.add_task(action, ns, path, translate(path))
    else:
        log.skip('skip  %s', translate(path))


def initialize(conf, env):

    global pool

    hooks = conf.get('hooks', {})
    pool = Threadpool(multiprocessing.cpu_count(), wait=False)

    force = False
    normalize = lambda path: path.replace(conf['output_dir'], '')

    for pattern, action in hooks.iteritems():
        if isinstance(action, (types.FunctionType, basestring)):
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
