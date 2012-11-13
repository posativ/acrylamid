# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import io
import attest

tt = attest.Tests()
from acrylamid.readers import reststyle, markdownstyle, distinguish, ignored


@tt.test
def rest():

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

    i, meta = reststyle(io.StringIO('\n'.join(header)))
    assert i == len(header) - 1

    assert 'foo' in meta['authors']
    assert meta['version'] == 1
    assert meta['date'] == '2001-08-16'
    assert 'second and subsequent' in meta['indentation']
    assert meta['draft'] is True


@tt.test
def mkdown():

    header = ["Title:   My Document",
    "Summary: A brief description of my document.",
    "Authors: Waylan Limberg",
    "         John Doe",
    "Date:    October 2, 2007",
    "blank-value: ",
    "base_url: http://example.com",
    "",
    "This is the first paragraph of the document."]

    i, meta = markdownstyle(io.StringIO('\n'.join(header)))
    assert i == len(header) - 1

    assert 'John Doe' in meta['authors']
    assert meta['date'] == 'October 2, 2007'
    assert meta['blank-value'] == None


@tt.test
def quotes():

    assert distinguish('"') == '"'
    assert distinguish('""') == ''

    assert distinguish('Foo"') == 'Foo"'
    assert distinguish('"Foo') == '"Foo'

    assert distinguish('"Foo" Bar') == '"Foo" Bar'
    assert distinguish('"Foo Bar"') == 'Foo Bar'

    assert distinguish("\"'bout \" and '\"") == "'bout \" and '"


@tt.test
def ignore():

    assert ignored('/path/', 'foo', ['foo', 'fo*', '/foo'], '/path/')
    assert ignored('/path/', 'dir/', ['dir', 'dir/'], '/path/')
    assert not ignored('/path/to/', 'baz/', ['/baz/', '/baz'], '/path/')

    assert ignored('/', '.git/info/refs', ['.git*'], '/')
    assert ignored('/', '.gitignore', ['.git*'], '/')

    assert ignored('/', '.DS_Store', ['.DS_Store'], '/')
