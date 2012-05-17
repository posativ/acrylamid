#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os

from acrylamid import log
from acrylamid.errors import AcrylamidException
from acrylamid.filters import Filter
from acrylamid.filters.md import get_pygments_style

try:
    from docutils.core import publish_parts
    from docutils.parsers.rst import directives
except ImportError:
    publish_parts = None
    directives = None

class Restructuredtext(Filter):

    match = ['restructuredtext', 'rst', 'rest', 'reST', 'reStructuredText']
    version = '1.0.1'

    conflicts = ['markdown', 'plain']
    priority = 70.00

    def init(self, conf, env):

        self.extensions = {}
        self.ignore = env.options.ignore

        if not publish_parts or not directives:
            raise ImportError('reStructuredText: No module named docutils')

        # -- discover reStructuredText extensions --
        for mem in os.listdir(os.path.dirname(__file__)):
            if mem.startswith('rstx_') and mem.endswith('.py'):
                try:
                    mod = __import__(mem.replace('.py', ''))
                    rstx = mod.makeExtension()
                    if isinstance(mod.match, basestring):
                        mod.match = [mod.__name__]
                    for name in mod.match:
                        directives.register_directive(name, rstx)
                except (ImportError, Exception), e:
                    log.warn('%r %s: %s' % (mem, e.__class__.__name__, e))

    def inject(self):

        return get_pygments_style()

    def transform(self, content, entry, *filters):

        settings = {
            'initial_header_level': 1,
            'doctitle_xform': 0
        }

        parts = publish_parts(content, writer_name='html', settings_overrides=settings)
        return parts['body'].encode('utf-8')
