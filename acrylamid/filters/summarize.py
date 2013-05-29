# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from acrylamid import log, helpers
from acrylamid.filters import Filter

from acrylamid.lib.html import HTMLParser, HTMLParseError


class Summarizer(HTMLParser):

    def __init__(self, text, maxwords, href, options):
        self.href = href
        self.mode = options['mode']
        self.options = options

        self.words = 0
        self.maxwords = maxwords

        HTMLParser.__init__(self, text)

    def handle_starttag(self, tag, attrs):
        # Apply and stack each tag until we reach maxword.
        if self.words < self.maxwords:
            super(Summarizer, self).handle_starttag(tag, attrs)

    def handle_data(self, data):
        # append words
        if self.words >= self.maxwords:
            pass
        else:
            ws = data.count(' ')
            if ws + self.words < self.maxwords:
                self.result.append(data)
            else:
                words = data.split(' ')
                self.result.append(' '.join(words[:self.maxwords - self.words]) + ' ')
            self.words += ws

        if self.words >= self.maxwords and not self.stack:
            # weird markup, mostly from WordPress. Just append link and break
            if self.mode > -1:
                self.result.append(self.options['link'] % self.href)
                self.mode = -1

    def handle_endtag(self, tag):
        # If we are behind the word limit, append out link in various modes, else append tag
        if self.words < self.maxwords:
            self.result.append('</%s>' % self.stack.pop())

        elif self.stack:
            # this injects the link to the end of the current tag
            if self.mode == 0:
                self.result.append(self.options['link'] % self.href)
                self.mode = -1

            # now we append all stored tags
            for x in self.stack[:]:

                # this adds the link if it's not inside a given tag, prefered way
                if self.mode == 1:
                    if not any(filter(lambda t: t in ['code', 'pre', 'b', 'a', 'em'], self.stack)):
                        self.result.append(self.options['link'] % self.href)
                        self.mode = -1

                self.result.append('</%s>' % self.stack.pop())

            # this adds the link when the stack is empty
            if self.mode == 2:
                self.result.append(self.options['link'] % self.href)

    def handle_startendtag(self, tag, attrs):
        if self.words < self.maxwords and tag not in self.options['ignore']:
            super(Summarizer, self).handle_startendtag(tag, attrs)

    def handle_entityref(self, entity):
        if self.words < self.maxwords:
            super(Summarizer, self).handle_entityref(entity)

    def handle_charref(self, char):
        if self.words < self.maxwords:
            super(Summarizer, self).handle_charref(char)

    def handle_comment(self, comment, keywords=['excerpt', 'summary', 'break', 'more']):
        if self.words < self.maxwords and [word for word in keywords if word in comment.lower()]:
            self.words = self.maxwords


class Summarize(Filter):
    """Summarizes content up to `maxwords` (defaults to 100)."""

    match = ['summarize', 'sum']
    version = 3
    priority = 15.0

    defaults = {
        'mode': 1,
        'ignore': ['img', 'video', 'audio'],
        'link': '<span>&#8230;<a href="%s" class="continue">continue</a>.</span>'
    }

    @property
    def uses(self):
        return self.env.path

    def transform(self, content, entry, *args):
        options = helpers.union(Summarize.defaults, self.conf.fetch('summarize_'))

        try:
            options.update(entry.summarize)
        except AttributeError:
            pass

        try:
            maxwords = int(options.get('maxwords') or args[0])
        except (IndexError, ValueError) as ex:
            if isinstance(ex, ValueError):
                log.warn('Summarize: invalid maxwords argument %r',
                         options.get('maxwords') or args[0])
            maxwords = 100

        try:
            return ''.join(Summarizer(
                content, maxwords, self.env.path+entry.permalink, options).result)
        except HTMLParseError:
            log.exception('could not summarize ' + entry.filename)
            return content
