# -*- encoding: utf-8 -*-

import unittest
from nose.exc import SkipTest

import argparse

from acrylamid import log, tasks

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

        assert imprt.convert(html, fmt='Markdown') == (md, 'markdown')
        assert imprt.convert(html, fmt='reStructuredText') == (rst, 'rst')
        assert imprt.convert(html, fmt='HTML') == (html, 'html')

        assert imprt.convert('', fmt='Markdown') == ('', 'markdown')
        assert imprt.convert(None, fmt='Markdown') == ('', 'markdown')
