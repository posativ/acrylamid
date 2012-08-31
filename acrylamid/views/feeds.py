# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from os.path import exists
from datetime import datetime

from acrylamid.views import View, tag
from acrylamid.helpers import joinurl, event, expand, union


class Feed(View):

    priority = 25.0

    def generate(self, request):
        entrylist = filter(lambda e: not e.draft, request['entrylist'])
        entrylist = list(entrylist)[0:self.num_entries]
        tt = self.env.engine.fromfile('%s.xml' % self.type)

        path = joinurl(self.conf['output_dir'], self.path)
        if not path.endswith(('.xml', '.html')):
            path = joinurl(path, 'index.html')

        if exists(path) and not filter(lambda e: e.has_changed, entrylist):
            if not tt.has_changed:
                event.skip(path)
                raise StopIteration

        updated = entrylist[0].date if entrylist else datetime.now()
        html = tt.render(conf=self.conf, env=union(self.env, route=self.path,
                         updated=updated, entrylist=entrylist))

        yield html, path


class FeedPerTag(tag.Tag, Feed):

    def context(self, env, request):
        self._populate_tags(request)

        return env

    def generate(self, request):

        entrylist = [entry for entry in request['entrylist']
                     if not entry.draft]

        self.original_path = self.path
        for tag in self.tags:

            entrylist = [entry for entry in self.tags[tag]]
            new_request = request
            new_request['entrylist'] = entrylist
            self.path = expand(self.original_path, {'name': tag})
            for html, path in Feed.generate(self, new_request):
                yield html, path


class Atom(Feed):

    def init(self, num_entries=25):
        self.num_entries = num_entries
        self.type = 'atom'


class RSS(Feed):

    def init(self, num_entries=25):

        from wsgiref.handlers import format_date_time
        from time import mktime

        self.num_entries = num_entries
        self.env.engine.register(
            'rfc822', lambda x: format_date_time(mktime(x.timetuple())))
        self.type = 'rss'


class AtomPerTag(FeedPerTag):

    def init(self, num_entries=25):
        self.num_entries = num_entries
        self.type = 'atom'


class RssPerTag(FeedPerTag):

    def init(self, num_entries=25):

        from wsgiref.handlers import format_date_time
        from time import mktime

        self.num_entries = num_entries
        self.env.engine.register(
            'rfc822', lambda x: format_date_time(mktime(x.timetuple())))
        self.type = 'rss'
