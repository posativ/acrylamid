# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import shutil

from acrylamid import log
from acrylamid.core import cache
from acrylamid import helpers
from acrylamid import AcrylamidException


class Helpers(unittest.TestCase):

    @classmethod
    def setup_class(self):
        log.init('acrylamid', level=40)
        cache.init()

    @classmethod
    def teardown_class(self):
        shutil.rmtree(cache.cache_dir)

    @unittest.skipIf(helpers.translitcodec is None, 'no translitcodec available')
    def test_safeslug(self):

        examples = (('This is a Test', 'this-is-a-test'),
                    ('this is a test', 'this-is-a-test'),
                    ('This is another-- test', 'this-is-another-test'),
                    ('A real example: Hello World in C++ -- "a new approach*"!',
                     'a-real-example-hello-world-in-c++-a-new-approach'))

        for value, expected in examples:
            assert helpers.safeslug(value) == expected

        examples = ((u'Hänsel und Gretel', 'haensel-und-gretel'),
                    (u'fácil € ☺', 'facil-eur'))

        for value, expected in examples:
            assert helpers.safeslug(value) == expected

        from unicodedata import normalize
        setattr(helpers, 'normalize', normalize)
        helpers.translitcodec = None
        assert helpers.safeslug(u'Hänsel und Gretel') == 'hansel-und-gretel'

    @unittest.skipIf(helpers.unidecode is None, 'no unidecode available')
    def test_safeslugwithrussian(self):

        examples = [(u'Nothing happens', 'nothing-happens'),
                    (u'русский', 'russkii')]

        for value, expected in examples:
            assert helpers.safeslug(value) == expected

        helpers.unidecode = None
        assert helpers.safeslug(u'русский') == ''

    def test_joinurl(self):

        examples = ((['hello', 'world'], 'hello/world'),
                    (['/hello', 'world'], '/hello/world'),
                    (['hello', '/world'], 'hello/world'),
                    (['/hello', '/world'], '/hello/world'),
                    (['/hello/', '/world/'], '/hello/world/'))

        for value, expected in examples:
            assert helpers.joinurl(*value) == expected

    def test_expand(self):

        assert helpers.expand('/:foo/:bar/', {'foo': 1, 'bar': 2}) == '/1/2/'
        assert helpers.expand('/:foo/:spam/', {'foo': 1, 'bar': 2}) == '/1/:spam/'
        assert helpers.expand('/:foo/', {'bar': 2}) == '/:foo/'

    def test_paginate(self):

        class X(str):  # dummy class
            has_changed = True
            md5 = property(lambda x: str(hash(x)))

        res = ['1', 'asd', 'asd123', 'egg', 'spam', 'ham', '3.14', '42']
        res = [X(val) for val in res]

        # default stuff
        assert list(helpers.paginate(res, 4)) == \
            [((None, 1, 2), res[:4], True), ((1, 2, None), res[4:], True)]
        assert list(helpers.paginate(res, 4, lambda x: x.isdigit())) == \
            [((None, 1, None), [X('1'), X('42')], True), ]
        assert list(helpers.paginate(res, 7)) == \
            [((None, 1, 2), res[:7], True), ((1, 2, None), res[7:], True)]

        # with orphans
        assert list(helpers.paginate(res, 7, orphans=1)) == \
            [((None, 1, None), res, True)]
        assert list(helpers.paginate(res, 6, orphans=1)) == \
            [((None, 1, 2), res[:6], True), ((1, 2, None), res[6:], True)]

        # a real world example which has previously failed
        res = [X(_) for _ in range(20)]
        assert list(helpers.paginate(res, 10)) == \
            [((None, 1, 2), res[:10], True), ((1, 2, None), res[10:], True)]

        res = [X(_) for _ in range(21)]
        assert list(helpers.paginate(res, 10)) == \
            [((None, 1, 2), res[:10], True), ((1, 2, 3), res[10:20], True),
             ((2, 3, None), res[20:], True)]

        # edge cases
        assert list(helpers.paginate([], 2)) == []
        assert list(helpers.paginate([], 2, orphans=7)) == []
        assert list(helpers.paginate([X('1'), X('2'), X('3')], 3, orphans=1)) == \
            [((None, 1, None), [X('1'), X('2'), X('3')], True)]

    def test_safe(self):

        assert helpers.safe('"') == '"'
        assert helpers.safe('') == '""'

        assert helpers.safe('*Foo') == '"*Foo"'
        assert helpers.safe('{"Foo') == '\'{"Foo\''

        assert helpers.safe('"Foo" Bar') == '"Foo" Bar'
        assert helpers.safe("'bout \" and '") == "\"'bout \" and '\""

        assert helpers.safe('Hello World') == 'Hello World'
        assert helpers.safe('Hello: World') == '"Hello: World"'
        assert helpers.safe('Hello\'s World') == 'Hello\'s World'
        assert helpers.safe('Hello "World"') == 'Hello "World"'

    def test_system(self):

        examples = ((['echo', 'ham'], None, 'ham'),
                    ('cat', 'foo', 'foo'),
            )
        for cmd, stdin, expected in examples:
            assert helpers.system(cmd, stdin) == expected

        with self.assertRaises(AcrylamidException):
            helpers.system('bc', '1+1')

        with self.assertRaises(OSError):
            helpers.system('foo', None)
