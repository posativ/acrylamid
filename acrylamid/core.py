#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import logging
import os
import fnmatch

from acrylamid.utils import EntryList, FileEntry
log = logging.getLogger('acrylamid.core')


def handle(request):
    """This will prepare the whole thing. Dir-walks through content dir and
    try to get the timestamp (fallback to '%d.%m.%Y, %H:%M' parsing, or even
    worse: mtime). return entrylist reverse sorted by date."""

    conf = request['conf']
    env = request['env']

    request['entrylist'] = [FileEntry(e, conf) for e in filelist(request['conf'])]
    request['entrylist'] = EntryList(request['entrylist'])
    request['entrylist'].sort(key=lambda k: k.date, reverse=True)
    return request


def filelist(conf):
    """gathering all entries in entries_dir except entries_ignore via fnmatch."""

    flist = []
    for root, dirs, files in os.walk(conf['entries_dir']):
        for f in files:
            if f[0] == '.':
                continue
            path = os.path.join(root, f)
            fn = filter(lambda p: fnmatch.fnmatch(path, os.path.join(conf['entries_dir'], p)),
                        conf.get('entries_ignore', []))
            if not fn:
                flist.append(path)

    return flist
