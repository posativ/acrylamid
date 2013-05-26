# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.
#
# give update information for Acrylamid

from __future__ import print_function

import io
import re

from os.path import join, dirname

from acrylamid.lib import __file__ as PATH
from acrylamid.colors import blue, red, bold, underline
from acrylamid.helpers import memoize


def changesfor(version):
    """return CHANGES for `version` and whether it *breaks*."""

    with io.open(join(dirname(PATH), 'CHANGES'), encoding='utf-8') as fp:

        rv = []
        section, paragraph, safe = False, False, True

        for line in (line.rstrip() for line in fp if line):

            if not line:
                continue

            m = re.match(r'^(\d\.\d) \(\d{4}-\d{2}-\d{2}\)$', line)

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

    return not safe, '\n'.join(rv)


colorize = lambda text: \
    re.sub('`([^`]+)`', lambda m: bold(blue(m.group(1))).encode('utf-8'),
    re.sub('`([A-Z_*]+)`', lambda m: bold(m.group(1)).encode('utf-8'),
    re.sub('(#\d+)', lambda m: underline(m.group(1)).encode('utf-8'),
    re.sub('(breaks?)', lambda m: red(bold(m.group(1))).encode('utf-8'), text))))


def breaks(env, firstrun):
    """Return whether the new version may break current configuration and print
    all changes between the current and new version."""

    version = memoize('version') or (0, 4)
    if version >= (env.version.major, env.version.minor):
        return False

    memoize('version', (env.version.major, env.version.minor))

    if firstrun:
        return False

    broken = False

    for major in range(version[0], env.version.major or 1):
        for minor in range(version[1], env.version.minor):
            rv, hints = changesfor('%i.%i' % (major, minor + 1))
            broken = broken or rv

            if not hints:
                continue

            print()
            print((blue('Acrylamid') + ' %i.%s' % (major, minor+1) + u' – changes').encode('utf-8'), end="")

            if broken:
                print((u'– ' + red('may break something.')).encode('utf-8'))
            else:
                print()

            print()
            print(colorize(hints).encode('utf-8'))
            print()

    return broken
