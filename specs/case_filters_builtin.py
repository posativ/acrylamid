# -*- coding: utf-8 -*-

from acrylamid import log, defaults, Environment
from acrylamid.filters import initialize, get_filters

log.init('foo', 35)

conf = {'lang': 'en'}
env = Environment({'path': '', 'options': type('X', (), {'ignore': False})})
initialize([], conf, env)

# now we have filters in path
from acrylamid.filters.hyphenation import build


class Entry(object):

    permalink = '/foo/'

    def __init__(self, lang='en'):
        self.lang = lang


describe "Hyphenation":

    it "hyphenates":

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

    it "builds us pattern":

        # short term
        build('en')

        hyphenate = build('en_US')
        assert hyphenate('Airplane') == ['Air', 'plane']

describe "Jinja2":

    it "works":

        jinja2 = get_filters()['Jinja2'](conf, env, 'Jinja2')

        assert jinja2.transform('{{ entry.lang }}', Entry('de')) == 'de'
        assert jinja2.transform("{{ 'which which' | system }}", None) == '/usr/bin/which'

describe "Summarize":

    it "works":

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
                     'class="continue">continue</a>.</span></p>')]

        for text, result in examples:
            assert summarize.transform(text, Entry(), '5') == result
