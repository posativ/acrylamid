# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import io

from time import strftime, gmtime
from os.path import getmtime, exists, splitext, basename
from urlparse import urljoin
from xml.sax.saxutils import escape

from acrylamid.views import View
from acrylamid.helpers import event, joinurl, rchop


class Map(io.StringIO):
    """A simple Sitemap generator."""

    def __init__(self, *args, **kw):

        io.StringIO.__init__(self)
        self.write(u"<?xml version='1.0' encoding='UTF-8'?>\n")
        self.write(u'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n')
        self.write(u'        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n')

    def add(self, url, lastmod, changefreq='never', priority=0.5, images=None):

        self.write(u'  <url>\n')
        self.write(u'    <loc>%s</loc>\n' % escape(url))
        self.write(u'    <lastmod>%s</lastmod>\n' % strftime('%Y-%m-%d', gmtime(lastmod)))
        if changefreq:
            self.write(u'    <changefreq>%s</changefreq>\n' % changefreq)
        if priority != 0.5:
            self.write(u'    <priority>%.1f</priority>\n' % priority)
        for img in images or []:
            self.write(u'    <image:image>\n')
            self.write(u'        <image:loc>%s</image:loc>\n' %  escape(urljoin(url, basename(img))))
            self.write(u'    </image:image>\n')

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
    
    The sitemap by default excludes any resources copied over with the entry.
    If you wish to include image resources associated with the entry, the config property
    ``SITEMAP_IMAGE_EXT`` can be use to define file extensions to include.
    ``SITEMAP_RESOURCE_EXT`` can be used for other file types such as text files and PDFs.
    Video resources are not supported, and should not be included in the above properties. 
    """

    priority = 0.0
    scores = {'page': (1.0, 'never'), 'entry': (1.0, 'never')}

    def init(self, conf, env):

        def track(ns, path):
            if ns != 'resource':
                self.files.add((ns, path))                
            elif self.resext and splitext(path)[1] in self.resext:
                self.files.add((ns, path))

        def changed(ns, path):
            if not self.modified:
                self.modified = True

        self.files = set([])
        self.modified = False
        
        # use extension to check if resource should be tracked (keep image, video and other resources separate)
        self.resext = conf.get('sitemap_resource_ext', [])
        self.imgext = conf.get('sitemap_image_ext', [])
        # video resources require more attributes (image, description)
        # see http://support.google.com/webmasters/bin/answer.py?hl=en&answer=183668
        #self.vidext = conf.get('sitemap_video_ext', [])

        # track output files
        event.register(track, to=['create', 'update', 'skip', 'identical'])
        event.register(changed, to=['create', 'update'])

    def context(self, conf, env, data):
        """If resources are included in sitemap, create a map for each entry and its 
        resources, so they can be include in <url>"""

        if self.imgext:
            self.mapping = dict([(entry.permalink, entry.resources)
                for entry in data['entrylist']])

        return env

    def generate(self, conf, env, data):
        """In this step, we filter drafted entries (they should not be included into the
        Sitemap) and write the pre-defined priorities to the map."""

        path = joinurl(conf['output_dir'], self.path)
        sm = Map()

        if exists(path) and not self.modified and not conf.modified:
            event.skip('sitemap', path)
            raise StopIteration

        for ns, fname in self.files:

            if ns == 'draft':
                continue

            permalink = '/' + fname.replace(conf['output_dir'], '')
            url = conf['www_root'] + permalink
            priority, changefreq = self.scores.get(ns, (0.5, 'weekly'))
            if self.imgext:
                images = [x for x in self.mapping.get(permalink, []) if splitext(x)[1].lower() in self.imgext]
                sm.add(rchop(url, 'index.html'), getmtime(fname), changefreq, priority, images)
            else:
                sm.add(rchop(url, 'index.html'), getmtime(fname), changefreq, priority)
        sm.finish()
        yield sm, path
