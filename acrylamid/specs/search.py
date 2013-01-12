# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import attest

tt = attest.Tests()
from acrylamid.views import search


@tt.test
def commonprefix():

    for a, b, i in  ('foo', 'faa', 1), ('test', 'test', 4), ('', 'spam', 0), ('a', 'b', 0):
        assert search.commonprefix(a, b) == (i, b)


@tt.test
def basics():

    tree = {}
    for word in 'javascript', 'java', 'java-vm':
        search.insert(tree, word, 1)

    assert 'j' in tree
    assert 'ava' in tree['j'][0]
    assert 'script' in tree['j'][0]['ava'][0]
    assert '-vm' in tree['j'][0]['ava'][0]

    assert len(tree['j'][0]['ava']) == 2  # Java found!
    assert len(tree['j'][0]['ava'][0]['script']) == 2  # JavaScript found!
    assert len(tree['j'][0]['ava'][0]['-vm']) == 2  # Java-VM found!


@tt.test
def split():

    tree = {}
    for word in 'a', 'aa', 'aaa', 'aaaa', 'ab':
        search.insert(tree, word, 1)

    assert 'a' in tree
    assert 'a' in tree['a'][0]
    assert 'a' in tree['a'][0]['a'][0]
    assert 'a' in tree['a'][0]['a'][0]['a'][0]
    assert 'b' in tree['a'][0]

    assert len(tree['a']) == 1  # search word must be longer than three chars ;)
    assert len(tree['a'][0]['a']) == 2
    assert len(tree['a'][0]['b']) == 2
    assert len(tree['a'][0]['a'][0]['a']) == 2
    assert len(tree['a'][0]['a'][0]['a'][0]['a']) == 2


@tt.test
def advanced():

    def find(node, i):
        if len(node) == 2 and node[1] == i:
            yield i

        for key in node[0]:
            yield find(node[0][key], i)

    tree = {}
    words = 'eines', 'erwachte', 'er', 'einem', 'ein', 'erhalten', 'es', \
            'etwas', 'eine', 'einer', 'entgegenhob'

    for i, word in enumerate(words):
        search.insert(tree, word, i)

    for i in range(len(word)):
        assert len(list(find((tree, -1), i))) == 1

if __name__ == '__main__':

    tt.run()
