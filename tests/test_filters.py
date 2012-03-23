# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA

from acrylamid.filters import FilterList
from acrylamid.filters import md

class TestFilters(unittest.TestCase):

    def setUp(self):
        pass

    def test_FilterList(self):

        x = FilterList()
        f1 = ('myfilter', md, ())