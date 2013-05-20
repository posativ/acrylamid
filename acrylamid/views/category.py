# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from itertools import chain

from acrylamid.views.index import Index, Paginator
from acrylamid.helpers import expand


def fetch(tree):

    for item in tree[1]:
        yield item

    for subtree in tree[0].values():
        for item in fetch(subtree):
            yield item


def recurse(category, tree):

    yield category, sorted(list(fetch(tree)), key=lambda k: k.date, reverse=True)

    for subtree in tree[0].items():
        for item in recurse(category + '/' + subtree[0], subtree[1]):
            yield item


class Category(Index):

    export = ['prev', 'curr', 'next', 'items_per_page', 'category', 'entrylist']
    template = 'main.html'

    tree = ({}, [])

    def context(self, conf, env, data):

        for entry in data['entrylist']:
            node = self.tree

            for i, category in enumerate(entry.category):

                if i < len(entry.category) - 1:
                    if category in node:
                        node = node[category]
                    else:
                        node = node[0].setdefault(category, ({}, []))
                else:
                    node[0].setdefault(category, ({}, []))[1].append(entry)

        class Link:

            def __init__(self, title, href):
                self.title = title
                self.href = href if href.endswith('/') else href + '/'

        def categorize(category):
            for i, name in enumerate(category):
                rv = '/'.join(category[:i] + [name])
                yield Link(rv, expand(self.path, {'name': rv}))

        env.engine.register('categorize', categorize)
        return env

    def generate(self, conf,env, data):

        iterator = chain(*map(lambda args: recurse(*args), self.tree[0].items()))

        for category, entrylist in iterator:
            data['entrylist'] = entrylist
            for res in Paginator.generate(self, conf, env, data,
                                          category=category, name=category):
                yield res
