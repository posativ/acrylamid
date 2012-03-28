#!/usr/bin/env python
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from acrylamid.filters import Filter


class HTML(Filter):

    match = ['pass', 'plain', 'html', 'xhtml', 'HTML']
    conflicts = ['rst', 'md']
    priority = 70.0

    def transform(self, content, request, *filters):
        return content
