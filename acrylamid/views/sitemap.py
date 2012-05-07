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
    change and all other ressources have a changefreq of weekly."""

    priority = 0.0

    def init(self):

        def track(path, *args, **kw):
            self.files.add(path)

        def changed(path, *args, **kw):
            if not self.has_changed:
                self.has_changed = True

        self.files = set([])
        self.has_changed = False

        permalink = self.conf['permalink_format']
        for pat, repl in [(':year', '\d+'), (':month', '\d+'), (':day', '\d+'), (':[^/]+', '\S+')]:
            permalink = re.sub(pat, repl, permalink)

        # we rank full entries higher
        self.regex = re.compile(joinurl(self.conf['www_root'], permalink))

        # track output files
        event.register(track, to=['create', 'update', 'skip', 'identical'])
        event.register(changed, to=['create', 'update', 'identical'])

    def generate(self, request):

        path = joinurl(self.conf['output_dir'], self.path)
        sm = Map()

        if exists(path) and not self.has_changed:
            event.skip(path)
            raise StopIteration

        for fname in self.files:
            url = join(self.conf['www_root'], fname.replace(self.conf['output_dir'], ''))

            if self.regex.match(url):
                sm.add(url.rstrip('index.html'), getmtime(fname), priority=1.0)
            else:
                sm.add(url.rstrip('index.html'), getmtime(fname), changefreq='weekly')

        yield sm.read(), path
