# -*- encoding: utf-8 -*-

import unittest
from nose.exc import SkipTest

from acrylamid.lib import importer
from acrylamid import log

log.init('acrylamid', 20)


class TestImport(unittest.TestCase):

    def test_unescape(self):

        assert importer.unescape('&lt;p&gt;Foo&lt;/p&gt;') == '<p>Foo</p>'
        assert importer.unescape('Some Text/') == 'Some Text/'

    def test_conversion(self):

        md = 'Hello _[World](http://example.com/)!_'
        rst = 'Hello *`World <http://example.com/>`_!*'
        html = '<p>Hello <em><a href="http://example.com/">World</a>!</em></p>'

        try:
            import html2text
        except ImportError:
            raise SkipTest

        assert importer.convert(html, fmt='Markdown') == (md, 'markdown')
        assert importer.convert(html, fmt='reStructuredText') == (rst, 'rst')
        assert importer.convert(html, fmt='HTML') == (html, 'html')

        assert importer.convert('', fmt='Markdown') == ('', 'markdown')
        assert importer.convert(None, fmt='Markdown') == ('', 'markdown')
