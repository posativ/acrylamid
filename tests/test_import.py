# -*- encoding: utf-8 -*-

import sys; reload(sys)
sys.setdefaultencoding('utf-8')

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA

from acrylamid.lib import importer
from acrylamid import log
from subprocess import check_output

log.init('acrylamid', 20)


class TestUtils(unittest.TestCase):

    def test_unescape(self):

        self.assertEquals(importer.unescape('&lt;p&gt;Foo&lt;/p&gt;'), '<p>Foo</p>')
        self.assertEquals(importer.unescape('Some Text/'), 'Some Text/')

    def test_convert(self):

        md = 'Hello *[World](http://example.com/)!*'
        rst = 'Hello *`World <http://example.com/>`_!*'
        html = '<p>Hello <em><a href="http://example.com/">World</a>!</em></p>'

        self.assertEquals(importer.convert(html, fmt='Markdown'), (md, 'markdown'))
        self.assertEquals(importer.convert(html, fmt='reStructuredText'), (rst, 'rst'))
        self.assertEquals(importer.convert(html, fmt='HTML'), (html, 'html'))

        self.assertEquals(importer.convert('', fmt='Markdown'), ('', 'markdown'))
        self.assertEquals(importer.convert(None, fmt='Markdown'), ('', 'markdown'))

    def test_rss20(self):

        pass
