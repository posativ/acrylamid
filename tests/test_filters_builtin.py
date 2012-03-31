# -*- coding: utf-8 -*-

import sys; reload(sys)
sys.setdefaultencoding('utf-8')

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA

from acrylamid import log, defaults, Environment
from acrylamid.filters import initialize, get_filters

log.init('foo', 15)
initialize([], {'lang': 'en'}, Environment({'path': '/',
           'options': type('X', (), {'ignore': False})}))

# now we have filters in path
from acrylamid.filters.hyphenation import build


class Entry(object):

    def __init__(self, lang):
        self.lang = lang


class TestHyphenation(unittest.TestCase):

    def test_hyphenation(self):

        hyph = get_filters()['Hyphenate']('Hyphenate')

        self.assertEqual(hyph.transform('Airplane', Entry('en')), 'Airplane')
        self.assertEqual(hyph.transform('supercalifragilisticexpialidocious', Entry('en')),
                         '&shy;'.join(['su', 'per', 'cal', 'ifrag', 'ilis', 'tic', 'ex',
                                       'pi', 'ali', 'do', 'cious']))

        hyph = get_filters()['Hyphenate']('Hyphenate')

        self.assertEqual(hyph.transform('Flugzeug', Entry('de'), '8'), 'Flugzeug')
        self.assertEqual(hyph.transform('Flugzeug', Entry('de'), '7'), 'Flug&shy;zeug')

        # test unsupported
        self.assertEqual(hyph.transform('Flugzeug', Entry('foo'), '8'), 'Flugzeug')

    def test_hyphenation_build(self):

        # short term
        build('en')

        hyphenate = build('en_US')
        self.assertEqual(hyphenate('Airplane'), ['Air', 'plane'])

    def test_jinja2(self):

        jinja2 = get_filters()['Jinja2']('Jinja2')

        self.assertEqual(jinja2.transform('{{ entry.lang }}', Entry('de')), 'de')
        self.assertEqual(jinja2.transform("{{ 'which which' | system }}", None), '/usr/bin/which')
