# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA

from acrylamid.lib import HTMLParser
f = lambda x: ''.join(HTMLParser(x).result)


class TestHTMLParser(unittest.TestCase):

    def test_starttag(self):

        examples = [
            '<p></p>',
            '<p id="foo"></p>',
            '<script src="/js/foo.js" type="text/javascript"></script>',
            '<iframe allowfullscreen></iframe>',
        ]

        for example in examples:
            self.assertEqual(f(example), example)

    def test_data(self):
        assert f('<p>Data!1</p>') == '<p>Data!1</p>'

    def test_endtag(self):

        examples = [
            '<p></p></p>',
            '</p>'*3,
        ]

        for example in examples:
            self.assertEqual(f(example), example)

    def test_startendtag(self):

        examples = [
            '<br />',
            '<link id="foo" attr="bar"/>'
        ]

        for example in examples:
            self.assertEqual(f(example), example)

    def test_entityref(self):

        self.assertEqual(f('<span>&amp;</span>'), '<span>&amp;</span>')
        self.assertEqual(f('<span>&foo;</span>'), '<span>&foo;</span>')

    def test_charref(self):

        self.assertEqual(f('<span>&#1234;</span>'), '<span>&#1234;</span>')
