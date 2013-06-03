# -*- coding: utf-8 -*-

import attest

from acrylamid import helpers, refs
from acrylamid import AcrylamidException


class Helpers(attest.TestBase):

    @attest.test
    def safeslug(self):

        examples = (('This is a Test', 'this-is-a-test'),
                    ('this is a test', 'this-is-a-test'),
                    ('This is another-- test', 'this-is-another-test'),
                    ('A real example: Hello World in C++ -- "a new approach*"!',
                     'a-real-example-hello-world-in-c++-a-new-approach'))

        for value, expected in examples:
            assert helpers.safeslug(value) == expected

        examples = ((u'Hänsel und Gretel', 'haensel-und-gretel'),
                    (u'fácil € ☺', 'facil-eu'),
                    (u'русский', 'russkii'))

        for value, expected in examples:
            assert helpers.safeslug(value) == expected

    @attest.test
    def joinurl(self):

        examples = ((['hello', 'world'], 'hello/world'),
                    (['/hello', 'world'], '/hello/world'),
                    (['hello', '/world'], 'hello/world'),
                    (['/hello', '/world'], '/hello/world'),
                    (['/hello/', '/world/'], '/hello/world/index.html'),
                    (['/bar/', '/'], '/bar/index.html'))

        for value, expected in examples:
            assert helpers.joinurl(*value) == expected

    @attest.test
    def expand(self):

        assert helpers.expand('/:foo/:bar/', {'foo': 1, 'bar': 2}) == '/1/2/'
        assert helpers.expand('/:foo/:spam/', {'foo': 1, 'bar': 2}) == '/1/spam/'
        assert helpers.expand('/:foo/', {'bar': 2}) == '/foo/'

        assert helpers.expand('/:slug.html', {'slug': 'foo'}) == '/foo.html'
        assert helpers.expand('/:slug.:slug.html', {'slug': 'foo'}) == '/foo.foo.html'

    @attest.test
    def paginate(self):

        X = type('X', (str, ), {'modified': True}); refs.load()

        res = ['1', 'asd', 'asd123', 'egg', 'spam', 'ham', '3.14', '42']
        res = [X(val) for val in res]

        # default stuff
        assert list(helpers.paginate(res, 4)) == \
            [((None, 1, 2), res[:4], True), ((1, 2, None), res[4:], True)]
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

    @attest.test
    def safe(self):

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

        assert helpers.safe('[foo][bar] Baz') == '"[foo][bar] Baz"'

    @attest.test
    def system(self):

        examples = ((['echo', 'ham'], None, 'ham'),
                    ('cat', 'foo', 'foo'),
            )
        for cmd, stdin, expected in examples:
            assert helpers.system(cmd, stdin) == expected

        with attest.raises(AcrylamidException):
            helpers.system('false')

        with attest.raises(OSError):
            helpers.system('foo', None)
