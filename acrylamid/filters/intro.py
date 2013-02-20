# -*- encoding: utf-8 -*-
#
# Copyright 2012 Mark van Lent <mark@vlent.nl>. All rights reserved.
# License: BSD Style, 2 clauses.

from acrylamid import log, helpers
from acrylamid.filters import Filter
from acrylamid.lib.html import HTMLParser, HTMLParseError


class Introducer(HTMLParser):
    paragraph_list = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'ul', 'ol', 'pre', 'p']
    """List of root elements, which may be treated as paragraphs"""

    def __init__(self, html, maxparagraphs, href, options):
        self.maxparagraphs = maxparagraphs
        self.paragraphs = 0
        self.options = options
        self.href = href

        super(Introducer, self).__init__(html)

    def handle_starttag(self, tag, attrs):
        if self.paragraphs < self.maxparagraphs:
            super(Introducer, self).handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self.paragraphs >= self.maxparagraphs:
            pass
        elif len(self.stack) < 1 or (self.stack[0] not in self.paragraph_list and self.stack[-1] not in self.paragraph_list):
            pass
        else:
            self.result.append(data)

    def handle_endtag(self, tag):
        if self.paragraphs < self.maxparagraphs:
            if tag in self.paragraph_list:
                self.paragraphs += 1
            super(Introducer, self).handle_endtag(tag)

            if self.paragraphs == self.maxparagraphs:
                for x in self.stack[:]:
                    self.result.append('</%s>' % self.stack.pop())
                if self.options['link'] != '':
                    self.result.append(self.options['link'] % self.href)

    def handle_startendtag(self, tag, attrs):
        if self.paragraphs < self.maxparagraphs and tag not in self.options['ignored']:
            super(Introducer, self).handle_startendtag(tag, attrs)

    def handle_entityref(self, name):
        if self.paragraphs < self.maxparagraphs:
            super(Introducer, self).handle_entityref(name)

    def handle_charref(self, char):
        if self.paragraphs < self.maxparagraphs:
            super(Introducer, self).handle_charref(char)

    def handle_comment(self, comment):
        if self.paragraphs < self.maxparagraphs:
            super(Introducer, self).handle_comment(comment)


class Introduction(Filter):

    match = ['intro', ]
    version = 2
    priority = 15.0

    defaults = {
        'ignored': ['img', 'video', 'audio'],
        'link': '<span>&#8230;<a href="%s" class="continue">continue</a>.</span>'
    }

    def transform(self, content, entry, *args):
        options = helpers.union(Introduction.defaults, self.conf.fetch('intro_'))

        try:
            options.update(entry.intro)
        except AttributeError:
            pass

        try:
            maxparagraphs = int(options.get('maxparagraphs') or args[0])
        except (IndexError, ValueError) as ex:
            if isinstance(ex, ValueError):
                log.warn('Introduction: invalid maxparagraphs argument %r',
                         options.get('maxparagraphs') or args[0])
            maxparagraphs = 1

        try:
            return ''.join(Introducer(
                content, maxparagraphs, self.env.path+entry.permalink, options).result)
        except HTMLParseError as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.msg,
                                       entry.filename))
            return content
        return content
