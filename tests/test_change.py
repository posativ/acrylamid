# -*- coding: utf-8 -*-

import sys; reload(sys)
sys.setdefaultencoding('utf-8')

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA

import os
import re

import shutil
import subprocess
import tempfile
import time
import random

from os.path import join, isfile
from datetime import datetime, timedelta

try:
    from subprocess import check_output
except ImportError:
    def check_output(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocessCalledProcessError(retcode, cmd, output=output)
        return output

one = lambda iterable: len(filter(lambda k: k, iterable)) == 1


def touch(path, delta=''):
    """A crossplattform UNIX touch."""

    def parse(input):
        # http://blog.posativ.org/2011/parsing-human-readable-timedeltas-in-python/
        keys = ["weeks", "days", "hours", "minutes", "seconds"]
        regex = "".join(["((?P<%s>\d+)%s ?)?" % (k, k[0]) for k in keys])
        kwargs = {}
        for k,v in re.match(regex, input).groupdict(default="0").items():
            kwargs[k] = int(v)
        return timedelta(**kwargs)

    timestamp = datetime.fromtimestamp(os.stat(path).st_mtime)

    if delta.startswith('+'):
        timestamp += parse(delta[1:])
    elif delta.startswith('-'):
        timestamp -= parse(delta[1:])

    os.utime(path, (time.mktime(timestamp.timetuple()),)*2)
    return os.stat(path).st_mtime


class TestTouch(unittest.TestCase):

    def setUp(self):
        fd, self.path = tempfile.mkstemp()
        with os.fdopen(fd, 'wb') as fp:
            fp.write('Foo\n')

    def test_touch(self):

        ts = os.stat(self.path).st_mtime
        self.assertEquals(ts, touch(self.path))

        self.assertTrue(ts < touch(self.path, '+3s'))
        self.assertTrue(ts < touch(self.path, '+5m 57s'))
        self.assertAlmostEqual(ts, touch(self.path, '-6m'))

    def tearDown(self):
        os.remove(self.path)


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.path = tempfile.mkdtemp(dir='.')
        subprocess.check_call(['acrylamid', 'init', '-q', self.path])
        os.chdir(self.path)
        subprocess.check_call(['acrylamid', 'compile', '-qC'])

    def shortcut(self, cmd, regex, func=any):
        out = check_output(cmd).strip('\x1b[?1034h')  # XXX my OS X/Terminal fault?
        regex = re.compile('^\s*'+ regex)

        for line in out.split('\n')[:-2]:
            print `line`
        print regex.pattern

        self.assertTrue(func(regex.match(line) for line in out.split('\n')[:-2]))

    def test_content(self):

        # recompilation should skip through everything
        # there's a weird invisible character in front
        self.shortcut(['acrylamid', 'compile', '-C'], 'skip', all) # should be all

        # change mtime should result result in at least one identical
        touch('content/sample-entry.txt', '+5s')
        self.shortcut(['acrylamid', 'compile', '-C'], 'skip', one)

        # change content should result in at least on change
        subprocess.check_call(['sed', '-i', '-e', 's/i/u/g', 'content/sample-entry.txt'])
        self.shortcut(['acrylamid', 'compile', '-C'], 'create', any)

        # create
        subprocess.check_call(['acrylamid', 'new', '-q', 'Spam'])
        self.shortcut(['acrylamid', 'compile', '-C'], 'skip')

    def test_layout_independent(self):

        # clean, cached start
        self.shortcut(['acrylamid', 'compile', '-C'], 'skip', all)

        for path in ['layouts/articles.html', 'layouts/entry.html',
                     'layouts/rss.xml', 'layouts/atom.xml']:
            touch(path, '+%is' % random.randint(5, 100))

        self.shortcut(['acrylamid', 'compile', '-C'], 'identical', all)

    def test_layout_single(self):

        # still working?
        self.shortcut(['acrylamid', 'compile', '-C'], 'skip', all)

        # change a single independent layout
        touch('layouts/rss.xml', '+5s')
        self.shortcut(['acrylamid', 'compile', '-C'], 'identical', one)

    def test_layout_base1(self):

        # working?
        self.shortcut(['acrylamid', 'compile', '-C'], 'skip', all)

        # change the base layout (and feed xml for a more easy check)
        for path in ['layouts/base.html', 'layouts/rss.xml', 'layouts/atom.xml']:
            touch(path, '+%is' % random.randint(5, 100))
        self.shortcut(['acrylamid', 'compile', '-C'], 'identical',  all)

    def test_layout_base2(self):

        # one identical means only the articles view has changed, but the others must too
        touch('layouts/base.html', '+5s')
        self.shortcut(['acrylamid', 'compile', '-C'], 'identical',  lambda x: not one(x))

    def test_layout_base3(self):

        with open('layouts/base.html', 'a') as fp:
            fp.write('foo\n')
        touch('layouts/base.html', '+5s')

        # this should exclude rss/atom.xml because they do not rely on base.html
        self.shortcut(['acrylamid', 'compile', '-C'], 'update',
                      lambda x: not one(x) and not any(x))

    def tearDown(self):
        os.chdir('../')
        shutil.rmtree(self.path)
