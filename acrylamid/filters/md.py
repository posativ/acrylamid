#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os
import markdown

from acrylamid.filters import Filter
from acrylamid.errors import AcrylamidException


def get_pygments_style():
    try:
        from pygments.formatters import get_formatter_by_name
    except ImportError:
        return {}

    fmt = get_formatter_by_name('html', style='trac')
    return {'text/css': '/* Pygments */\n\n' + fmt.get_style_defs('.highlight')}


class Markdown(Filter):

    match = ['md', 'mkdown', 'markdown', 'Markdown']
    version = '1.0.0'

    conflicts = ['rst', 'plain']
    priority = 70.0

    extensions = dict((x, x) for x in ['abbr', 'fenced_code', 'footnotes',
                                       'headerid', 'tables', 'codehilite'])

    def init(self, conf, env):

        self.failed = []
        self.ignore = env.options.ignore

        # -- discover markdown extensions --
        for mem in os.listdir(os.path.dirname(__file__)):
            if mem.startswith('mdx_') and mem.endswith('.py'):
                try:
                    mod = __import__(mem.replace('.py', ''))
                    mdx = mod.makeExtension()
                    if isinstance(mod.match, basestring):
                        self.match.append(mod.match)
                        self.extensions[mod.__name__] = mdx
                    else:
                        for name in mod.match:
                            self.extensions[name] = mdx
                except (ImportError, Exception), e:
                    self.failed.append('%r %s: %s' % (mem, e.__class__.__name__, e))

    def __contains__(self, key):
        return True if key in self.extensions else False

    def inject(self):

        if 'codehilite' in self:
            return get_pygments_style()
        return {}

    def transform(self, text, entry, *filters):

        val = []
        for f in filters:
            if f in self:
                val.append(f)
            else:
                x = f.split('(', 1)[:1][0]
                if x in self:
                    val.append(x)
                    self.extensions[x] = f
                elif not self.ignore:
                    raise AcrylamidException('Markdown: %s' % '\n'.join(self.failed))

        md = markdown.Markdown(extensions=[self.extensions[m] for m in val])
        return md.convert(text)
