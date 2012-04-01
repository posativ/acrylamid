#!/usr/bin/env python
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import re
from acrylamid.filters import Filter


class HTML(Filter):

    match = [re.compile('^(pass|plain|X?HTML)$', re.I)]
    conflicts = ['rst', 'md']
    priority = 70.0

    def transform(self, content, entry, *filters):
        return content
