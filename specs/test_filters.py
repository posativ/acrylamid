# -*- coding: utf-8 -*-

import unittest
import re

from acrylamid.filters import FilterList, FilterTree
from acrylamid.filters import Filter, disable


def build(name, **kw):
    return type(name, (Filter, ), kw)({}, {}, name)


class TestFilterlist(unittest.TestCase):

    def test_plain_strings(self):

        f1 = build('F1', match=['foo', 'bar'], conflicts=['spam'])
        f2 = build('F2', match=['spam'])
        f3 = build('F3', match=['bla'])

        x = FilterList([f1])

        assert f1 in x
        assert f2 in x
        assert f3 not in x

    def test_regex_strings(self):

        f1 = build('F1', match=['foo', 'bar'], conflicts=['spam'])
        f2 = build('F2', match=[re.compile('^spam$')])
        f3 = build('F3', match=['bla'])

        x = FilterList([f1])

        assert f1 in x
        assert f2 in x
        assert f3 not in x

    def test_conflicts(self):

        f1 = build('F1', match=['foo', 'bar'], conflicts=['spam'])
        f4 = build('F4', match=['baz'], conflicts=['foo'])

        x = FilterList([f1])

        assert f1 in x
        assert f4 in x

    def test_access_by_name(self):

        f3 = build('F3', match=[re.compile('^sp', re.I)])
        x = FilterList([f3])

        assert x['sp'] == f3
        assert x['spam'] == f3
        assert x['sPaMmEr'] == f3

    def test_disable(self):

        f1 = build('F1', match=['Foo'], conflicts=['Bar'])
        f2 = disable(f1)

        assert hash(f1) != hash(f2)
        assert f1.match != f2.match

        assert f1.name == f2.name
        assert f1.conflicts == f2.conflicts


class TestFilterTree(unittest.TestCase):

    def test_path(self):

        t = FilterTree()
        t.add([1, 3, 4, 7], 'foo')
        assert t.path('foo') == [1, 3, 4, 7]


    def test_works(self):

        t = FilterTree()

        t.add([1, 2, 5], 'foo')
        t.add([1, 2, 3, 5], 'bar')
        t.add([7, ], 'baz')

        assert list(t.iter('foo')) == [[1, 2], [5, ]]
        assert list(t.iter('bar')) == [[1, 2], [3, 5]]
        assert list(t.iter('baz')) == [[7, ], ]

    def test_edge_cases(self):

        t = FilterTree()

        t.add([1, 2], 'foo')
        t.add([1, 2], 'bar')
        t.add([2, ], 'baz')

        assert list(t.iter('foo')) == [[1, 2], ]
        assert list(t.iter('bar')) == [[1, 2], ]
        assert list(t.iter('baz')) == [[2, ], ]
