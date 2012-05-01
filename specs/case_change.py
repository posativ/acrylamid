# -*- coding: utf-8 -*-

import konira

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
            raise subprocess.CalledProcessError(retcode, cmd, output=output)
        return output

one = lambda iterable: len(filter(lambda k: k, iterable)) == 1


def touch(path, delta='', reset=False):
    """A crossplattform UNIX touch."""

    def parse(input):
        # http://blog.posativ.org/2011/parsing-human-readable-timedeltas-in-python/
        keys = ["weeks", "days", "hours", "minutes", "seconds"]
        regex = "".join(["((?P<%s>\d+)%s ?)?" % (k, k[0]) for k in keys])
        kwargs = {}
        for k,v in re.match(regex, input).groupdict(default="0").items():
            kwargs[k] = int(v)
        return timedelta(**kwargs)

    if reset:
        timestamp = datetime.now()
    else:
        timestamp = datetime.fromtimestamp(os.stat(path).st_mtime)

    if delta.startswith('+'):
        timestamp += parse(delta[1:])
    elif delta.startswith('-'):
        timestamp -= parse(delta[1:])

    os.utime(path, (time.mktime(timestamp.timetuple()),)*2)
    return os.stat(path).st_mtime


def run(cmd):
    output = check_output(cmd).strip('\x1b[?1034h')  # XXX my OS X/Terminal fault?
    return output.split('\n')[:-2]


describe 'our touch works':

    before all:
        fd, self.path = tempfile.mkstemp()
        with os.fdopen(fd, 'wb') as fp:
            fp.write('Foo\n')

    it "works":
        ts = os.stat(self.path).st_mtime
        assert ts == touch(self.path)

        assert ts < touch(self.path, '+3s')
        assert ts < touch(self.path, '+5m 57s')
        assert ts == touch(self.path, '-6m')

    after all:
        os.remove(self.path)


describe 'emulate changes to content':

    before all:
        self.path = tempfile.mkdtemp(dir='.')
        subprocess.check_call(['acrylamid', 'init', '-q', self.path])
        os.chdir(self.path)
        subprocess.check_call(['acrylamid', 'compile', '-qC'])

    it '1 should skip through when we make no changes':

        assert all(filter(lambda line: 'skip' in line, run(['acrylamid', 'compile', '-C'])))

    it '2 modify mtime but it stays identical and articles view skips':

        touch('content/sample-entry.txt', '+5s')
        output = run(['acrylamid', 'compile', '-C'])
        touch('content/sample-entry.txt', reset=True)

        assert one(filter(lambda line: 'skip' in line, output))
        assert any(filter(lambda line: 'identical' in line, output))

    it '3 updates a file if we change add some words':

        time.sleep(1.1)
        with open('content/sample-entry.txt', 'a') as fp:
            fp.write('Test.')

        assert any(filter(lambda line: 'update' in line, run(['acrylamid', 'compile', '-C'])))

    it '4 should do incremental updates when we add a new entry':

        subprocess.check_call(['acrylamid', 'new', '-q', 'Spam'])
        output = run(['acrylamid', 'compile', '-C'])

        assert any(filter(lambda line: 'skip' in line, output))
        assert any(filter(lambda line: 'create' in line, output))
        assert any(filter(lambda line: 'update' in line, output))


    after all:
        os.chdir('../')
        shutil.rmtree(self.path)


describe 'emulate changes to layouts':

    before all:
        self.path = tempfile.mkdtemp(dir='.')
        subprocess.check_call(['acrylamid', 'init', '-q', self.path])
        os.chdir(self.path)
        subprocess.check_call(['acrylamid', 'compile', '-qC'])

    it 'should stay identical':

        lst = ['layouts/articles.html', 'layouts/entry.html',
               'layouts/rss.xml', 'layouts/atom.xml']

        for path in lst:
            touch(path, '+%is' % random.randint(5, 100))
        assert all(filter(lambda line: 'identical' in line, run(['acrylamid', 'compile', '-C'])))

        # reset every timestamp
        for path in lst:
            touch(path, reset=True)

    it 'touch a parent template should affect all inherited templates':

        touch('layouts/base.html', '+5s')
        assert filter(lambda line: 'identical' in line, run(['acrylamid', 'compile', '-C'])) != 1
        touch('layouts/base.html', reset=True)

    it 'updates a single independent layout but the others not':

        touch('layouts/rss.xml', '+5s')
        output = run(['acrylamid', 'compile', '-C'])
        touch('layouts/rss.xml', reset=True)

        assert len(filter(lambda line: 'skip' in line, output)) == len(output) - 1
        assert len(filter(lambda line: 'identical' in line, output)) == 1

    it 'does not update atom and rss if we change the base template':

        with open('layouts/base.html', 'a') as fp:
            fp.write('foo\n')

        touch('layouts/base.html', '+5s')
        output = run(['acrylamid', 'compile', '-C'])
        touch('layouts/base.html', reset=True)

        assert len(filter(lambda line: 'update' in line, output)) == len(output) - 2
        assert len(filter(lambda line: 'skip' in line, output)) == 2

    after all:
        os.chdir('../')
        shutil.rmtree(self.path)
