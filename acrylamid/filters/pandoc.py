# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid.filters import Filter
from acrylamid.helpers import system
from acrylamid.errors import AcrylamidException


class Pandoc(Filter):

    match = ['Pandoc', 'pandoc']
    version = '1.0.0'

    conflicts = ['Markdown', 'reStructuredText', 'HTML']
    priority = 70.0

    def init(self, conf, env):
        self.ignore = env.options.ignore

    def transform(self, text, entry, *args):

        try:
            system(['which', 'pandoc'])
        except AcrylamidException:
            if self.ignore:
                return text
            raise AcrylamidException('Pandoc: pandoc not available')

        if len(args) == 0:
            raise AcrylamidException("pandoc filter takes one or more arguments")

        fmt, extras = args[0], args[1:]
        cmd = ['pandoc', '-f', fmt, '-t', 'HTML']
        cmd.extend(['--'+x for x in extras])

        try:
            return system(cmd, stdin=text)
        except OSError as e:
            raise AcrylamidException(e.msg)
