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
        help="use the Jinja2 template engine (default)")
]


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

    If you need to restore single files, remove the existing file and run::

        $ acrylamid init path/to/blog/

    and all missing files are automatically re-created."""

    if not options.engine:
        try:
            import jinja2
            options.engine = 'jinja2'
        except ImportError:
            options.engine = 'mako'

    root = options.dest
    theme, files = rollout(options.theme, options.engine)

    # remember whether we are restore an existing theme
    restore = isfile(join(root, 'conf.py'))

    if isfile(root):
        raise AcrylamidException("%s already exists!" % root)

    if isdir(root) and len(os.listdir(root)) > 0 and not options.overwrite:
        if not restore and raw_input("Destination directory not empty! Continue? [yn]: ") != 'y':
            sys.exit(1)

    if 'conf.py' not in files:
        conf = string.Template(defaults.copy('conf.py').read())
        files['conf.py'] = io.BytesIO(conf.substitute(engine=options.engine,
                                                      theme=theme).encode('utf-8'))

    for dest, items in files.iteritems():
        dest = join(root, dest)

        if not isdir(dirname(dest)):
            os.makedirs(dirname(dest))

        if isinstance(items, (basestring, io.IOBase)):
            items = [items, ]

        for obj in items:
            if hasattr(obj, 'read'):
                path = join(dirname(dest), basename(obj.name)) if dest.endswith('/') else dest
                if options.overwrite or not exists(path):
                    with io.open(path, 'wb') as fp:
                        fp.write(obj.read())
                    event.create(path)
                else:
                    event.skip(path)
            else:
                src = join(dirname(defaults.__file__), options.theme, options.engine, obj)
                if options.overwrite or not exists(join(dest, basename(src))):
                    shutil.copy(src, dest)
                    event.create(dest if basename(dest) else join(dest, obj))
                else:
                    event.skip(dest)

    if not restore:
        log.info('Created your fresh new blog at %r. Enjoy!', root)
