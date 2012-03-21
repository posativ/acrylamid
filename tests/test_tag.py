# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA

from acrylamid.views import tag


class TestTag(unittest.TestCase):

    def test_tagcloud(self):

        tags = {'foo': range(1), 'bar': range(2)}
        cloud = tag.Tagcloud(tags, steps=4, max_items=100, start=0)
        lst = [(t.name, t.step) for t in cloud]

        self.assertIn(('foo', 3), lst)
        self.assertIn(('bar', 0), lst)

        tags = {'foo': range(1), 'bar': range(2), 'baz': range(4), 'spam': range(8)}
        cloud = tag.Tagcloud(tags, steps=4, max_items=4, start=0)
        lst = [(t.name, t.step) for t in cloud]

        self.assertIn(('foo', 3), lst)
        self.assertIn(('bar', 2), lst)
        self.assertIn(('baz', 1), lst)
        self.assertIn(('spam', 0), lst)
