# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from itertools import chain

from acrylamid.views.index import Index, Paginator
from acrylamid.compat import itervalues, iteritems
from acrylamid.helpers import expand, safeslug


def fetch(tree):
    """fetch all posts from the tree"""

    for item in tree[1]:
        yield item

    for subtree in itervalues(tree[0]):
        for item in fetch(subtree):
            yield item


def recurse(category, tree):

    yield category, sorted(list(fetch(tree)), key=lambda k: k.date, reverse=True)

    for subtree in iteritems(tree[0]):
        for item in recurse(category + '/' + safeslug(subtree[0]), subtree[1]):
            yield item


class Top(object):
    """Top-level category node without a category at all.  Iterable and yields
    sub categories that are also iterable up to the very last sub category."""

    def __init__(self, tree, route):
        self.tree = tree
        self.route = route
        self.parent = []

    def __iter__(self):
        for category, subtree in sorted(iteritems(self.tree[0]), key=lambda k: k[0]):
            yield Subcategory(self.parent + [category], category, subtree, self.route)

    def __bool__(self):
        return len(self) > 0

    @property
    def items(self):
        return list(fetch(self.tree))

    @property
    def href(self):
        return expand(self.route, {'name': ''})


class Subcategory(Top):

    def __init__(self, parent, category, tree, route):
        self.parent = parent
        self.title = category
        self.tree = tree
        self.route = route

    def __str__(self):
        return self.title

    @property
    def href(self):
        return expand(self.route, {'name': '/'.join(map(safeslug, self.parent))})


class Category(Index):

    export = ['prev', 'curr', 'next', 'items_per_page', 'category', 'entrylist']
    template = 'main.html'

    def context(self, conf, env, data):

        self.tree = ({}, [])

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
        env.categories = Top(self.tree, self.path)
        return env

    def generate(self, conf,env, data):

        iterator = chain(*map(lambda args: recurse(*args), iteritems(self.tree[0])))

        for category, entrylist in iterator:
            data['entrylist'] = entrylist
            for res in Paginator.generate(self, conf, env, data,
                                          category=category, name=category):
                yield res
