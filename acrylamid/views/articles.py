# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid.views import View
from acrylamid.helpers import union, joinurl, event, md5, memoize

from os.path import exists


class Articles(View):
    """Generates an overview of all articles using *layouts/articles.html* as
    default jinja2 template (`Example <http://blog.posativ.org/articles/>`_).

    To enable Articles view, add:

    .. code-block:: python

        '/articles/' : {
            'view': 'articles',
            'template': 'articles.html'  # default
        }

    to your :doc:`conf.py` where */articles/* is the default URL for this view.

    We filter articles that are drafts and add them to the *articles*
    dictionary using ``(entry.year, entry.imonth)`` as key. During templating
    we sort all keys by value, hence we get a listing of years > months > entries.

    Variables available during Templating:

    - *articles* containing the articles
    - *num_entries* count of articles
    - *conf*, *env*"""

    priority = 80.0

    def init(self, template='articles.html'):
        self.template = template

    def generate(self, request):

        entrylist = sorted((e for e in request['entrylist'] if not e.draft),
                        key=lambda k: k.date, reverse=True)

        tt = self.env.engine.fromfile(self.template)
        path = joinurl(self.conf['output_dir'], self.path, 'index.html')

        hv = md5(*entrylist, attr=lambda o: o.md5)
        rv = memoize('articles-hash')

        if rv == hv:
            has_changed = False
        else:
            # save new value for next run
            memoize('articles-hash', hv)
            has_changed = True

        if exists(path) and not has_changed and not tt.has_changed:
            event.skip(path)
            raise StopIteration

        articles = {}
        for entry in entrylist:
            articles.setdefault((entry.year, entry.imonth), []).append(entry)

        route = self.path
        html = tt.render(conf=self.conf, articles=articles,
                         env=union(self.env, num_entries=len(entrylist), route=route))

        yield html, path
