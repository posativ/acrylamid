#!/usr/bin/env python
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from acrylamid.filters import Filter


class Markdown(Filter):

    __name__ = 'Pass-Through'
    __match__ = ['pass', 'plain', 'html', 'xhtml']
    __conflicts__ = ['rst', 'md']
    __priority__ = 70.0

    def __init__(self, conf, env):
        pass

    def __call__(self, content, request, *filters):
        return content
