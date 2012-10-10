# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from future_builtins import filter

import io
import re

from time import strftime, gmtime
from os.path import join, getmtime, exists
from collections import defaultdict

from acrylamid.views import View
from acrylamid.helpers import event, joinurl, rchop


class Map(io.StringIO):
    """A simple Sitemap generator."""

    def __init__(self, *args, **kw):

        io.StringIO.__init__(self)
        self.write(u"<?xml version='1.0' encoding='UTF-8'?>\n")
        self.write(u'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

    def add(self, url, lastmod, changefreq='never', priority=0.5):

        self.write(u'  <url>\n')
        self.write(u'    <loc>%s</loc>\n' % url)
        self.write(u'    <lastmod>%s</lastmod>\n' % strftime('%Y-%m-%d', gmtime(lastmod)))
        if changefreq:
            self.write(u'    <changefreq>%s</changefreq>\n' % changefreq)
        if priority != 0.5:
            self.write(u'    <priority>%.1f</priority>\n' % priority)
        self.write(u'  </url>\n')

    def finish(self):
        self.write(u'</urlset>')


class Sitemap(View):
    """Create an XML-Sitemap where permalinks have the highest priority (1.0) and do never
    change and all other ressources have a changefreq of weekly.

    .. code-block:: python

        '/sitemap.xml': {
            'view': 'Sitemap'
        }
    """

    priority = 0.0
    scores = {'page': (1.0, 'never'), 'entry': (1.0, 'never')}

    def init(self):

        def track(path, *args, **kw):
            self.files.add(path)

        def changed(path, *args, **kw):
            if not self.has_changed:
                self.has_changed = True

        self.files = set([])
        self.has_changed = False

        # track output files
        event.register(track, to=['create', 'update', 'skip', 'identical'])
        event.register(changed, to=['create', 'update', 'identical'])

    def convert(self, link, replacements):
        for pat, repl in replacements:
            link = re.sub(pat, repl, link)

        if link.endswith('/'):
            link += 'index.html'

        return re.compile('^' + joinurl(re.escape(self.conf['www_root']), link) + '$')

    def context(self, env, request):
        """"Here we prepare the detection pattern and active views. For each view we convert
        ``view.path`` to a regular expression pattern using simple replacements."""

        patterns = defaultdict(list)
        replacements = [(':year', '\d+'), (':month', '\d+'), (':day', '\d+'),
                        (':num', '\d+'), (':[^/]+', '[^/]+')]

        for view in self.env.views:
            patterns[view].append(self.convert(view.path, replacements))
            if hasattr(view, 'pagination'):
                patterns[view].append(self.convert(view.pagination, replacements))

        self.patterns = patterns
        self.views = self.env.views[:]

        # sort active views by frequency
        for key in 'entry', 'tag', 'index':
            for view in [v for v in self.views if v == key]:
                self.views.remove(view)
                self.views.insert(0, view)

        return env

    def generate(self, request):
        """In this step, we filter drafted entries (they should not be included into the
        Sitemap) and test each url pattern for success and write the corresponding
        changefreq and priority to the Sitemap."""

        drafted = set([joinurl(self.conf['output_dir'], e.permalink, 'index.html')
                    for e in request['entrylist'] + request['pages'] if e.draft])

        path = joinurl(self.conf['output_dir'], self.path)
        sm = Map()

        if exists(path) and not self.has_changed:
            event.skip(path)
            raise StopIteration

        for fname in self.files:
            if fname in drafted:
                continue

            url = join(self.conf['www_root'], fname.replace(self.conf['output_dir'], ''))
            for view in self.views:

                if any(filter(lambda pat: pat.match(url), self.patterns[view])):
                    priority, changefreq = self.scores.get(view.name, (0.5, 'weekly'))
                    sm.add(rchop(url, 'index.html'), getmtime(fname), changefreq, priority)

                    break

        sm.finish()
        yield sm, path
