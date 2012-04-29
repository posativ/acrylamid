# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid.views import View
from acrylamid.utils import union, joinurl, event, cache, md5

from os.path import exists


class Articles(View):
    """Generates a overview of all articles."""

    def generate(self, request):

        entrylist = sorted((e for e in request['entrylist'] if not e.draft),
                        key=lambda k: k.date, reverse=True)

        tt = self.env.jinja2.get_template('articles.html')
        path = joinurl(self.conf['output_dir'], self.path, 'index.html')

        hv = md5(*entrylist, attr=lambda o: o.md5)
        rv = cache.memoize('articles-hash')

        if rv == hv:
            has_changed = False
        else:
            # save new value for next run
            cache.memoize('articles-hash', hv)
            has_changed = True

        if exists(path) and not has_changed and not tt.has_changed:
                event.skip(path)
                raise StopIteration

        articles = {}
        for entry in entrylist:
            articles.setdefault((entry.year, entry.month), []).append(entry)

        html = tt.render(conf=self.conf, articles=articles,
                         env=union(self.env, num_entries=len(entrylist)))

        yield html, path
