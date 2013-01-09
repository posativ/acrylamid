# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

"""
Static Site Search
~~~~~~~~~~~~~~~~~~

A full text search using compressed `suffix trees`_ (CST).  In comparison to a
single index file like in Sphinx_ this has several advantages:

  - O(1/27 * n log n) instead of O(n) space efficency (one character prefix versus index)
  - full text search with no arbitrary limitation of the character set
  - finds all exact matches and substrings in O(log n)

For the record (index for aroun 170 posts):

  - JSON index with no special characters allowed (such as dash): 375k (132k gzipped)
  - CST  index with special characters (except punctuation): 42k (12k gzipped) per prefix

So, what is a prefix?  The idea is, that a user does mainly search for a single
term and a single prefix such as `python` where `p` is a prefix of the term and
in a suffix tree we can construct in O(n * log n) for a constant size alphabet.
As alphabet, we use 26 lowercase ascii characters and a tree for everything
else, hence O(1/27 * n log n) space efficency per sub tree, which is better
that O(n) in practise (see the numbers above).

When the user now enters a search term, the browser only needs to load the sub
tree that contains all suffixes for this term, in average 42k (12 gzipped) with
much more search features \o/.

.. _suffix trees: https://en.wikipedia.org/wiki/Suffix_tree
.. _Sphinx: http://sphinx-doc.org/"""

import re
import io
import json
import string

from os.path import join, dirname
from collections import defaultdict

from acrylamid.views import View
from acrylamid.helpers import joinurl


def commonprefix(a, b):
    """Find longest common prefix of `a` and `b`."""

    pos = 0
    length = min(len(a), len(b))

    while pos < length and a[pos] == b[pos]:
        pos += 1

    return pos, b


def insert(tree, word, refs):

    # get top-level node
    node, prev = tree.setdefault(word[0], ({}, )), None

    i = 0
    while i < len(word) - 1:

        try:
            index, prefix = max(commonprefix(word[i+1:], key) for key in node[0]
                if word[i+1] == key[0])
        except ValueError:
            index, prefix = 0, None

        if prefix and index == len(prefix) and index != len(word[i+1:]):
            prev, node = node, node[0][prefix]
            i += index

        # has common sub prefix, retain compression
        elif 0 < index < len(prefix):

            rv = node[0].pop(prefix)
            a, b = prefix[:index], prefix[index:]

            i += len(a)

            node[0][a] = ({b: rv}, )
            node, prev = node[0][a], node

            if i == len(word) - 1:
                prev[0][a] = (node[0], refs)
                break

        # not yet saved, append
        else:
            node[0][word[i+1:]] = (node[0].get(word[i+1:], ({}, ))[0], refs)
            break


def index(entrylist):
    """Build compressed suffix tree in something around O(n * log(n)), but with
    huge time constants. It is *really* slow but more space efficient, hopefully."""

    tree, meta = {}, []
    words = defaultdict(set)

    for num, entry in enumerate(entrylist):
        meta.append((entry.permalink, entry.title))

        for word in re.split(r"[.:,\s!?=\(\)]+", entry.content):
            if len(word) < 3:
                continue
            for i in range(len(word) - 3):
                words[word[i:].lower()].add(num)

    for key, value in words.iteritems():
        insert(tree, key, list(value))

    del words
    return tree, meta


class Search(View):

    def generate(self, conf, env, request):

        if not env.options.search:
            raise StopIteration()

        tree, meta = index(request['entrylist'])

        for i, entry in enumerate(request['entrylist']):
            yield io.StringIO(entry.content), \
                  joinurl(conf['output_dir'], self.path, 'src', '%i.txt' % i)

        # CST algorithm with `meta` data
        with io.open(join(dirname(__file__), 'search.js')) as fp:
            javascript = fp.read()

        fp = io.StringIO((javascript
            .replace('%% PATH %%', json.dumps(self.path))
            .replace('%% ENTRYLIST %%', json.dumps(meta))))
        yield fp, joinurl(conf['output_dir'], self.path, 'search.js')

        for char in string.ascii_lowercase:
            if char in tree:
                fp = io.BytesIO()
                json.dump(tree.pop(char), fp)

                yield fp, joinurl(conf['output_dir'], self.path, char + '.js')

        fp = io.BytesIO()
        json.dump(tree, fp)
        yield fp, joinurl(conf['output_dir'], self.path, '_.js')
