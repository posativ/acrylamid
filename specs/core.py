# -*- coding: utf-8 -*-

import attest
from acrylamid.core import cache


class Cache(attest.TestBase):

    def __context__(self):
        with attest.tempdir() as path:
            self.path = path
            cache.init(self.path)

        yield

    @attest.test
    def persistence(self):

        cache.init(self.path)
        cache.set('foo', 'bar', "Hello World!")
        cache.set('foo', 'baz', "spam")
        assert cache.get('foo', 'bar') == "Hello World!"
        assert cache.get('foo', 'baz') == "spam"

        cache.shutdown()
        cache.init(self.path)
        assert cache.get('foo', 'bar') == "Hello World!"
        assert cache.get('foo', 'baz') == "spam"

    @attest.test
    def remove(self):

        cache.init(self.path)
        cache.set('foo', 'bar', 'baz')
        cache.remove('foo')
        cache.remove('invalid')

        assert cache.get('foo', 'bar') == None
        assert cache.get('invalid', 'bla') == None

    @attest.test
    def clear(self):

        cache.init(self.path)
        cache.set('foo', 'bar', 'baz')
        cache.set('spam', 'bar', 'baz')

        cache.clear()
        assert cache.get('foo', 'bar') == None
        assert cache.get('spam', 'bar') == None
