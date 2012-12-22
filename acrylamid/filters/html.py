# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import re
from acrylamid.filters import Filter


class HTML(Filter):

    match = [re.compile('^(pass|plain|X?HTML)$', re.I)]
    version = 1

    conflicts = ['rst', 'md']
    priority = 70.0

    def transform(self, content, entry, *filters):
        return content
