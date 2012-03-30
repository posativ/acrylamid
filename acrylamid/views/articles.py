# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from acrylamid.views import View
from acrylamid.utils import union, joinurl, event, cache, md5

from os.path import exists
from collections import defaultdict


class Articles(View):
    """Generates a overview of all articles."""

    path = '/articles/'

    def generate(self, request):

        entrylist = sorted((e for e in request['entrylist'] if not e.draft),
                        key=lambda k: k.date, reverse=True)

        articles = defaultdict(list)
        tt = self.env.jinja2.get_template('articles.html')

        p = joinurl(self.conf['output_dir'], self.path)
        if not filter(lambda e: p.endswith(e), ['.xml', '.html']):
            p = joinurl(p, 'index.html')

        hv = md5(*entrylist, attr=lambda o: o.md5)
        rv = cache.memoize('articles-hash')

        if rv == hv:
            has_changed = False
        else:
            # save new value for next run
            cache.memoize('articles-hash', hv)
            has_changed = True

        if exists(p) and not has_changed and not tt.has_changed:
                event.skip(p.replace(self.conf['output_dir'], ''), path=p)
                raise StopIteration

        for entry in entrylist:
            url, title, year = entry.permalink, entry.title, entry.date.year
            articles[year].append((entry.date, url, title))

        html = tt.render(conf=self.conf, articles=articles,
                                  env=union(self.env, num_entries=len(entrylist)))

        yield html, p
