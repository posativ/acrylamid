# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from __future__ import unicode_literals

import sys
import os
import io
import imp
import shutil
import string

from os.path import exists, isfile, isdir, join, dirname, basename

from acrylamid import log, defaults
from acrylamid import AcrylamidException
from acrylamid.tasks import task, argument
from acrylamid.helpers import event

arguments = [
    argument("dest", metavar="DEST|FILE", nargs="?", default="."),
    argument("-f", "--force", action="store_true", dest="overwrite",
        help="don't ask, just overwrite", default=False),
    argument("--theme", dest="theme", default="html5",
        help="use theme (minimalistic HTML5 per default)"),
    argument("--mako", action="store_const", dest="engine", const="mako",
        help="use the Mako template engine", default=""),
    argument("--jinja2", action="store_const", dest="engine", const="jinja2",
        help="use the Jinja2 template engine")
]


def resolve(options, theme, files):
    """Takes a files dictionary and yields src and full destination path.

    :param options: Argparse namespace object
    :param theme: theme directory name
    :param files: {'/path/': [item, ...]}"""

    if 'conf.py' not in files:
        conf = string.Template(defaults.copy('conf.py').read())
        files['conf.py'] = io.BytesIO(conf.substitute(engine=options.engine,
                                                      theme=theme).encode('utf-8'))

    for path, items in files.iteritems():
        path = join(options.dest, path)

        if isinstance(items, (basestring, io.IOBase)):
            items = [items, ]

        for obj in items:
            if hasattr(obj, 'read'):
                dest = join(path, basename(obj.name)) if path.endswith('/') else path
                yield obj, dest
            else:
                obj = join(dirname(defaults.__file__), options.theme, options.engine, obj)
                yield obj, join(dirname(path), basename(obj))


def write(obj, dest):
    if hasattr(obj, 'read'):
        with io.open(dest, 'wb') as fp:
            fp.write(obj.read())
    else:
        shutil.copy(obj, dest)


def rollout(name, engine):
    """A helper to ship custom themes.  Your theme must provide a ``__init__.py``
    that contains a :func:`rollout` function that returns the theme directory
    name as well as a dictionary of files."""

    directory = join(dirname(defaults.__file__), name)

    if not isdir(directory):
        raise AcrylamidException("no such theme %r" % name)

    if not isdir(join(directory, engine)):
        raise AcrylamidException("theme is not available for %r" % engine)

    try:
        if isfile(join(directory, engine, '__init__.py')):
            fp, path, descr = imp.find_module(engine, [directory])
        else:
            # try parent directory
            fp, path, descr = imp.find_module(name, [dirname(defaults.__file__)])
        mod = imp.load_module(engine, fp, path, descr)
    except (ImportError, Exception) as e:
        raise AcrylamidException(unicode(e))

    return mod.rollout(engine)


@task('init', arguments, help='initializes base structure in PATH')
def init(env, options):
    """Subcommand: init -- create the base structure of an Acrylamid blog
    or restore individual files and folders.

    If the destination directory is empty, it will create a new blog. If the
    destination  directory is not empty it won't overwrite anything unless
    you supply -f, --force to re-initialize the whole theme.

    If you need to restore a single file, run

        $ cd blog && acrylamid init theme/main.html
    """

    if not options.engine:
        try:
            import jinja2
            options.engine = 'jinja2'
        except ImportError:
            options.engine = 'mako'

    theme, files = rollout(options.theme, options.engine)

    # if destination is part of theme, restore it!
    for src, dest in resolve(options, theme, files):
        if dest.endswith(options.dest):
            if (not isfile(options.dest) or options.overwrite or
                raw_input("re-initialize %s ? [yn]: " % options.dest) == 'y'):
                write(src, options.dest)
                log.info('re-initialized  ' + options.dest)
                return

    if isfile(options.dest):
        raise AcrylamidException("%s already exists!" % options.dest)

    if isdir(options.dest) and len(os.listdir(options.dest)) > 0 and not options.overwrite:
        if raw_input("Destination directory not empty! Continue? [yn]: ") != 'y':
            sys.exit(1)

    for src, dest in resolve(options, theme, files):

        if not isdir(dirname(dest)):
            os.makedirs(dirname(dest))

        if options.overwrite or not exists(dest):
            write(src, dest)
            event.create(dest)
        else:
            event.skip(dest)

    log.info('Created your fresh new blog at %r. Enjoy!', options.dest)
