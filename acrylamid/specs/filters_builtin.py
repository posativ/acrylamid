# -*- coding: utf-8 -*-

from acrylamid import log, utils
from acrylamid.filters import initialize, get_filters

import attest
tt = attest.Tests()

log.init('foo', 35)

conf = {'lang': 'en'}
env = utils.Struct({'path': '', 'options': type('X', (), {'ignore': False})})
initialize([], conf, env)

# now we have filters in path
from acrylamid.filters.hyphenation import build


class Entry(object):

    permalink = '/foo/'

    def __init__(self, lang='en'):
        self.lang = lang


class Hyphenation(attest.TestBase):

    @attest.test
    def hyphenate(self):

        hyph = get_filters()['Hyphenate'](conf, env, 'Hyphenate')

        hyph.transform('Airplane', Entry('en')) == 'Airplane'
        hyph.transform('supercalifragilisticexpialidocious', Entry('en')) == \
                         '&shy;'.join(['su', 'per', 'cal', 'ifrag', 'ilis', 'tic', 'ex',
                                       'pi', 'ali', 'do', 'cious'])

        hyph = get_filters()['Hyphenate'](conf, env, 'Hyphenate')

        assert hyph.transform('Flugzeug', Entry('de'), '8') == 'Flugzeug'
        assert hyph.transform('Flugzeug', Entry('de'), '7') == 'Flug&shy;zeug'

        # test unsupported
        assert hyph.transform('Flugzeug', Entry('foo'), '8') == 'Flugzeug'

    @attest.test
    def build_pattern(self):

        # short term
        build('en')

        hyphenate = build('en_US')
        assert hyphenate('Airplane') == ['Air', 'plane']


@tt.test
def jinja2():

    jinja2 = get_filters()['Jinja2'](conf, env, 'Jinja2')

    assert jinja2.transform('{{ entry.lang }}', Entry('de')) == 'de'
    assert jinja2.transform("{{ 'which which' | system }}", None) == '/usr/bin/which'


@tt.test
def mako():

    mako = get_filters()['Mako'](conf, env, 'Mako')

    e = Entry('de')
    e.filename = '1'

    assert mako.transform('${entry.lang}', Entry('de')) == 'de'
    assert mako.transform("${ 'which which' | system }", e) == '/usr/bin/which'


@tt.test
def acronyms():

    acronyms = get_filters()['Acronyms'](conf, env, 'Acronyms')
    abbr = lambda abbr, expl: '<abbr title="%s">%s</abbr>' % (expl, abbr)

    examples = [
        ('CGI', abbr('CGI', 'Common Gateway Interface')),
        ('IMDB', abbr('IMDB', 'Internet Movie Database')),
        ('IMDb', abbr('IMDb', 'Internet Movie Database')),
        ('PHP5', abbr('PHP5', 'Programmers Hate PHP ;-)')),
        ('TEST', 'TEST')
    ]

    for test, result in examples:
        assert acronyms.transform(test, None) == result


@tt.test
def headoffset():

    h1 = get_filters()['h1'](conf, env, 'h1')
    examples = [
        ('<h1>Hello</h1>', '<h2>Hello</h2>'), ('<h2>World</h2>', '<h3>World</h3>'),
        ('<h1 class="foo bar">spam</h1>', '<h2 class="foo bar">spam</h2>'),
        ('<h1 class="foo" id="baz">spam</h1>', '<h2 class="foo" id="baz">spam</h2>'),
    ]

    for test, result in examples:
        assert h1.transform(test, None) == result

    h5 = get_filters()['h5'](conf, env, 'h5')
    assert h5.transform('<h3>eggs</h3>', '<h6>eggs</h6>')


@tt.test
def summarize():

    summarize = get_filters()['summarize'](conf, env, 'summarize')
    examples = [('Hello World', 'Hello World'),
                # a real world example
                ('<p>Hello World, you have to click this link because</p>',
                 '<p>Hello World, you have to <span>&#8230;<a href="/foo/" '+ \
                 'class="continue">continue</a>.</span></p>'),
                ('<p>Hel&shy;lo Wor&shy;ld, you have to click this link because</p>',
                # now with HTML entities
                 '<p>Hel&shy;lo Wor&shy;ld, you have to <span>&#8230;<a href="/foo/" '+ \
                 'class="continue">continue</a>.</span></p>'),
                ('Hello<br />', 'Hello<br />'),
                ('<p>Hello World, you have<br /> to <br /> click<br /> this<br /> link...</p>',
                 '<p>Hello World, you have<br /> to <span>&#8230;<a href="/foo/" '+ \
                 'class="continue">continue</a>.</span></p>'),
                ('Hello World, you have to click this link because',
                 'Hello World, you have to <span>&#8230;<a href="/foo/" '+ \
                 'class="continue">continue</a>.</span>')]

    for text, result in examples:
        assert summarize.transform(text, Entry(), '5') == result
