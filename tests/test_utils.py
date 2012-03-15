# -*- coding: utf-8 -*-

import sys; reload(sys)
sys.setdefaultencoding('utf-8')

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA

from acrylamid import log
from acrylamid import utils
from acrylamid import AcrylamidException

class TestUtils(unittest.TestCase):

    def setUp(self):
        log.init('acrylamid', level=40)

    def test_safeslug(self):

        examples = (('This is a Test', 'this-is-a-test'),
                    ('this is a test', 'this-is-a-test'),
                    ('This is another-- test', 'this-is-another-test'),
                    ('A real example: Hello World in C++ -- "a new approach*"!',
                     'a-real-example-hello-world-in-c++-a-new-approach'))

        for value, expected in examples:
            self.assertEqual(utils.safeslug(value), expected)

        if not utils.translitcodec:
            raise ImportError('this test requires `translitcodec`')

        examples = ((u'Hänsel und Gretel', 'haensel-und-gretel'),
                    (u'fácil € ☺', 'facil-eur'))

        for value, expected in examples:
            self.assertEqual(utils.safeslug(value), expected)

        from unicodedata import normalize
        setattr(utils, 'normalize', normalize)
        utils.translitcodec = None
        self.assertEqual(utils.safeslug(u'Hänsel und Gretel'), 'hansel-und-gretel')

    def test_joinurl(self):

        examples = ((['hello', 'world'], 'hello/world'),
                    (['/hello', 'world'], '/hello/world'),
                    (['hello', '/world'], 'hello/world'),
                    (['/hello', '/world'], '/hello/world'))

        for value, expected in examples:
            self.assertEqual(utils.joinurl(*value), expected)

    def test_expand(self):

        self.assertEqual(utils.expand('/:foo/:bar/', {'foo': 1, 'bar': 2}), '/1/2/')
        self.assertEqual(utils.expand('/:foo/:spam/', {'foo': 1, 'bar': 2}), '/1/:spam/')

    def test_paginate(self):

        res = ['1', 'asd', 'asd123', 'egg', 'spam', 'ham', '3.14', '42']
        examples = ((4, lambda x: x, ([res[:4], res[4:]], True)),
                    (4, lambda x: x.isdigit(), ([['1', '42'], ], True)),
                    (3, lambda x: x.isalpha(), ([['asd', 'egg', 'spam'], ['ham']], True)),
            )

        for ipp, func, expected in examples:
            self.assertEqual(utils.paginate(res, ipp, func), expected)

        # a real world example which has previously failed
        x, foo = utils.paginate(range(20), 10, lambda x: True)
        self.assertEqual(x, [range(20)[:10], range(20)[10:]])

    def test_system(self):

        examples = ((['echo', 'ham'], None, 'ham'),
                    ('bc', '1 + 1\n', '2'),
            )
        for cmd, stdin, expected in examples:
            self.assertEqual(utils.system(cmd, stdin), expected)

        with self.assertRaises(AcrylamidException):
            utils.system('bc', '1+1')
        with self.assertRaises(OSError):
            utils.system('foo', None)
