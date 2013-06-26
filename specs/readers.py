# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import io
import attest

tt = attest.Tests()
from acrylamid.readers import reststyle, markdownstyle, distinguish, ignored
from acrylamid.readers import pandocstyle


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
    assert meta['blank-value'] == ""


@tt.test
def pandoc():

    header = ["% title",
    "% Author; Another",
    "% June 15, 2006",
    "",
    "Here comes the regular text"]

    i, meta = pandocstyle(io.StringIO('\n'.join(header)))
    assert i == len(header) - 1

    assert 'Another' in meta['author']
    assert meta['date'] == 'June 15, 2006'


@tt.test
def quotes():

    assert distinguish('"') == '"'
    assert distinguish('""') == ''

    assert distinguish('Foo"') == 'Foo"'
    assert distinguish('"Foo') == '"Foo'

    assert distinguish('"Foo" Bar') == '"Foo" Bar'
    assert distinguish('"Foo Bar"') == 'Foo Bar'

    assert distinguish("\"'bout \" and '\"") == "'bout \" and '"

    # quote commas, so they are not recognized as a new part
    assert distinguish('["X+ext(foo, bar=123)", other]') == ["X+ext(foo, bar=123)", "other"]
    assert distinguish('["a,b,c,d", a, b, c]') == ['a,b,c,d', 'a', 'b', 'c']

    # # shlex tokenizer should not split on "+"
    assert distinguish("[X+Y]") == ["X+Y"]

    # non-ascii
    assert distinguish('["Föhn", "Bär"]') == ["Föhn", "Bär"]
    assert distinguish('[Bla, Calléjon]') == ["Bla", "Calléjon"]
    assert distinguish('[да, нет]') == ["да", "нет"]


@tt.test
def types():

    for val in ['None', 'none', '~', 'null']:
        assert distinguish(val) == None

    for val in ['3.14', '42.0', '-0.01']:
        assert distinguish(val) == float(val)

    for val in ['1', '2', '-1', '9000']:
        assert distinguish(val) == int(val)

    assert distinguish('test') == 'test'
    assert distinguish('') == ''


@tt.test
def backslash():

    assert distinguish('\\_bar') == '_bar'
    assert distinguish('foo\\_') == 'foo_'
    assert distinguish('foo\\\\bar') == 'foo\\bar'


@tt.test
def ignore():

    assert ignored('/path/', 'foo', ['foo', 'fo*', '/foo'], '/path/')
    assert ignored('/path/', 'dir/', ['dir', 'dir/'], '/path/')
    assert not ignored('/path/to/', 'baz/', ['/baz/', '/baz'], '/path/')

    assert ignored('/', '.git/info/refs', ['.git*'], '/')
    assert ignored('/', '.gitignore', ['.git*'], '/')

    assert ignored('/', '.DS_Store', ['.DS_Store'], '/')
