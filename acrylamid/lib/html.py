# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

"""
Generic HTML tools
~~~~~~~~~~~~~~~~~~

A collection of tools that ease reading and writing HTML. Currently,
there's only a improved version of python's :class:`HTMLParser.HTMLParser`,
that returns the HTML untouched, so you can override specific calls to
add custom behavior.

This implementation is used :mod:`acrylamid.filters.acronyms`,
:mod:`acrylamid.filters.hyphenation` and more advanced in
:mod:`acrylamid.filters.summarize`. It is quite fast, but remains
an unintuitive way of working with HTML."""

import sys
import re

from cgi import escape
from HTMLParser import HTMLParser as DefaultParser, HTMLParseError
from htmlentitydefs import name2codepoint


def unescape(s):
    """&amp; -> & conversion"""
    return re.sub('&(%s);' % '|'.join(name2codepoint),
            lambda m: unichr(name2codepoint[m.group(1)]), s)


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
    """A more useful base HTMLParser that returns the actual HTML by
    default::

    >>> "<b>Foo</b>" == HTMLParser("<b>Foo</b>").result

    It is intended to use this class as base so you don't make
    the same mistakes I did before.

    .. attribute:: result

        This is the processed HTML."""

    def __init__(self, html):
        DefaultParser.__init__(self)
        self.result = []
        self.stack = []

        self.feed(html)

    def handle_starttag(self, tag, attrs):
        """Append tag to stack and write it to result."""

        self.stack.append(tag)
        self.result.append('<%s %s>' % (tag, format(attrs)) if attrs else '<%s>' % tag)

    def handle_data(self, data):
        """Everything that is *not* a tag shows up as data, but you can't expect
       that it is always a continous sentence or word."""

        self.result.append(data)

    def handle_endtag(self, tag):
        """Append ending tag to result and pop it from the stack too."""

        try:
            self.stack.pop()
        except IndexError:
            pass
        self.result.append('</%s>' % tag)

    def handle_startendtag(self, tag, attrs):
        """Something like ``"<br />"``"""
        self.result.append('<%s %s/>' % (tag, format(attrs)))

    def handle_entityref(self, name):
        """An escaped ampersand like ``"&#38;"``."""
        self.result.append('&' + name + ';')

    def handle_charref(self, char):
        """An escaped umlaut like ``"&auml;"``"""
        self.result.append('&#' + char + ';')

    def handle_comment(self, comment):
        """Preserve HTML comments."""
        self.result.append('<!--' + comment + '-->')

__all__ = ['HTMLParser', 'HTMLParseError', 'unescape']
