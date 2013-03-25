# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import os
import io
import re
import time
import stat

from tempfile import mkstemp
from functools import partial
from collections import defaultdict
from os.path import join, isfile, getmtime, split, splitext

from acrylamid import core, helpers, log
from acrylamid.errors import AcrylamidException
from acrylamid.helpers import mkfile, event
from acrylamid.readers import relfilelist

ns = "assets"

__writers = None
__defaultwriter = None


class Writer(object):
    """A 'open-file-and-write-to-dest' writer.  Only operates if the source
    file has been modified or the destination does not exists."""

    uses = None

    def __init__(self, conf, env):
        self.conf = conf
        self.env = env

    def filter(self, input, directory):
        """Filter input set for includes and imports using `uses` pattern.
        The pattern must include a group 'file' that holds the included item.
        If the pattern is the empty string (the default), return input.

        Note, that Acrylamid will only read the first 512 bytes of a file
        to check for includes. Therefore, do not move your includes to the
        end of file."""

        if not self.uses:
            return input

        imports = set()
        for path in input:
            with io.open(join(directory, path)) as fp:
                text = fp.read(512)

            for m in re.finditer(self.uses, text, re.MULTILINE):
                imports.add(m.group('file'))

        return input.difference(imports)

    def modified(self, src, dest):
        return not isfile(dest) or getmtime(src) > getmtime(dest)

    def generate(self, src, dest):
        return io.open(src, 'rb')

    def write(self, src, dest, force=False, dryrun=False):
        if not force and not self.modified(src, dest):
            return event.skip(ns, dest)

        mkfile(self.generate(src, dest), dest, ns=ns, force=force, dryrun=dryrun)

    def shutdown(self):
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


class Template(HTML):
    """Transform HTML files using the current markup engine. You can inherit
    from all theme files inside the theme directory."""

    def __init__(self, conf, env):
        env.engine.extend(conf['static'])
        super(Template, self).__init__(conf, env)

    def modified(self, src, dest):
        return super(Template, self).modified(src, dest) or self.env.modified

    def generate(self, src, dest):
        relpath = split(src[::-1])[0][::-1]  # (head, tail) but reversed behavior
        return self.env.engine.fromfile(relpath).render(env=self.env, conf=self.conf)

    def write(self, src, dest, force=False, dryrun=False):
        dest = dest.replace(splitext(src)[-1], self.target)
        return super(Template, self).write(src, dest, force=force, dryrun=dryrun)

    @property
    def ext(self):
        return tuple(self.env.engine.extension)

    target = '.html'


class System(Writer):

    def write(self, src, dest, force=False, dryrun=False):

        dest = dest.replace(splitext(src)[-1], self.target)

        if not force and isfile(dest) and getmtime(dest) > getmtime(src):
            return event.skip(ns, dest)

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
            log.exception('%s: %s' % (e.__class__.__name__, e.args[0]))
        else:
            with os.fdopen(fd, 'w') as fp:
                fp.write(res)

            with io.open(path, 'rb') as fp:
                mkfile(fp, dest, time.time()-tt, ns, force, dryrun)
        finally:
            os.unlink(path)


class SASS(System):

    ext, target = '.sass', '.css'
    cmd = ['sass', ]

    # matches @import 'foo.sass' (and optionally without quotes)
    uses = r'^@import ["\']?(?P<file>.+?\.sass)["\']?'


class SCSS(System):

    ext, target = '.scss', '.css'
    cmd = ['sass', '--scss']

    # matches @import 'foo.scss', we do not support import 'foo'; or url(foo);
    uses = r'^@import ["\'](?P<file>.+?\.scss)["\'];'


class LESS(System):

    ext, target = '.less', '.css'
    cmd = ['lessc', ]

    # matches @import 'foo.less'; and @import-once ...
    uses = r'^@import(-once)? ["\'](?P<file>.+?\.less)["\'];'


class CoffeeScript(System):

    ext, target = '.coffee', '.js'
    cmd = ['coffee', '-cp']


class IcedCoffeeScript(System):

    ext, target = ['.iced', '.coffee'], '.js'
    cmd = ['iced', '-cp']


def worker(conf, env, args):
    """Compile each file extension for each folder in its own process.
    """
    (ext, directory), items = args[0], args[1]
    writer = __writers.get(ext, __defaultwriter)

    for path in writer.filter(items, directory):
        src, dest = join(directory, path), join(conf['output_dir'], path)
        writer.write(src, dest, force=env.options.force, dryrun=env.options.dryrun)


def compile(conf, env):
    """Copy/Compile assets to output directory.  All assets from the theme
    directory (except for templates) and static directories can be compiled or
    just copied using several built-in writers."""

    global __writers, __defaultwriter
    __writers = {}
    __defaultwriter = Writer(conf, env)

    files = defaultdict(set)

    for cls in [globals()[writer](conf, env) for writer in conf.static_filter]:
        if isinstance(cls.ext, (list, tuple)):
            for ext in cls.ext:
                __writers[ext] = cls
        else:
            __writers[cls.ext] = cls

    for path, directory in relfilelist(conf['theme'], conf['theme_ignore'], env.engine.templates):
        files[(splitext(path)[1], directory)].add(path)

    for path, directory in relfilelist(conf['static'], conf['static_ignore']):
        files[(splitext(path)[1], directory)].add(path)

    map(partial(worker, conf, env), files.iteritems())
