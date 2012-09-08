# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import io

from os.path import join, relpath, isfile, getmtime, splitext

from acrylamid import readers, utils
from acrylamid.helpers import mkfile, event

__writers = None
__defaultwriter = None

__ext_map = {
    # '.sass': 'acrylamid.assets.SASSWriter',
    # '.less': 'acrylamid.assets.LESSWriter',
    # '.haml': 'acrylamid.assets.HAMLWriter',
    # ...
}


class DefaultWriter(object):

    def write(self, src, dest, force=False, dryrun=False):

        if not force and isfile(dest) and getmtime(dest) > getmtime(src):
            return event.skip(dest)

        with io.open(src, 'rb') as fp:
            mkfile(fp, dest, force=force, dryrun=dryrun, mode="b")


def initialize(conf, env):

    global __writers, __defaultwriter
    __writers = {}
    __defaultwriter = DefaultWriter()


def compile(conf, env):
    """Copy or compile assets to output directory.  If an asset is used as template, it
    won't be copied to the output directory. All assets are tracked by the event object
    and should not be removed during `acrylamid clean`."""

    global __writers, __default

    files = (relpath(path, conf['theme']) for path in readers.filelist(conf['theme']))
    files = (f for f in files if f not in env.engine.templates)

    for path in files:

        # initialize writer for extension if not already there
        _, ext = splitext(path)
        if ext in __ext_map and ext not in __writers:
            __writers[ext] = utils.import_object(__ext_map[ext])()

        src, dest = join(conf['theme'], path), join(conf['output_dir'], path)
        writer = __writers.get(ext, __defaultwriter)
        writer.write(src, dest, force=env.options.force, dryrun=env.options.dryrun)
