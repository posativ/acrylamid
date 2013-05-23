# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import sys
import io
import os
import tempfile
import subprocess
import shutil

from os.path import join, dirname, isfile
from datetime import datetime

from acrylamid import log, readers, commands
from acrylamid.errors import AcrylamidException

from acrylamid.tasks import task, argument
from acrylamid.utils import force_unicode as u
from acrylamid.helpers import safe, event

yaml, rst, md = \
    lambda title, date: u"---\ntitle: %s\ndate: %s\n---\n\n" % (safe(title), date), \
    lambda title, date: u"%s\n" % title + "="*len(title) + '\n\n' + ":date: %s\n\n" % date, \
    lambda title, date: u"Title: %s\nDate: %s\n\n" % (title, date)

formats = {'.md': md, '.mkdown': md, '.rst': rst, '.rest': rst}


@task('new', [argument("title", nargs="*", default=None)], help="create a new entry")
def run(conf, env, options):
    """Subcommand: new -- create a new blog entry the easy way.  Either run
    ``acrylamid new My fresh new Entry`` or interactively via ``acrylamid new``
    and the file will be created using the preferred permalink format."""

    # we need the actual default values
    commands.initialize(conf, env)

    ext = conf.get('content_extension', '.txt')
    fd, tmp = tempfile.mkstemp(suffix=ext, dir='.cache/')

    editor = os.getenv('VISUAL') if os.getenv('VISUAL') else os.getenv('EDITOR')
    tt = formats.get(ext, yaml)

    if options.title:
        title = u(' '.join(options.title))
    else:
        title = u(raw_input("Entry's title: "))

    with io.open(fd, 'w', encoding='utf-8') as f:
        f.write(tt(title, datetime.now().strftime(conf['date_format'])))

    entry = readers.Entry(tmp, conf)
    p = join(conf['content_dir'], dirname(entry.permalink)[1:])

    try:
        os.makedirs(p.rsplit('/', 1)[0])
    except OSError:
        pass

    filepath = p + ext
    if isfile(filepath):
        raise AcrylamidException('Entry already exists %r' % filepath)
    shutil.move(tmp, filepath)
    event.create('new', filepath)

    if datetime.now().hour == 23 and datetime.now().minute > 45:
        log.info("notice  don't forget to update entry.date-day after mignight!")

    if log.level() >= log.WARN:
        return

    try:
        if editor:
            retcode = subprocess.call(editor.split() + [filepath])
        elif sys.platform == 'darwin':
            retcode = subprocess.call(['open', filepath])
        else:
            retcode = subprocess.call(['xdg-open', filepath])
    except OSError:
        raise AcrylamidException('Could not launch an editor')

    # XXX process detaches... m(
    if retcode < 0:
        raise AcrylamidException('Child was terminated by signal %i' % -retcode)

    if os.stat(filepath)[6] == 0:
        raise AcrylamidException('File is empty!')
