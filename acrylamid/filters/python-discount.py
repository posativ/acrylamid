# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid.filters import Filter

try:
    from discount import Markdown
except ImportError:
    Markdown = None  # NOQA


class Discount(Filter):

    match = ['discount', 'Discount']
    version = '1.0.0'

    conflicts = ['Markdown', 'reStructuredText', 'HTML', 'Pandoc', 'typography']
    priority = 70.0

    def init(self, conf, env):

        if Markdown is None:
            raise ImportError("Discount: discount not available")

    def transform(self, text, entry, *args):

        mkd = Markdown(text.encode(entry.encoding),
                       autolink=True, safelink=True, ignore_header=True)
        return mkd.get_html_content().decode(entry.encoding, errors='replace')
