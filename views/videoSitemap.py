# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import io
import re

from acrylamid.helpers import event, joinurl, rchop
from os.path import getmtime, exists, splitext
from xml.sax.saxutils import escape
from acrylamid.views import View
import time


class Map(io.StringIO):
    """A simple Sitemap generator."""
    def __init__(self, *args, **kw):
        io.StringIO.__init__(self)
        self.write(u"<?xml version='1.0' encoding='UTF-8'?>\n")
        self.write(u'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                   u'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n')

    def add(self, url, yt, title, desc, lastmod, changefreq='never', priority=0.5):
        self.write(u'<url>\n')
        self.write(u'<loc>%s</loc>\n' % escape(url))
        self.write(u'<video:video>\n')
        self.write(u'<video:player_loc allow_embed="yes" autoplay="autoplay=1">'
                   u'http://www.youtube.com/v/%s</video:player_loc>\n' % yt)
        self.write(u'<video:thumbnail_loc>http://i.ytimg.com/vi/%s/hqdefault.jpg</video:thumbnail_loc>\n' % yt)
        self.write(u'<video:title>%s</video:title>\n' % title)
        self.write(u'<video:description>%s</video:description>\n' % desc)
        self.write(u'<video:publication_date>%s</video:publication_date>\n' % time.strftime('%Y-%M-%d%TH:%M:%S', time.localtime(lastmod)))
        self.write(u'<video:family_friendly>yes</video:family_friendly> \n')
        self.write(u'<video:uploader info="https://www.youtube.com/user/owenhogarth">Blubee</video:uploader>')
        self.write(u'</video:video>\n')
        self.write(u'</url>\n')

    def finish(self):
        self.write(u'</urlset>')


class VideoSitemap(View):
    priority = 0.0
    scores = {'page': (1.0, 'never'), 'entry': (1.0, 'never')}

    def __init__(self, **kwargs):
        super(VideoSitemap, self).__init__(**kwargs)
        self.modified = False
        self.files = set([])

    def init(self, conf, env):
        self.env = env

        def track(ns, path):
            if ns != 'resource':
                self.files.add((ns, path))
            elif self.resext and splitext(path)[1] in self.resext:
                self.files.add((ns, path))

        def changed(ns, path):
            if not self.modified:
                self.modified = True

        self.resext = conf.get('sitemap_resource_ext', [])
        self.imgext = conf.get('sitemap_image_ext', [])

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

        pages = []
        for i in env.globals.pages:
            pages.append(i.slug)
        for i in env.globals.entrylist:
            pages.append(i.slug)

        if exists(path) and not self.modified and not conf.modified:
            event.skip('sitemap', path)
            raise StopIteration
        for ns, fname in self.files:

            if ns == 'page' or ns == 'entry' or ns == 'index':
                pass
            else:
                continue

            permalink = '/' + fname.replace(conf['output_dir'], '')
            permalink = rchop(permalink, 'index.html')
            url = conf['www_root'] + permalink

            priority, changefreq = self.scores.get(ns, (0.5, 'weekly'))

            _pages = env.globals.entrylist + env.globals.pages

            for i in _pages:
                if permalink.strip('/') in pages:
                    if i.slug.strip('/') == permalink.strip('/'):
                        pages.remove(permalink.strip('/'))
                        video = re.search('youtube.com/(v/|watch\?v=|embed/)([a-zA-Z0-9\-_]*)', i.content)
                        if video:
                            yt = video.group().split('/')[-1]
                            sm.add(url, yt, i.title, i.metadesc, getmtime(fname), changefreq, priority)

        sm.finish()
        yield sm, path