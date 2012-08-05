# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import io
import re

from time import strftime, gmtime
from os.path import join, getmtime, exists

from acrylamid.views import View
from acrylamid.helpers import event, joinurl


class Map(object):
    """A simple Sitemap generator."""

    def __init__(self, *args, **kw):

        self.sm = io.StringIO()
        self.sm.write(u"<?xml version='1.0' encoding='UTF-8'?>\n")
        self.sm.write(u'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

    def add(self, url, lastmod, changefreq='never', priority=None):

        self.sm.write(u'  <url>\n')
        self.sm.write(u'    <loc>%s</loc>\n' % url)
        self.sm.write(u'    <lastmod>%s</lastmod>\n' % strftime('%Y-%m-%d', gmtime(lastmod)))
        if changefreq:
            self.sm.write(u'    <changefreq>%s</changefreq>\n' % changefreq)
        if priority:
            self.sm.write(u'    <priority>%.1f</priority>\n' % priority)
        self.sm.write(u'  </url>\n')

    def read(self):
        self.sm.seek(0)
        return self.sm.read() + u'</urlset>'


class Sitemap(View):
    """Create an XML-Sitemap where permalinks have the highest priority (1.0) and do never
    change and all other ressources have a changefreq of weekly.

    .. code-block:: python

        '/sitemap.xml': {
            'view': 'Sitemap'
        }
    """

    priority = 0.0

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

    def context(self, env, request):

        patterns = dict()
        replacements = [(':year', '\d+'), (':month', '\d+'), (':day', '\d+'), (':[^/]+', '\S+')]

        for fmt in ('entry_permalink', 'page_permalink'):
            permalink = self.conf[fmt]
            for pat, repl in replacements:
                permalink = re.sub(pat, repl, permalink)

                # we rank full entries higher
                patterns[fmt] = re.compile(joinurl(re.escape(self.conf['www_root']), permalink))

        self.isfullentry = lambda url: patterns['entry_permalink'].match(url) or \
                                       patterns['page_permalink'].match(url)

    def generate(self, request):

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

            if self.isfullentry(url):
                sm.add(url.rstrip('index.html'), getmtime(fname), priority=1.0)
            else:
                sm.add(url.rstrip('index.html'), getmtime(fname), changefreq='weekly')

        yield sm.read(), path
