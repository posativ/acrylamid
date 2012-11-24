# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# give update information for Acrylamid


import io
import re
import textwrap

from os.path import join, dirname

import acrylamid

from acrylamid.colors import blue, red, bold, underline
from acrylamid.helpers import memoize


def changesfor(version):

    with io.open(join(dirname(acrylamid.__file__), '../', 'CHANGES.md')) as fp:

        rv = []
        section, paragraph, safe = False, False, True

        for line in (line.rstrip() for line in fp if line):

            if not line:
                continue

            m = re.match('^version (\d\.\d)$', line, re.IGNORECASE)

            if m:
                section = m.group(1) == version
                continue

            if section and line.startswith('### '):
                paragraph = 'changes' in line
                continue

            if section and paragraph:
                rv.append(line)
                if 'break' in line:
                    safe = False

    return safe, '\n'.join(rv)


colorize = lambda text: \
    re.sub('`([^`]+)`', lambda m: bold(blue(m.group(1))).encode('utf-8'),
    re.sub('`([A-Z_*]+)`', lambda m: bold(m.group(1)).encode('utf-8'),
    re.sub('(#\d+)', lambda m: underline(m.group(1)).encode('utf-8'),
    re.sub('(breaks?)', lambda m: red(m.group(1)).encode('utf-8'), text))))


def check(env, firstrun):
    """Return whether the new version is compatible/safe with the last and
    print all changes between the current and new version."""

    version = memoize('version') or (0, 4)
    if version >= (env.version.major, env.version.minor):
        return True

    memoize('version', (env.version.major, env.version.minor, env.version.patch))

    if firstrun:
        return True

    safe = True
    print

    for major in range(version[0], env.version.major or 1):
        for minor in range(version[1], env.version.minor):
            broken, hints = changesfor('%i.%i' % (major, minor + 1))
            safe = min(broken, safe)

            print (blue('acrylamid') + ' %i.%s' % (major, minor+1) + u' – changes').encode('utf-8'),

            if not safe:
                print (u'– ' + red('may break something.')).encode('utf-8')
            else:
                print

            print
            print colorize(hints).encode('utf-8')
            print

    return safe
