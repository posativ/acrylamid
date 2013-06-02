# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import io
import re

from functools import partial
from collections import defaultdict
from os.path import join, isfile, getmtime, split, splitext

from acrylamid.compat import iteritems
from acrylamid.helpers import mkfile, event
from acrylamid.readers import relfilelist

try:
    from acrylamid.assets.web import Webassets, Bundle
except ImportError:
    from acrylamid.assets.fallback import Webassets, Bundle

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
        return self.env.engine.fromfile(self.env, relpath).render(env=self.env, conf=self.conf)

    def write(self, src, dest, force=False, dryrun=False):
        dest = dest.replace(splitext(src)[-1], self.target)
        return super(Template, self).write(src, dest, force=force, dryrun=dryrun)

    @property
    def ext(self):
        return tuple(self.env.engine.extension)

    target = '.html'


def initialize(conf, env):

    env.webassets = Webassets(conf, env)

    env.engine.globals['compile'] = env.webassets.compile
    env.engine.globals['Bundle'] = Bundle


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

    excludes = list(env.engine.templates.keys()) + env.webassets.excludes(conf['theme'])
    for path, directory in relfilelist(conf['theme'], conf['theme_ignore'], excludes):
        files[(splitext(path)[1], directory)].add(path)

    excludes = env.webassets.excludes(conf['static'] or '')
    for path, directory in relfilelist(conf['static'], conf['static_ignore'], excludes):
        files[(splitext(path)[1], directory)].add(path)

    list(map(partial(worker, conf, env), iteritems(files)))
