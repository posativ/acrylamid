# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from acrylamid.filters import Filter

try:
    from discount import Markdown
except ImportError:
    Markdown = None  # NOQA


class Discount(Filter):

    match = ['discount', 'Discount']
    version = 1

    conflicts = ['Markdown', 'reStructuredText', 'HTML', 'Pandoc', 'typography']
    priority = 70.0

    def init(self, conf, env):

        if Markdown is None:
            raise ImportError("Discount: discount not available")

    def transform(self, text, entry, *args):

        mkd = Markdown(text.encode('utf-8'),
                       autolink=True, safelink=True, ignore_header=True)
        return mkd.get_html_content().decode('utf-8')
