# -*- coding: utf-8 -*-

from attest import test, TestBase

from acrylamid.lib.html import HTMLParser

f = lambda x: ''.join(HTMLParser(x).result)


class TestHTMLParser(TestBase):

    @test
    def starttag(self):

        examples = [
            '<p></p>',
            '<p id="foo"></p>',
            '<script src="/js/foo.js" type="text/javascript"></script>',
            '<iframe allowfullscreen></iframe>',
        ]

        for ex in examples:
            assert f(ex) == ex

    @test
    def data(self):
        assert f('<p>Data!1</p>') == '<p>Data!1</p>'

    @test
    def endtag(self):

        examples = [
            '<p></p></p>',
            '</p>'*3,
        ]

        for ex in examples:
            assert f(ex) == ex

    @test
    def startendtag(self):

        for ex in ['<br />',  '<link id="foo" attr="bar"/>']:
            assert f(ex) == ex

    @test
    def entityrefs(self):

        assert f('<span>&amp;</span>') == '<span>&amp;</span>'
        assert f('<span>&foo;</span>') == '<span>&foo;</span>'

    @test
    def charrefs(self):

        assert f('<span>&#1234;</span>') == '<span>&#1234;</span>'
