#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys

from cgi import escape
from HTMLParser import HTMLParser as DefaultParser, HTMLParseError

from acrylamid.lib.async import ThreadPool, Worker


def format(attrs):
    res = []
    for key, value in attrs:
        if value is None:
            res.append(key)
        else:
            res.append('%s="%s"' % (key, escape(value)))
    return ' '.join(res)


if sys.version_info < (3, 0):
    class WTFMixin(object, DefaultParser):
        pass
else:
    class WTFMixin(DefaultParser):
        pass


class HTMLParser(WTFMixin):
    """A more useful base HTMLParser.  This class contains the processed but untouched
    result in self.result. It is intended to use this class to avoid HTML mess up."""

    def __init__(self, html):
        DefaultParser.__init__(self)
        self.result = []
        self.stack = []

        self.feed(html)

    def handle_starttag(self, tag, attrs):

        self.stack.append(tag)
        self.result.append('<%s %s>' % (tag, format(attrs)) if attrs else '<%s>' % tag)

    def handle_data(self, data):
        self.result.append(data)

    def handle_endtag(self, tag):
        try:
            self.stack.pop()
        except IndexError:
            pass
        self.result.append('</%s>' % tag)

    def handle_startendtag(self, tag, attrs):
        self.result.append('<%s %s/>' % (tag, format(attrs)))

    def handle_entityref(self, name):
        self.result.append('&' + name + ';')

    def handle_charref(self, char):
        self.result.append('&#' + char + ';')


__all__ = ['HTMLParser', 'HTMLParseError', 'ThreadPool', 'Worker']
