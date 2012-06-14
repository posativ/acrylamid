# -*- coding: utf-8 -*-

import unittest

from acrylamid.lib.html import HTMLParser
f = lambda x: ''.join(HTMLParser(x).result)


class  TestHTMLParser(unittest.TestCase):

    def test_starttag(self):

        examples = [
            '<p></p>',
            '<p id="foo"></p>',
            '<script src="/js/foo.js" type="text/javascript"></script>',
            '<iframe allowfullscreen></iframe>',
        ]

        for ex in examples:
            assert f(ex) == ex

    def test_data(self):
        assert f('<p>Data!1</p>') == '<p>Data!1</p>'

    def test_endtag(self):

        examples = [
            '<p></p></p>',
            '</p>'*3,
        ]

        for ex in examples:
            assert f(ex) == ex

    def test_startendtag(self):

        for ex in ['<br />',  '<link id="foo" attr="bar"/>']:
            assert f(ex) == ex

    def test_entityrefs(self):

        assert f('<span>&amp;</span>') == '<span>&amp;</span>'
        assert f('<span>&foo;</span>') == '<span>&foo;</span>'

    def test_charrefs(self):

        assert f('<span>&#1234;</span>') == '<span>&#1234;</span>'
