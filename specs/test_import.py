# -*- encoding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import io
from os.path import join, dirname

from nose.exc import SkipTest
from acrylamid import log, tasks, helpers

log.init('acrylamid', 20)
tasks.task = lambda x,y,z: lambda x: x

from acrylamid.tasks import imprt

read = lambda path: io.open(join(dirname(__file__), 'samples', path), encoding='utf-8').read()
wordpress = read('thethreedevelopers.wordpress.2012-04-11.xml')
rss = read('blog.posativ.org.xml')
atom = read('vlent.nl.xml')


class TestImport(unittest.TestCase):

    def test_unescape(self):

        assert imprt.unescape('&lt;p&gt;Foo&lt;/p&gt;') == '<p>Foo</p>'
        assert imprt.unescape('Some Text/') == 'Some Text/'

    def test_conversion(self):

        md = 'Hello _[World](http://example.com/)!_'
        rst = 'Hello *`World <http://example.com/>`_!*'
        html = '<p>Hello <em><a href="http://example.com/">World</a>!</em></p>'

        try:
            import html2text
        except ImportError:
            raise SkipTest

        try:
            import html2rest
        except ImportError:
            try:
                helpers.system(['which', 'pandoc'])
            except:
                raise SkipTest
        else:
            raise SkipTest

        assert imprt.convert(html, fmt='Markdown') == (md, 'markdown')
        assert imprt.convert(html, fmt='reStructuredText') == (rst, 'rst')
        assert imprt.convert(html, fmt='HTML') == (html, 'html')

        assert imprt.convert('', fmt='Markdown') == ('', 'markdown')
        assert imprt.convert(None, fmt='Markdown') == ('', 'markdown')


class TestRSS(unittest.TestCase):

    def test_recognition(self):

        examples = [
            'baz',
            '<?xml version="1.0" encoding="utf-8"?>' \
            + '<rss version="1.0" xmlns:atom="http://www.w3.org/2005/Atom">' \
            + '</rss>',
            wordpress, atom
        ]

        for value in examples:
            with self.assertRaises(imprt.InputError):
                imprt.rss(value)

        imprt.rss(rss)

    def test_defaults(self):

        defaults, items = imprt.rss(rss)

        assert defaults['sitename'] == 'mecker. mecker. mecker.'
        assert defaults['www_root'] == 'http://blog.posativ.org/'

        assert len(items) == 1

    def test_first_entry(self):

        defaults, items = imprt.rss(rss)
        entry = items[0]

        for key in 'title', 'content', 'link', 'date', 'tags':
            assert key in entry

        assert len(entry['tags']) == 2


class TestAtom(unittest.TestCase):

    def test_recognition(self):

        examples = [
            'bar',
            '<?xml version="1.0" encoding="utf-8"?>' \
            + '<feed xmlns="http://invalid.org/" xml:lang="de">' \
            + '</feed>',
            wordpress, rss
        ]

        for value in examples:
            with self.assertRaises(imprt.InputError):
                imprt.atom(value)

        imprt.atom(atom)

    def test_defaults(self):

        defaults, items = imprt.atom(atom)

        assert defaults['sitename'] == "Mark van Lent's weblog"
        assert defaults['author'] == 'Mark van Lent'
        assert defaults['www_root'] == 'http://www.vlent.nl/weblog/'

        assert len(items) == 1

    def test_first_entry(self):

        defaults, items = imprt.atom(atom)
        entry = items[0]

        for key in 'title', 'content', 'link', 'date', 'tags':
            assert key in entry

        assert len(entry['tags']) == 2
