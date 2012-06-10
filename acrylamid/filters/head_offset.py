# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid.filters import Filter
from re import sub


class Headoffset(Filter):
    """This filter increases HTML headings by N whereas N is the suffix of
    this filter, e.g. `h2' increases headers by two."""

    version = '1.0.0'

    def transform(self, text, entry, *args):

        def f(m):
            i = int(m.group(1))+1
            return ''.join(['<h%i' % i, m.group(2), '>', m.group(3), '</h%i>' % i])

        for i in range(int(self.name[1])):
            text = sub(r'<h([12345])([^>]*)>(.+)</h\1>', f, text)

        return text


for offset in range(1, 6):
    var = 'h%i' % offset
    globals()[var] = type(var, (Headoffset, ), {
        'match': [var],
        'conflicts': ['h%i' % i for i in set([1, 2, 3, 4, 5]) - set([offset])]
    })
