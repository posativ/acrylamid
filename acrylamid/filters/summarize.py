# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid import log
from acrylamid.filters import Filter

from HTMLParser import HTMLParser, HTMLParseError
from cgi import escape


class Summarizer(HTMLParser):

    def __init__(self, text, href, link, mode, maxwords=100):
        HTMLParser.__init__(self)

        self.maxwords = maxwords
        self.href = href
        self.link = link
        self.mode = mode

        self.summarized = []
        self.words = 0
        self.stack = []

        self.feed(text)

    def handle_starttag(self, tag, attrs):
        # Apply and stack each tag until we reach maxword.

        def tagify(tag, attrs):
            if attrs:
                return '<%s %s>' % (tag, ' '.join(['%s="%s"' % (k, escape(v))
                                        for k, v in attrs]))
            else:
                return '<%s>' % tag

        if self.words < self.maxwords:
            self.stack.append(tag)
            self.summarized.append(tagify(tag, attrs))

    def handle_data(self, data):
        # append words
        if self.words >= self.maxwords:
            pass
        else:
            ws = data.count(' ')
            if ws + self.words < self.maxwords:
                self.summarized.append(data)
            else:
                words = data.split(' ')
                self.summarized.append(' '.join(words[:self.maxwords - self.words]) + ' ')
            self.words += ws

    def handle_endtag(self, tag):
        # If we are behind the word limit, append out link in various modes, else append tag
        if self.words < self.maxwords:
            self.summarized.append('</%s>' % self.stack.pop())

        elif self.stack:
            # this injects the link to the end of the current tag
            if self.mode == 0:
                self.summarized.append(self.link % self.href)

            # now we append all stored tags
            for x in self.stack[:]:

                # this adds the link if it's not inside a given tag, prefered way
                if self.mode == 1:
                    if not filter(lambda t: t in ['code', 'pre', 'b', 'a', 'em'], self.stack):
                        self.summarized.append(self.link % self.href)
                        self.mode = -1

                self.summarized.append('</%s>' % self.stack.pop())

            # this adds the link when the stack is empty
            if self.mode == 2:
                self.summarized.append(self.link % self.href)

    def handle_startendtag(self, tag, attrs):
        if self.words < self.maxwords:
            s = '<%s %s/>' % (tag, ' '.join(['%s="%s"' % (k, escape(v)) for k, v in attrs]))
            self.summarized.append(s)

    def handle_entityref(self, entity):
        # handle &shy; correctly
        if self.words < self.maxwords:
            self.summarized.append('&' + entity + ';')

    def handle_charref(self, char):
        # handle charrefs
        if self.words < self.maxwords:
            self.summarized.append('&#' + char + ';')


class Summarize(Filter):
    """Summarizes content up to `maxwords` (defaults to 100)."""

    match = ['summarize', 'sum']

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
            return ''.join(X.summarized)
        except HTMLParseError as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.msg, entry.filename))
            return content
