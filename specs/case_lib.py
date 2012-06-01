# -*- coding: utf-8 -*-

from acrylamid.lib import HTMLParser
f = lambda x: ''.join(HTMLParser(x).result)

describe 'internal HTMLParser':

    it 'handles start tags correctly':

        examples = [
            '<p></p>',
            '<p id="foo"></p>',
            '<script src="/js/foo.js" type="text/javascript"></script>',
            '<iframe allowfullscreen></iframe>',
        ]

        for ex in examples:
            assert f(ex) == ex

    it 'does not touch data':
        assert f('<p>Data!1</p>') == '<p>Data!1</p>'

    it 'handles end tag correctly':

        examples = [
            '<p></p></p>',
            '</p>'*3,
        ]

        for ex in examples:
            assert f(ex) == ex

    it 'handles startend tags correctly':

        for ex in ['<br />',  '<link id="foo" attr="bar"/>']:
            assert f(ex) == ex

    it 'keeps entitiyrefs':

        assert f('<span>&amp;</span>') == '<span>&amp;</span>'
        assert f('<span>&foo;</span>') == '<span>&foo;</span>'

    it 'keeps charrefs':

        assert f('<span>&#1234;</span>') == '<span>&#1234;</span>'
