# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from acrylamid.views import View
from acrylamid.utils import mkfile, joinurl, event

from os.path import join, getmtime, exists
from collections import defaultdict


class Articles(View):
    """Generates a overview of all articles."""

    path = '/articles/'

    def __init__(self, conf, env, *args, **kwargs):
        View.__init__(self, *args, **kwargs)

    def __call__(self, request, *args, **kwargs):

        conf = request['conf']
        env = request['env']
        entrylist = request['entrylist']

        articles = defaultdict(list)
        tt_articles = env['tt_env'].get_template('articles.html')

        p = joinurl(conf['output_dir'], self.path)
        if not filter(lambda e: p.endswith(e), ['.xml', '.html']):
            p = joinurl(p, 'index.html')
        last_modified = max([getmtime(e.filename) for e in entrylist])

        if exists(p) and last_modified < getmtime(p):
            if not tt_articles.has_changed:
                event.skip(p.replace(conf['output_dir'], ''), path=p)
                return

        for entry in sorted(entrylist, key=lambda k: k.date, reverse=True):
            if entry.draft:
                continue

            url, title, year = entry.permalink, entry.title, entry.date.year
            articles[year].append((entry.date, url, title))

        articlesdict = conf.copy()
        articlesdict.update({'articles': articles,
                     'num_entries': len(entrylist)})
        articlesdict.update(request['env'])

        html = tt_articles.render(articlesdict)
        mkfile(html, p, p.replace(conf['output_dir'], ''), **kwargs)
