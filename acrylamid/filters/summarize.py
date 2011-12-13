# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from acrylamid.filters import Filter

from HTMLParser import HTMLParser
from cgi import escape

class Summarizer(HTMLParser):

    def __init__(self, text, href, maxwords=100):
        HTMLParser.__init__(self)
        self.maxwords = maxwords
        self.href = href
        self.summarized = ''
        self.words = 0
        self.stack = []

        self.feed(text)

    def handle_starttag(self, tag, attrs):
        '''Apply and stack each read tag until we reach maxword.'''

        def tagify(tag, attrs):
            '''convert parsed tag back into a html tag'''
            if attrs:
                return '<%s %s>' % (tag, ' '.join(['%s="%s"' % (k, escape(v))
                                        for k,v in attrs]))
            else:
                return '<%s>' % tag

        if self.words < self.maxwords:
            self.stack.append(tag)
            self.summarized += tagify(tag, attrs)

    def handle_data(self, data):

        if self.words >= self.maxwords:
            pass
        else:
            words = data.split(' ')
            if self.words + len(words) < self.maxwords:
                '''if the next few words will not go over maxwords'''
                self.words += len(words)
                self.summarized += data
            else:
                '''we can put some words before we reach the word limit'''
                if 'a' not in self.stack and self.stack and self.stack[-1] != 'ul':
                    somewords = self.maxwords - self.words
                    self.words += somewords
                    self.summarized += ' '.join(words[:somewords]) + ' '
                    self.summarized += '<span>&#8230;<a href="%s" class="continue">weiterlesen</a>.</span>' % self.href
                else:
                    self.maxwords += len(words)
                    self.words += len(words)
                    self.summarized += ' '.join(words)

    def handle_endtag(self, tag):
        '''Until we reach not the maxwords limit, we can safely pop every ending tag,
           added by handle_starttag. Afterwards, we apply missing endings tags if missing.'''
        if self.words < self.maxwords:
            self.stack.pop()
            self.summarized += '</%s>' % tag
        else:
            if self.stack:
                for x in range(len(self.stack)):
                    self.summarized += '</%s>' % self.stack.pop()
                    
    def handle_entityref(self, entity):
        '''handle &shy; correctly'''
        if self.words < self.maxwords:
            self.summarized += '&'+ entity + ';'
            
    def handle_charref(self, char):
        if self.words < self.maxwords:
            self.summarized += '&#' + char + ';'


class Summarize(Filter):
    
    __name__ = 'Summarize'
    __match__ = ['summarize', 'sum']
   
    def __init__(self, conf, env):
        self.env = env
        
    def __call__(self, content, req):
        
        return Summarizer(content, req.permalink, 200).summarized
