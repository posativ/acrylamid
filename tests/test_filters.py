# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA

import sys
import re

from acrylamid.filters import FilterList
from acrylamid.filters import Filter


def build(name, **kw):
    return type(name, (Filter, ), kw)({}, {}, name)


class TestFilters(unittest.TestCase):

    def setUp(self):
        pass

    def assertIn(self, x, y):
        if sys.version_info >= (2, 7):
            super(TestFilters, self).assertIn(x, y)
        else:
            self.assertTrue(x in y)

    def assertNotIn(self, x, y):
        if sys.version_info >= (2, 7):
            super(TestFilters, self).assertNotIn(x, y)
        else:
            self.assertTrue(x not in y)

    def test_FilterList(self):

        f1 = build('F1', match=['foo', 'bar'], conflicts=['spam'])
        f2 = build('F2', match=['spam'])
        f3 = build('F3', match=['bla'])

        # test plain strings
        x = FilterList([f1])

        self.assertIn(f1, x)
        self.assertIn(f2, x)
        self.assertNotIn(f3, x)

        # test with regular expression in match
        f2 = build('F2', match=[re.compile('^spam$')])
        x = FilterList([f1])

        self.assertIn(f1, x)
        self.assertIn(f2, x)
        self.assertNotIn(f3, x)

        # test y.conflicts in filter.match in list

        f4 = build('F4', match=['baz'], conflicts=['foo'])
        x = FilterList([f1])

        self.assertIn(f1, x)
        self.assertIn(f4, x)

        # test __getitem__
        f3 = build('F3', match=[re.compile('^sp', re.I)])
        x = FilterList([f3])

        self.assertEqual(x['sp'], f3)
        self.assertEqual(x['spam'], f3)
        self.assertEqual(x['sPaMmEr'], f3)
