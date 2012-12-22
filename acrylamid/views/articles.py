# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from acrylamid.views import View
from acrylamid.helpers import union, joinurl, event

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

    def init(self, conf, env, template='articles.html'):
        self.template = template

    def generate(self, conf, env, data):

        entrylist = data['entrylist']

        tt = env.engine.fromfile(self.template)
        path = joinurl(conf['output_dir'], self.path, 'index.html')

        if exists(path) and not (conf.modified or env.modified or tt.modified):
            event.skip(path)
            raise StopIteration

        articles = {}
        for entry in entrylist:
            articles.setdefault((entry.year, entry.imonth), []).append(entry)

        html = tt.render(conf=conf, articles=articles, env=union(env,
                         num_entries=len(entrylist), route=self.path))
        yield html, path
