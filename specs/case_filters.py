# -*- coding: utf-8 -*-

import re

from acrylamid.filters import FilterList
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
