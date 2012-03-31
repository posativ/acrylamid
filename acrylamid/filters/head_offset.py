# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from acrylamid.filters import Filter
from re import sub


class Headoffset(Filter):

    match = ['h' + str(i + 1) for i in range(5)]
    conflicts = ['h' + str(i + 1) for i in range(5)]

    def transform(self, text, entry, *args):

        def f(m):
            '''will return html with all headers increased by 1'''
            l = lambda i: i if i not in [str(x) for x in range(1, 6)] \
                            else str(int(i) + 1) if int(i) < 5 else '6'
            return ''.join([l(i) for i in m.groups()])

        offset = int(self.name[1])

        for i in range(offset):
            text = sub('(<h)(\d)(>)(.+)(</h)(\d)(>)', f, text)

        return text
