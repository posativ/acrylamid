# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import io

from time import strftime, gmtime
from os.path import join, getmtime

from acrylamid.views import View
from acrylamid.helpers import event, joinurl


class Map(object):

    def __init__(self, *args, **kw):
        self.sm = [u"<?xml version='1.0' encoding='UTF-8'?>",
                   u'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    def add(self, url, lastmod, priority=0.5, changefreq='never'):
        self.sm.extend([
            u'  <url>',
            u'    <loc>%s</loc>' % url,
            u'    <lastmod>%s</lastmod>' % strftime('%Y-%m-%d', gmtime(lastmod)),
            u'    <changefreq>%s</changefreq>' % changefreq,
            u'    <priority>%.1f</priority>' % priority,
            u'  </url>'
        ])

    def __iter__(self):
        for item in self.sm:
            yield item
        yield u'</urlset>'


class Sitemap(View):

    files = set([])

    def init(self):

        def callback(path, *args, **kw):
            self.files.add(path)

        event.register(callback, to=['create', 'update', 'skip', 'identical'])

    def generate(self, request):

        sm = Map()

        for path in self.files:

            url = join(self.conf['www_root'], path.replace(self.conf['output_dir'], ''))
            url = url.rstrip('index.html')

            sm.add(url, getmtime(path))

        yield '\n'.join(sm), joinurl(self.conf['output_dir'], self.path)
