# -*- coding: utf-8 -*-

from acrylamid import log, utils, core
from acrylamid.filters import initialize, get_filters

import attest

tt = attest.Tests()

log.init('foo', 35)

conf = core.Configuration({'lang': 'en', 'theme': ''})
env = utils.Struct({'path': '', 'engine': None, 'options': type('X', (), {'ignore': False})})
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
        pass
        # hyph = get_filters()['Hyphenate'](conf, env, 'Hyphenate')

        # hyph.transform('Airplane', Entry('en')) == 'Airplane'
        # hyph.transform('supercalifragilisticexpialidocious', Entry('en')) == \
        #                  '&shy;'.join(['su', 'per', 'cal', 'ifrag', 'ilis', 'tic', 'ex',
        #                                'pi', 'ali', 'do', 'cious'])

        # hyph = get_filters()['Hyphenate'](conf, env, 'Hyphenate')

        # assert hyph.transform('Flugzeug', Entry('de'), '8') == 'Flugzeug'
        # assert hyph.transform('Flugzeug', Entry('de'), '7') == 'Flug&shy;zeug'

        # # test unsupported
        # assert hyph.transform('Flugzeug', Entry('foo'), '8') == 'Flugzeug'

    @attest.test
    def build_pattern(self):
        pass
        # # short term
        # build('en')

        # hyphenate = build('en_US')
        # assert hyphenate('Airplane') == ['Air', 'plane']


@tt.test
def jinja2():
    pass
    # jinja2 = get_filters()['Jinja2'](conf, env, 'Jinja2')

    # assert jinja2.transform('{{ entry.lang }}', Entry('de')) == 'de'
    # assert jinja2.transform("{{ 'which which' | system }}", None) == '/usr/bin/which'


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

    conf['summarize_mode'] = 0
    summarize = get_filters()['summarize'](conf, env, 'summarize')

    assert summarize.transform((
        '<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod '
        'tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam</p>'
        '\n'
        '<p>Here it breaks ...</p>'),
        Entry(), '20') == (
        '<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod '
        'tempor incididunt ut labore et dolore magna aliqua. Ut '
        '<span>&#8230;<a href="/foo/" class="continue">continue</a>.</span></p>')



@tt.test
def intro():

    intro = get_filters()['intro'](conf, env, 'intro')
    examples = [('Hello World', ''),
                ('<p>First</p>', '<p>First</p><span>&#8230;<a href="/foo/" class="continue">continue</a>.</span>'),
                ('<p>First</p><p>Second</p>', '<p>First</p><span>&#8230;<a href="/foo/" class="continue">continue</a>.</span>')]

    for text, result in examples:
        assert intro.transform(text, Entry(), '1') == result


@tt.test
def strip():

    strip = get_filters()['strip'](conf, env, 'strip')
    examples = [
        ('<em>Foo</em>', 'Foo'), ('<a href="#">Bar</a>', 'Bar'),
        ('<video src="#" />', '')]

    for text, result in examples:
        assert strip.transform(text, Entry()) == result

    assert strip.transform('<pre>...</pre>', Entry(), 'pre') == ''
    assert strip.transform('<pre>&lt;</pre>', Entry(), 'pre') == ''


@tt.test
def liquid():

    liquid = get_filters()['liquid'](conf, env, 'liquid')

    # liquid block recognition
    text = '\n'.join([
        "{% tag %}", "", "Foo Bar.", "", "{% endtag %}"
    ])

    rv = liquid.block("tag").match(text)
    assert rv.group(1) == ""
    assert rv.group(2) == "\nFoo Bar.\n"

    # multiple, not nested blocks
    text = '\n'.join([
        "{% block %}", "", "Foo Bar.", "", "{% endblock %}",
        "",
        "{% block %}", "", "Baz.", "", "{% endblock %}"
    ])

    rv = tuple(liquid.block("block").finditer(text))
    assert len(rv) == 2

    x, y = rv
    assert x.group(2).strip() == "Foo Bar."
    assert y.group(2).strip() == "Baz."

    # self-closing block
    text = '{% block a few args %}'
    rv = liquid.block("block").match(text)

    assert rv is not None
    assert rv.group(1) == 'a few args'
    assert rv.group(2) is None

    # blockquote
    examples = [
        ('{% blockquote Author, Source http://example.org/ Title %}\nFoo Bar\n{% endblockquote %}',
         '<blockquote><p>Foo Bar</p><footer><strong>Author, Source</strong> <cite><a href="http://example.org/">Title</a></cite></footer></blockquote>'),
    ]

    for text, result in examples:
        assert liquid.transform(text, Entry()) == result
