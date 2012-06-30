# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import io

try:
    import docutils
except ImportError:
    docutils = None  # NOQA

from acrylamid.readers import reststyle, markdownstyle


class TestStyles(unittest.TestCase):

    @unittest.skipIf(docutils is None, 'no docutils available')
    def test_rest(self):

        header = ["Header",
        "======",
        "",
        ":date: 2001-08-16",
        ":version: 1",
        ":draft: True",
        ":authors: foo, bar",
        ":indentation: Since the field marker may be quite long, the second",
        "   and subsequent lines of the field body do not have to line up",
        "   with the first line, but they must be indented relative to the",
        "   field name marker, and they must line up with each other.",
        ":parameter i: integer",
        "",
        "Hello *World*."]

        i, meta = reststyle(io.StringIO(u'\n'.join(header)))
        assert i == len(header) - 1

        assert 'foo' in meta['authors']
        assert meta['version'] == 1
        assert meta['date'] == '2001-08-16'
        assert 'second and subsequent' in meta['indentation']
        assert meta['draft'] is True

    def test_mkdown(self):

        header = ["Title:   My Document",
        "Summary: A brief description of my document.",
        "Authors: Waylan Limberg",
        "         John Doe",
        "Date:    October 2, 2007",
        "blank-value: ",
        "base_url: http://example.com",
        "",
        "This is the first paragraph of the document."]

        i, meta = markdownstyle(io.StringIO(u'\n'.join(header)))
        assert i == len(header) - 1

        assert 'John Doe' in meta['authors']
        assert meta['date'] == 'October 2, 2007'
        assert meta['blank-value'] == None
