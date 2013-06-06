# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from itertools import chain

from acrylamid.views.index import Index, Paginator
from acrylamid.helpers import expand, safeslug


def fetch(tree):
    """fetch all posts from the tree"""

    for item in tree[1]:
        yield item

    for subtree in tree[0].values():
        for item in fetch(subtree):
            yield item


def recurse(category, tree):

    yield category, sorted(list(fetch(tree)), key=lambda k: k.date, reverse=True)

    for subtree in tree[0].items():
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
        for category, subtree in sorted(self.tree[0].iteritems(), key=lambda k: k[0]):
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
    """A view to recursively render all posts of a category, sub category and
    so on. Configuration syntax:

    .. code-block:: python

        '/category/:name/': {
            'view': 'category',
            'pagination': '/category/:name/:num/'
        }

    Categories are either explicitly set in the metadata section
    (`category: foo/bar`) or derived from the path of the post, e.g.
    `content/projects/python/foo-bar.txt` will set the category to `projects/python`.

    .. code-block:: sh

        $ tree content/
        content/
        ├── projects
        │   ├── bla.txt
        │   └── python
        │       └── fuu.txt
        └── test
            └── sample-entry.txt

    The directory structure above then renders the following:

    .. code-block:: sh

        $ acrylamid compile
          create  [0.00s] output/category/test/index.html
          create  [0.00s] output/category/projects/index.html
          create  [0.00s] output/category/projects/python/index.html

    Both, bla.txt and fuu.txt are shown on the project listing, but only the
    fuu.txt post appears on the projects/python listing.

    Categories in the Entry Context
    -------------------------------

    To link to the category listing, use the following Jinja2 code instead of
    the tag code in the `entry.html` template:

    .. code-block:: html+jinja

       {% if 'category' in env.views and entry.category %}
           <p>categorized in
               {% for link in entry.category | categorize %}
                   <a href="{{ env.path + link.href }}">{{ link.title }}</a>
                   {%- if loop.revindex > 2 -%}
                   ,
                   {%- elif loop.revindex == 2 %}
                   and
                   {% endif %}
               {% endfor %}
           </p>

    This uses the new `categorize` filter which is available when you have the
    category view enabled. It takes the category list from `entry.category` and
    yields the hierarchical categories, e.g. projects/python yields projects and
    projects/python.

    Categories in the Environment Context
    -------------------------------------

    Similar to the tag cloud you are able to generate a category listing on
    each page: ``env.categories`` is an iterable object that yields categories
    (which are iterable as well and yield sub categories). The following Jinja2
    code recursively renders all categories and sub categories in a simple list:

    .. code-block:: html+jinja

        <ul class="categories">
        {% for category in env.categories recursive %}

            <li>Category: <a href="{{ category.href }}">{{ category.title }}</a>
                with {{ category.items | count }} articles.
            </li>

            {% if category %}
                <ul class="depth-{{ loop.depth }}">{{ loop(category) }}</ul>
            {% endif %}

        {% endfor %}
        </ul>


    .. versionadded:: 0.8

        Support for categories was introduced.
    """

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

        iterator = chain(*map(lambda args: recurse(*args), self.tree[0].items()))

        for category, entrylist in iterator:
            data['entrylist'] = entrylist
            for res in Paginator.generate(self, conf, env, data,
                                          category=category, name=category):
                yield res
