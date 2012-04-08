#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os

from acrylamid.filters import Filter
from acrylamid.utils import cached_property


class Restructuredtext(Filter):

    match = ['restructuredtext', 'rst', 'rest', 'reST', 'reStructuredText']
    conflicts = ['markdown', 'plain']
    priority = 70.00

    def init(self, conf, env):

        self.failed = []
        self.extensions = {}
        self.ignore = env.options.ignore

    def transform(self, content, entry, *filters):

        self.filters = filters

        settings = {
            'initial_header_level': 1,
            'doctitle_xform': 0
        }

        parts = self.publish_parts(content, writer_name='html', settings_overrides=settings)
        return parts['body'].encode('utf-8')

    @cached_property
    def publish_parts(self):
        """On-demand import.  Importing reStructuredText and Pygments takes
        3/5 of overall runtime just to import."""

        from docutils.core import publish_parts
        from docutils.parsers.rst import directives

        # -- discover reStructuredText extensions --
        for mem in os.listdir(os.path.dirname(__file__)):
            if mem.startswith('rstx_') and mem.endswith('.py'):
                try:
                    mod = __import__(mem.replace('.py', ''))
                    rstx = mod.makeExtension()
                    if isinstance(mod.match, basestring):
                        self.match.append(mod.match)
                        self.extensions[mod.__name__] = rstx
                    else:
                        for name in mod.match:
                            self.extensions[name] = rstx
                except (ImportError, Exception), e:
                    self.failed.append('%r %s: %s' % (mem, e.__class__.__name__, e))

        for directive, klass in self.extensions.iteritems():
            directives.register_directive(directive, klass)

        return publish_parts
