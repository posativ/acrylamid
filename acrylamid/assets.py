# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import os
import io
import time
import stat
import shutil

from tempfile import mkstemp, mkdtemp
from itertools import chain
from os.path import join, relpath, isfile, getmtime, splitext

from acrylamid import core, helpers, log, utils
from acrylamid.errors import AcrylamidException
from acrylamid.helpers import mkfile, event
from acrylamid.readers import filelist

__writers = None
__defaultwriter = None


class Writer(object):
    """A 'open-file-and-write-to-dest' writer.  Only operates if the source
    file has been modified or the destination does not exists."""

    def __init__(self, conf, env):
        self.conf = conf
        self.env = env

    def modified(self, src, dest):
        return not isfile(dest) or getmtime(src) > getmtime(dest)

    def generate(self, src, dest):
        return io.open(src, 'rb')

    def write(self, src, dest, force=False, dryrun=False):
        if not force and not self.modified(src, dest):
            return event.skip(dest)

        mkfile(self.generate(src, dest), dest, force=force, dryrun=dryrun)

    def clean(self):
        pass


class HTML(Writer):
    """Copy HTML files to output if not in theme directory."""

    ext = '.html'

    def write(self, src, dest, **kw):

        if src.startswith(self.conf['theme'].rstrip('/') + '/'):
            return

        return super(HTML, self).write(src, dest, **kw)


class XML(HTML):

    ext = '.xml'


class Jinja2(HTML):
    """Transform HTML files using the Jinja2 markup language. You can inherit
    from all theme files in the theme directory."""

    ext = '.html'

    def __init__(self, conf, env):
        super(Jinja2, self).__init__(conf, env)

        self.path = mkdtemp(core.cache.cache_dir)
        self.jinja2 = utils.import_object('acrylamid.templates.jinja2.Environment')()
        self.jinja2.init([conf['theme'], ] + conf['static'], self.path)

    def generate(self, src, dest):

        for directory in self.conf['static']:
            if src.startswith(directory.rstrip('/') + '/'):
                src = src[len(directory.rstrip('/') + '/'):]

        return self.jinja2.fromfile(src).render(env=self.env, conf=self.conf)

    def clean(self):
        shutil.rmtree(self.path)


class System(Writer):

    def write(self, src, dest, force=False, dryrun=False):

        dest = dest.replace(self.ext, self.target)
        if not force and isfile(dest) and getmtime(dest) > getmtime(src):
            return event.skip(dest)

        if isinstance(self.cmd, basestring):
            self.cmd = [self.cmd, ]

        tt = time.time()
        fd, path = mkstemp(dir=core.cache.cache_dir)

        # make destination group/world-readable as other files from Acrylamid
        os.chmod(path, os.stat(path).st_mode | stat.S_IRGRP | stat.S_IROTH)

        try:
            res = helpers.system(self.cmd + [src])
        except (OSError, AcrylamidException) as e:
            if isfile(dest):
                os.unlink(dest)
            log.warn('%s: %s' % (e.__class__.__name__, e.args[0]))
        else:
            with os.fdopen(fd, 'w') as fp:
                fp.write(res)

            with io.open(path, 'rb') as fp:
                mkfile(fp, dest, ctime=time.time()-tt, force=force, dryrun=dryrun)
        finally:
            os.unlink(path)


class SASS(System):

    ext, target = '.sass', '.css'
    cmd = ['sass', ]


class SCSS(System):

    ext, target = '.scss', '.css'
    cmd = ['sass', '--scss']


class LESS(System):

    ext, target = '.less', '.css'
    cmd = ['lessc', ]


def initialize(conf, env):

    if isinstance(conf.setdefault('static', []), basestring):
        conf['static'] = [conf['static'], ]

    global __writers, __defaultwriter
    __writers = {}
    __defaultwriter = Writer(conf, env)


def compile(conf, env):
    """Copy/Compile assets to output directory.  All assets from the theme
    directory (except for templates) and static directories can be compiled or
    just copied using several built-in writers."""

    global __writers, __default

    ext_map = dict((cls.ext, cls) for cls in (
        globals()[writer] for writer in conf.static_filter
    ))

    other = [(prefix, filelist(prefix, conf['static_ignore'])) for prefix in conf['static']]
    if len(other):
        other_tmp = []
        for prefix, generator in other:
            other_tmp += [(relpath(path, prefix), prefix) for path in generator]
        other = other_tmp

    files = ((path, conf['theme']) for path in filelist(conf['theme'], conf['theme_ignore']))
    files = ((relpath(path, prefix), prefix) for path, prefix in files)
    files = ((path, prefix) for path, prefix in files if path not in env.engine.templates)

    for path, directory in chain(files, other):

        # initialize writer for extension if not already there
        _, ext = splitext(path)
        if ext in ext_map and ext not in __writers:
            __writers[ext] = ext_map[ext](conf, env)

        src, dest = join(directory, path), join(conf['output_dir'], path)
        writer = __writers.get(ext, __defaultwriter)
        writer.write(src, dest, force=env.options.force, dryrun=env.options.dryrun)

    for writer in __writers.values():
        writer.clean()
