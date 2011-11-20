#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import logging
import os
import fnmatch
import time
from datetime import datetime

from acrylamid.utils import FileEntry
log = logging.getLogger('acrylamid.core')
    

def start(request):
    return request
    

def handle(request):
    """This is the acrylamid handle:
        - generate filelist
        - sort filelist by date"""
        
    conf = request['conf']

    # generate a list of entries
    request['entrylist'] = filelist(request)

    for i,entry in enumerate(request['entrylist']):
        # convert mtime timestamp or `date:` to localtime (float), required for sort
        if isinstance(entry.date, basestring):
            timestamp = time.mktime(time.strptime(entry.date,
                conf.get('strptime', '%d.%m.%Y, %H:%M')))
            entry.date = datetime.fromtimestamp(timestamp)
        else:
            log.warn("using mtime from %s" % entry)
    
    request['entrylist'].sort(key=lambda k: k.date, reverse=True)
    return request


def filelist(request):
    """This is the default handler for getting entries.  It takes the
    request object in and figures out which entries bases on the default
    behavior that we want to show and generates a list of EntryBase
    subclass objects which it returns.
    
    Arguments:
    args -- dict containing the incoming Request object
    
    Returns the content we want to render"""
    
    conf = request['conf']
    
    filelist = []
    for root, dirs, files in os.walk(conf['entries_dir']):
        for file in files:
            path = os.path.join(root, file)
            fn = filter(lambda p: fnmatch.fnmatch(path, os.path.join(conf['entries_dir'], p)),
                        conf.get('entries_ignore', []))
            if not fn:
                filelist.append(path)
    
    entrylist = [FileEntry(e) for e in filelist]
    return entrylist
