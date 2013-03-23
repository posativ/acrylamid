# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from acrylamid import log

from acrylamid.filters import Filter
from acrylamid.lib.html import HTMLParser, HTMLParseError


class Text(HTMLParser):
    """Strip tags and attributes from HTML.  By default it keeps everything
    between any HTML tags, but you can supply a list of ignored tags."""

    handle_comment = handle_startendtag = lambda *x, **z: None

    def __init__(self, html, args):

        self.ignored = args
        super(Text, self).__init__(html)

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)

    def handle_endtag(self, tag):
        try:
            self.stack.pop()
        except IndexError:
            pass

        if tag in ('li', 'ul', 'p'):
            self.result.append('\n')

    def handle_data(self, data):
        if not any(tag for tag in self.ignored if tag in self.stack):
            super(Text, self).handle_data(data)

    def handle_entityref(self, name):
        if name == 'shy':
            return
        self.handle_data(self.unescape('&' + name + ';'))

    def handle_charref(self, char):
        self.handle_data(self.unescape('&#' + char + ';'))


class Strip(Filter):

    match = ['strip']
    version = 1
    priority = 0.0

    def transform(self, content, entry, *args):

        try:
            return ''.join(Text(content, args).result)
        except HTMLParseError:
            log.exception('could not strip ' + entry.filename)
            return content
