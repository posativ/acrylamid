# -*- coding: utf-8 -*-

import sys; reload(sys)
sys.setdefaultencoding('utf-8')

import shutil

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
        utils.cache.init()

    def tearDown(self):
        shutil.rmtree(utils.cache.cache_dir)

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

        class X(str):
            # dummy class
            has_changed = True
            md5 = property(lambda x: str(hash(x)))

        res = ['1', 'asd', 'asd123', 'egg', 'spam', 'ham', '3.14', '42']
        res = [X(val) for val in res]

        # default stuff
        self.assertEqual(list(utils.paginate(res, 4)),
            [(0, res[:4], True), (1, res[4:], True)])
        self.assertEqual(list(utils.paginate(res, 4, lambda x: x.isdigit())),
            [(0, [X('1'), X('42')], True), ])
        self.assertEqual(list(utils.paginate(res, 7)),
            [(0, res[:7], True), (1, res[7:], True)])

        # with orphans
        self.assertEqual(list(utils.paginate(res, 7, orphans=1)),
            [(0, res, True)])
        self.assertEqual(list(utils.paginate(res, 6, orphans=1)),
            [(0, res[:6], True), (1, res[6:], True)])

        # a real world example which has previously failed
        res = [X(_) for _ in range(20)]
        self.assertEqual(list(utils.paginate(res, 10)),
            [(0, res[:10], True), (1, res[10:], True)])

        # edge cases
        self.assertEqual(list(utils.paginate([], 2)), [])
        self.assertEqual(list(utils.paginate([], 2, orphans=7)), [])
        self.assertEqual(list(utils.paginate([X('1'), X('2'), X('3')], 3, orphans=1)),
            [(0, [X('1'), X('2'), X('3')], True)])

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
