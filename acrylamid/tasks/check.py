# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import io
import re
import time
import random
import collections

from urllib import quote
from xml.sax.saxutils import unescape

from acrylamid import readers, helpers
from acrylamid.tasks import task, argument
from acrylamid.colors import green, yellow, red, blue, white

from acrylamid.lib.async import Threadpool
from acrylamid.lib.requests import get, head, HTTPError, URLError

arguments = [
    argument("action", nargs="?", choices=["W3C", "links"], default="W3C",
        help="check action (default: W3C compatibility)"),
    argument("-r", "--random", dest="random", action="store_true", default=False,
        help="random order"),
    argument("-s", type=float, default=0.2, dest="sleep",
        help="seconds between requests (default 0.2)"),
    argument("-w", action="store_true", default=False, dest="warn",
        help="show W3C warnings"),
    argument("-j", "--jobs", dest="jobs", type=int, default=10, help="N parallel requests"),
]


def w3c(paths, conf, warn=False, sleep=0.2):
    """Validate HTML by using the validator.w3.org API.

    :param paths: a list of HTML files we map to our actual domain
    :param conf: configuration
    :param warn: don't handle warnings as success when set
    :param sleep: sleep between requests (be nice to their API)"""

    for path in paths:
        url = path[len(conf['output_dir'])-1:]

        resp = head("http://validator.w3.org/check?uri=" + \
            helpers.joinurl(conf['www_root'], quote(url)))

        print helpers.rchop(url, 'index.html'),

        if resp.code != 200:
            print red('not 200 Ok!')
            continue

        headers = resp.info()
        if headers['x-w3c-validator-status'] == "Abort":
            print red("Abort")
        elif headers['x-w3c-validator-status'] == 'Valid':
            if int(headers['x-w3c-validator-warnings']) == 0:
                print green('Ok')
            else:
                if warn:
                    print yellow(headers['x-w3c-validator-warnings'] + ' warns')
                else:
                    print green('Ok')
        else:
            res = headers['x-w3c-validator-errors'] + ' errors, ' + \
                  headers['x-w3c-validator-warnings'] + ' warns'
            print red(res)

        time.sleep(sleep)


def validate(paths, jobs):
    """Validates a list of urls using up to N threads.

    :param paths: a list of HTML files where we search for a-href's
    :param jobs: numbers of threads used to send I/O requests"""

    ahref = re.compile(r'<a [^>]*href="([^"]+)"[^>]*>.*?</a>')
    visited, urls = set(), collections.defaultdict(list)

    def check(url, path):
        """A HEAD request to URL.  If HEAD is not allowed, we try GET."""

        try:
            get(url, timeout=10)
        except HTTPError as e:
            if e.code == 405:
                try:
                    get(url, path, 'GET', True)
                except URLError as e:
                    print '  ' + yellow(e.reason), url
                    print white('  -- ' + path)
            else:
                print '  ' + red(e.code), url
                print white('  -- ' + path)
        except URLError as e:
            print '  ' + yellow(e.reason), url
            print white('  -- ' + path)

    # -- validation
    for path in paths:

        with io.open(path, 'r') as fp:
            data = fp.read()

        for match in ahref.finditer(data):
            a = match.group(1)
            if a.startswith(('http://', 'https://')):
                if a not in visited:
                    visited.add(a)
                    urls[path].append(a)

    print
    print "Trying", blue(len(visited)), "links..."
    print

    pool = Threadpool(jobs)
    for path in urls:
        for url in urls[path]:
            pool.add_task(check, *[unescape(url), path])

    try:
        pool.wait_completion()
    except KeyboardInterrupt:
        sys.exit(1)


@task('check', arguments, "run W3C or validate links")
def run(conf, env, options):
    """Subcommand: check -- run W3C over generated output and check destination
    of linked items"""

    paths = [path for path in readers.filelist(conf['output_dir']) if path.endswith('.html')]

    if options.random:
        random.shuffle(paths)

    if options.action == 'W3C':
        w3c(paths, conf, warn=options.warn, sleep=options.sleep)
    else:
        validate(paths, options.jobs)
