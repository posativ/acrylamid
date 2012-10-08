# -*- encoding: utf-8 -*-

import io
import unittest

from os.path import join, dirname

from nose.exc import SkipTest
from acrylamid import log, tasks, helpers

log.init('acrylamid', 20)
tasks.task = lambda x,y,z: lambda x: x

from acrylamid.tasks import imprt


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

        with self.assertRaises(imprt.InputError):
            imprt.rss20('baz')
            imprt.rss20('<?xml version="1.0" encoding="utf-8"?>' \
                      + '<rss version="1.0" xmlns:atom="http://www.w3.org/2005/Atom">' \
                      + '</rss>')


class TestAtom(unittest.TestCase):

    def test_recognition(self):

        with self.assertRaises(imprt.InputError):
            imprt.atom('bar')
            imprt.atom('<?xml version="1.0" encoding="utf-8"?>' \
                     + '<feed xmlns="http://invalid.org/" xml:lang="de">' \
                     + '</feed>')
