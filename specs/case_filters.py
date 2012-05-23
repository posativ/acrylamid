# -*- coding: utf-8 -*-

import re

from acrylamid.filters import FilterList, FilterTree
from acrylamid.filters import Filter


def build(name, **kw):
    return type(name, (Filter, ), kw)({}, {}, name)


describe 'FilterList':

    it 'works with plain strings':

        f1 = build('F1', match=['foo', 'bar'], conflicts=['spam'])
        f2 = build('F2', match=['spam'])
        f3 = build('F3', match=['bla'])

        x = FilterList([f1])

        assert f1 in x
        assert f2 in x
        assert f3 not in x

    it 'matches also with a regular expression':

        f1 = build('F1', match=['foo', 'bar'], conflicts=['spam'])
        f2 = build('F2', match=[re.compile('^spam$')])
        f3 = build('F3', match=['bla'])

        x = FilterList([f1])

        assert f1 in x
        assert f2 in x
        assert f3 not in x

    it 'conflicts within a match already in the list':

        f1 = build('F1', match=['foo', 'bar'], conflicts=['spam'])
        f4 = build('F4', match=['baz'], conflicts=['foo'])

        x = FilterList([f1])

        assert f1 in x
        assert f4 in x

    it 'we can access filters by name':

        f3 = build('F3', match=[re.compile('^sp', re.I)])
        x = FilterList([f3])

        assert x['sp'] == f3
        assert x['spam'] == f3
        assert x['sPaMmEr'] == f3


describe 'FilterTree':

    it 'remembers path correctly':

        t = FilterTree()
        t.add([1, 3, 4, 7], 'foo')
        assert t.path('foo') == [1, 3, 4, 7]


    it 'works as expected':

        t = FilterTree()

        t.add([1, 2, 5], 'foo')
        t.add([1, 2, 3, 5], 'bar')
        t.add([7, ], 'baz')

        assert list(t.iter('foo')) == [[1, 2], [5, ]]
        assert list(t.iter('bar')) == [[1, 2], [3, 5]]
        assert list(t.iter('baz')) == [[7, ], ]

    it 'handles edge cases':

        t = FilterTree()

        t.add([1, 2], 'foo')
        t.add([1, 2], 'bar')
        t.add([2, ], 'baz')

        assert list(t.iter('foo')) == [[1, 2], ]
        assert list(t.iter('bar')) == [[1, 2], ]
        assert list(t.iter('baz')) == [[2, ], ]
