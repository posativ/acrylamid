from acrylamid import log
from acrylamid.filters import Filter
from acrylamid.lib.html import HTMLParser, HTMLParseError


class Introducer(HTMLParser):

    def __init__(self, html, maxparagraphs=1):
        self.maxparagraphs = maxparagraphs
        self.paragraphs = 0
        super(Introducer, self).__init__(html)

    def handle_starttag(self, tag, attrs):
        if self.paragraphs < self.maxparagraphs:
            super(Introducer, self).handle_starttag(tag, attrs)

    def handle_data(self, data):
        if len(self.stack) < 1 or self.stack[0] != 'p':
            pass
        elif self.paragraphs >= self.maxparagraphs:
            pass
        else:
            self.result.append(data)

    def handle_endtag(self, tag):
        if self.paragraphs < self.maxparagraphs:
            if tag == 'p':
                self.paragraphs += 1
            super(Introducer, self).handle_endtag(tag)

    def handle_startendtag(self, tag, attrs):
        if self.paragraphs < self.maxparagraphs:
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

    def transform(self, content, entry, *args):
        try:
            maxparagraphs = int(entry.intro.maxparagraphs)
        except (AttributeError, KeyError, ValueError) as e:
            try:
                maxparagraphs = int(args[0])
            except (ValueError, IndexError) as e:
                if e.__class__.__name__ == 'ValueError':
                    log.warn('Introduction: invalid maxparagraphs argument %r',
                             args[0])
                maxparagraphs = 1

        try:
            return ''.join(Introducer(content, maxparagraphs).result)
        except HTMLParseError as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.msg,
                                       entry.filename))
            return content
        return content
