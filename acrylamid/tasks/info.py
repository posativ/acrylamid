# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import datetime

from time import localtime, strftime
from os.path import join, getmtime
from optparse import make_option, SUPPRESS_HELP

from acrylamid import log, utils
from acrylamid.errors import AcrylamidException

from acrylamid.core import cache
from acrylamid.base import Entry
from acrylamid.commands import initialize

aliases = ('info', )
usage = "%prog " + sys.argv[1]

def count(option, opt, value, parser, result=[]):
    result.append(str(opt).strip('-'))
    parser.values.max = result

option = lambda i: make_option('-%i' % (i), action="callback", callback=count, help=SUPPRESS_HELP)
options = [option(i) for i in range(10)]

# TODO: provide a ``from acrylamid import colors`` defining those functions (unicode, type aware)

def blue(text):
	return '\033[0;34m' + str(text) + '\033[0m'


def green(text):
	return '\033[0;32m' + str(text) + '\033[0m'


def white(text):
	return '\033[0;37m' + str(text) + '\033[0m'


def red(text):
	return '\033[0;31m' + str(text) + '\033[0m'


def ago(date, now=datetime.datetime.now()):

    delta = now - date

    secs = delta.seconds
    days = delta.days

    if days == 0:
        if secs < 10:
            return "just now"
        if secs < 60:
            return str(secs) + " seconds ago"
        if secs < 120:
            return  "a minute ago"
        if secs < 3600:
            return str(secs/60) + " minutes ago"
        if secs < 7200:
            return "an hour ago"
        if secs < 86400:
            return str(secs/3600) + " hours ago"
    if days == 1:
        return "Yesterday"
    if days < 7:
        return str(days) + " days ago"
    if days < 31:
        return str(days/7) + " weeks ago"
    if days < 365:
        return str(days/30) + " months ago"

    return str(days/365) + " years ago"


def run(conf, env, args, options):
    """Subcommand: info -- a short overview of a blog."""

    limit = int(''.join(options.get('max', '5')))

    request = initialize(conf, env)
    entrylist = sorted([Entry(e, conf) for e in utils.filelist(conf['content_dir'],
                            conf.get('entries_ignore', []))], key=lambda k: k.date, reverse=True)

    print
    print 'acrylamid', blue(env['version']) + ',',
    print 'cache size:', blue('%0.2f' % (cache.size / 1024.0**2)) + ' mb'
    print

    for entry in entrylist[:limit]:
        print '  ', green(ago(entry.date).ljust(12)),
        print white(entry.title) if entry.draft else entry.title

    print
    print '%s published,' % blue(len([e for e in entrylist if not e.draft])),
    print '%s drafted articles' % blue(len([e for e in entrylist if e.draft]))

    time = localtime(getmtime(join(conf.get('cache_dir', '.cache/'), 'info')))
    print 'last compilation at %s' % blue(strftime('%d. %B %Y, %H:%M', time))
