# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import os
import datetime
import argparse

from math import ceil
from time import localtime, strftime
from os.path import join, getmtime
from itertools import izip_longest as izip

from acrylamid import readers, commands
from acrylamid.core import cache
from acrylamid.utils import batch, force_unicode as u
from acrylamid.tasks import task, argument
from acrylamid.colors import white, blue, green, normal
from acrylamid.views.tag import fetch


class Gitlike(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):

        namespace.max = 10 * namespace.max + int(option_string.strip('-'))


option = lambda i: argument('-%i' % i, action=Gitlike, help=argparse.SUPPRESS,
    nargs=0, dest="max", default=0)
arguments = [
    argument("type", nargs="?", type=str, choices=["summary", "tags"],
        default="summary", help="info about given type (default: summary)"),
    argument("--coverage", type=int, default=None, dest="coverage",
        metavar="N", help="discover posts with uncommon tags")
] + [option(i) for i in range(10)]


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


def do_summary(conf, env, options):

    limit = options.max if options.max > 0 else 5
    entrylist, pages, translations, drafts = readers.load(conf)

    entrylist = sorted(entrylist + translations + drafts,
        key=lambda k: k.date, reverse=True)

    print
    print 'Acrylamid', blue(env['version']) + ',',
    print 'cache size:', blue('%0.2f' % (cache.size / 1024.0**2)) + ' mb'
    print

    for entry in entrylist[:limit]:
        print '  ', green(ago(entry.date.replace(tzinfo=None)).ljust(13)),
        print white(entry.title) if entry.draft else normal(entry.title)

    print
    print '%s published,' % blue(len([e for e in entrylist if not e.draft])),
    print '%s drafted articles' % blue(len([e for e in entrylist if e.draft]))

    time = localtime(getmtime(join(conf.get('cache_dir', '.cache/'), 'info')))
    print 'last compilation at %s' % blue(u(strftime(u'%d. %B %Y, %H:%M', time)))


# This function was written by Alex Martelli
# -- http://stackoverflow.com/questions/1396820/
def colprint(table, totwidth):
    """Print the table in terminal taking care of wrapping/alignment

    - `table`:    A table of strings. Elements must not be `None`
    """
    if not table:
        return
    numcols = max(len(row) for row in table)
    # ensure all rows have >= numcols columns, maybe empty
    padded = [row+numcols*('',) for row in table]
    # compute col widths, including separating space (except for last one)
    widths = [1 + max(len(x) for x in column) for column in zip(*padded)]
    widths[-1] -= 1
    # drop or truncate columns from the right in order to fit
    while sum(widths) > totwidth:
        mustlose = sum(widths) - totwidth
        if widths[-1] <= mustlose:
            del widths[-1]
        else:
            widths[-1] -= mustlose
            break
    # and finally, the output phase!
    for row in padded:
        s = ''.join(['%*s' % (-w, i[:w])
                     for w, i in zip(widths, row)])
        print s.encode('utf-8')

def do_tags(conf, env, options):

    limit = options.max if options.max > 0 else 100
    entrylist = readers.load(conf)[0]

    if options.coverage:
        for tag, entries in sorted(fetch(entrylist).iteritems()):
            if len(entries) <= options.coverage:
                print blue(tag).encode('utf-8'),
                print ', '.join(e.filename.encode('utf-8') for e in entries)
        return

    tags = ['%i %s' % (len(value), key) for key, value in
        sorted(fetch(entrylist).iteritems(), key=lambda k: len(k[1]), reverse=True)]

    colprint(
        list(izip(*list(batch(tags[:limit], ceil(len(tags)/4.0))), fillvalue='')),
        os.popen('stty size', 'r').read().split()[1]
    )


@task('info', arguments=arguments, help="short summary")
def run(conf, env, options):
    """Subcommand: info -- a short overview of a blog."""

    commands.initialize(conf, env)

    if options.type == "summary":
        do_summary(conf, env, options)
    elif options.type == "tags":
        do_tags(conf, env, options)
