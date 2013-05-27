# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import io

from time import strftime, gmtime
from os.path import getmtime, exists, splitext

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

    def init(self, conf, env):

        def track(ns, path):
            if ns != 'resource':
                self.files.add((ns, path))                
            elif self.resext and splitext(path) in self.resext:
                self.files.add((ns, path))

        def changed(ns, path):
            if not self.modified:
                self.modified = True

        self.files = set([])
        self.modified = False
        
        # use extension to check if resource should be tracked (eg PDF but should excluding images and video)
        self.resext = conf.get('sitemap_resource_ext', [])
        # Considered adding images and video, but need to be associated with loc. Better to have access to entry obj
        # see http://support.google.com/webmasters/bin/answer.py?hl=en&answer=183668
        #
        #self.imgext = conf.get('sitemap_image_ext', [])
        #self.vidext = conf.get('sitemap_video_ext', [])

        # track output files
        event.register(track, to=['create', 'update', 'skip', 'identical'])
        event.register(changed, to=['create', 'update', 'identical'])

    def generate(self, conf, env, data):
        """In this step, we filter drafted entries (they should not be included into the
        Sitemap) and write the pre-defined priorities to the map."""

        path = joinurl(conf['output_dir'], self.path)
        sm = Map()

        if exists(path) and not self.modified:
            event.skip('sitemap', path)
            raise StopIteration

        for ns, fname in self.files:

            if ns == 'draft':
                continue

            url = conf['www_root'] + '/' + fname.replace(conf['output_dir'], '')
            priority, changefreq = self.scores.get(ns, (0.5, 'weekly'))
            sm.add(rchop(url, 'index.html'), getmtime(fname), changefreq, priority)

        sm.finish()
        yield sm, path
