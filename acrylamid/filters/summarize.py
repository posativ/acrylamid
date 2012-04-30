# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid import log
from acrylamid.filters import Filter

from acrylamid.lib import HTMLParser, HTMLParseError


class Summarizer(HTMLParser):

    def __init__(self, text, href, link, mode, maxwords=100):
        self.maxwords = maxwords
        self.href = href
        self.link = link
        self.mode = mode
        self.words = 0

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

    def handle_endtag(self, tag):
        # If we are behind the word limit, append out link in various modes, else append tag
        if self.words < self.maxwords:
            self.result.append('</%s>' % self.stack.pop())

        elif self.stack:
            # this injects the link to the end of the current tag
            if self.mode == 0:
                self.result.append(self.link % self.href)

            # now we append all stored tags
            for x in self.stack[:]:

                # this adds the link if it's not inside a given tag, prefered way
                if self.mode == 1:
                    if not filter(lambda t: t in ['code', 'pre', 'b', 'a', 'em'], self.stack):
                        self.result.append(self.link % self.href)
                        self.mode = -1

                self.result.append('</%s>' % self.stack.pop())

            # this adds the link when the stack is empty
            if self.mode == 2:
                self.result.append(self.link % self.href)

    def handle_startendtag(self, tag, attrs):
        if self.words < self.maxwords:
            super(Summarizer, self).handle_startendtag(tag, attrs)

    def handle_entityref(self, entity):
        if self.words < self.maxwords:
            super(Summarizer, self).handle_entityref(entity)

    def handle_charref(self, char):
        if self.words < self.maxwords:
            super(Summarizer, self).handle_charref(char)


class Summarize(Filter):
    """Summarizes content up to `maxwords` (defaults to 100)."""

    match = ['summarize', 'sum']
    version = '1.0.0'

    def init(self, conf, env):

        self.path = env.path
        self.mode = conf.get('summarize_mode', 1)

        ellipsis = conf.get('summarize_ellipsis', '&#8230;')
        identifier = conf.get('summarize_identifier', 'continue')
        klass = conf.get('summarize_class', 'continue')

        self.link = '<span>'+ellipsis+'<a href="%s" class="'+klass+'">'+identifier+'</a>.</span>'

    def transform(self, content, entry, *args):

        try:
            maxwords = int(args[0])
        except (ValueError, IndexError) as e:
            if e.__class__.__name__ == 'ValueError':
                log.warn('Summarize: invalid maxwords argument %r', args[0])
            maxwords = 100

        try:
            X = Summarizer(content, self.path+entry.permalink, self.link, self.mode, maxwords)
            return ''.join(X.result)
        except HTMLParseError as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.msg, entry.filename))
            return content
