# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import datetime
import argparse

from time import localtime, strftime
from os.path import join, getmtime

from acrylamid import readers, commands
from acrylamid.core import cache
from acrylamid.tasks import task, argument
from acrylamid.colors import white, blue, green, normal


class Gitlike(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):

        namespace.max = 10 * namespace.max + int(option_string.strip('-'))


option = lambda i: argument('-%i' % i, action=Gitlike, help=argparse.SUPPRESS,
    nargs=0, dest="max", default=0)
arguments = [option(i) for i in range(10)]


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


@task('info', arguments=arguments, help="short summary")
def run(conf, env, options):
    """Subcommand: info -- a short overview of a blog."""

    limit = options.max if options.max > 0 else 5
    commands.initialize(conf, env)
    entrylist, pages = readers.load(conf)

    print
    print 'acrylamid', blue(env['version']) + ',',
    print 'cache size:', blue('%0.2f' % (cache.size / 1024.0**2)) + ' mb'
    print

    for entry in entrylist[:limit]:
        print '  ', green(ago(entry.date.replace(tzinfo=None)).ljust(13)),
        print white(entry.title) if entry.draft else normal(entry.title)

    print
    print '%s published,' % blue(len([e for e in entrylist if not e.draft])),
    print '%s drafted articles' % blue(len([e for e in entrylist if e.draft]))

    time = localtime(getmtime(join(conf.get('cache_dir', '.cache/'), 'info')))
    print 'last compilation at %s' % blue(strftime('%d. %B %Y, %H:%M', time))
