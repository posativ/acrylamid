# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from acrylamid.filters import Filter
from acrylamid.utils import system
from acrylamid.errors import AcrylamidException


class Pandoc(Filter):

    __name__ = 'pandoc'
    __match__ = ['Pandoc', 'pandoc']
    __conflicts__ = ['Markdown', 'reStructuredText', 'HTML']

    @classmethod
    def init(self, conf, env):

        try:
            system('pandoc', '--help')
        except OSError as e:
            raise AcrylamidException('no pandoc available')

    def transform(self, text, request, *args):

        if len(args) == 0:
            raise AcrylamidException("pandoc filter takes one or more arguments")

        fmt, extras = args[0], args[1:]
        cmd = ['pandoc', '-f', fmt, '-t', 'HTML']
        cmd.extend(['--'+x for x in extras])

        try:
            return system(cmd, stdin=text)
        except OSError as e:
            raise AcrylamidException(e.msg)
