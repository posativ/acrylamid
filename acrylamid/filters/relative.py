# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid import log
from acrylamid.filters import Filter
from acrylamid.helpers import joinurl
from acrylamid.lib.html import HTMLParser, HTMLParseError


class Href(HTMLParser):

    def __init__(self, html, func=lambda part: part):
        self.func = func
        super(Href, self).__init__(html)

    def apply(self, attrs):

        for i, (key, value) in enumerate(attrs):
            if key in ('href', 'src'):
                attrs[i] = (key, self.func(value))

        return attrs

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs = self.apply(attrs)
        super(Href, self).handle_starttag(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        if tag == 'img':
            attrs = self.apply(attrs)
        super(Href, self).handle_startendtag(tag, attrs)


class Relative(Filter):

    match = ['relative']
    version = 1

    def transform(self, text, entry, *args):

        def relatively(part):

            if part.startswith('/') or part.find('://') == part.find('/') - 1:
                return part

            return joinurl(entry.permalink, part)

        try:
            return ''.join(Href(text, relatively).result)
        except HTMLParseError as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.msg, entry.filename))
            return text


class Absolute(Filter):

    match = ['absolute']
    version = 1

    def init(self, conf, env):

        self.www_root = conf.www_root

    def transform(self, text, entry, *args):

        def absolutify(part):

            if part.startswith('/'):
                return joinurl(self.www_root, part)

            if part.find('://') == part.find('/') - 1:
                return part

            return joinurl(self.www_root, entry.permalink, part)

        try:
            return ''.join(Href(text, absolutify).result)
        except HTMLParseError as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.msg, entry.filename))
            return text
