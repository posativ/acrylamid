# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os
import io
import time

from tempfile import mkstemp
from itertools import chain
from os.path import join, relpath, isfile, getmtime, splitext

from acrylamid import core, helpers
from acrylamid.errors import AcrylamidException
from acrylamid.helpers import mkfile, event
from acrylamid.readers import filelist

__writers = None
__defaultwriter = None


class DefaultWriter(object):

    enabled = True

    def __init__(self, conf, env):

        self.conf = conf
        self.env = env

    def write(self, src, dest, force=False, dryrun=False):

        if not self.enabled:
            return

        if not force and isfile(dest) and getmtime(dest) > getmtime(src):
            return event.skip(dest)

        with io.open(src, 'rb') as fp:
            mkfile(fp, dest, force=force, dryrun=dryrun, mode="b")


class HTMLWriter(DefaultWriter):

    ext = '.html'

    def write(self, src, dest, **kw):

        if src.startswith(self.conf['theme'] + '/'):
            return

        return DefaultWriter.write(self, src, dest, **kw)


class System(DefaultWriter):

    def write(self, src, dest, force=False, dryrun=False):

        dest = dest.replace(self.ext, self.target)
        if not force and isfile(dest) and getmtime(dest) > getmtime(src):
            return event.skip(dest)

        if isinstance(self.cmd, basestring):
            self.cmd = [self.cmd, ]

        tt = time.time()
        fd, path = mkstemp(dir=core.cache.cache_dir)

        try:
            res = helpers.system(self.cmd + [src])
        except OSError:
            if isfile(dest):
                os.unlink(dest)
            raise AcrylamidException('%s is not available!' % self.cmd[0])

        with os.fdopen(fd, 'w') as fp:
            fp.write(res)

        with io.open(path, 'rb') as fp:
            mkfile(fp, dest, ctime=time.time()-tt, force=force, dryrun=dryrun, mode="b")


class SASSWriter(System):

    ext, target = '.sass', '.css'
    cmd = ['sass', ]


class SCSSWriter(System):

    ext, target = '.scss', '.css'
    cmd = ['sass', '--scss']


class LESSWriter(System):

    ext, target = '.less', '.css'
    cmd = ['lessc', ]


def initialize(conf, env):

    if isinstance(conf.setdefault('static', []), basestring):
        conf['static'] = [conf['static'], ]

    global __writers, __defaultwriter
    __writers = {}
    __defaultwriter = DefaultWriter(conf, env)


def compile(conf, env):
    """Copy or compile assets to output directory.  If an asset is used as template, it
    won't be copied to the output directory. All assets are tracked by the event object
    and should not be removed during `acrylamid clean`."""

    global __writers, __default

    ext_map = dict((cls.ext, cls) for cls in (
        SASSWriter, SCSSWriter, LESSWriter, HTMLWriter
    ))

    other = [(prefix, filelist(prefix, conf['static_ignore'])) for prefix in conf['static']]
    other = [((relpath(path, prefix), prefix) for path in generator)
        for prefix, generator in other]

    files = ((path, conf['theme']) for path in filelist(conf['theme'], conf['theme_ignore']))
    files = ((relpath(path, prefix), prefix) for path, prefix in files)
    files = ((path, prefix) for path, prefix in files if path not in env.engine.templates)

    for path, directory in chain(files, chain(*other)):

        # initialize writer for extension if not already there
        _, ext = splitext(path)
        if ext in ext_map and ext not in __writers:
            __writers[ext] = ext_map[ext](conf, env)

        src, dest = join(directory, path), join(conf['output_dir'], path)
        writer = __writers.get(ext, __defaultwriter)
        writer.write(src, dest, force=env.options.force, dryrun=env.options.dryrun)
