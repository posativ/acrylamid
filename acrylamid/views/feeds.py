# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from os.path import isfile
from datetime import datetime, timedelta
from itertools import ifilter

from acrylamid.utils import HashableList
from acrylamid.views import View, tag
from acrylamid.helpers import joinurl, event, expand, union


def utc(dt, fmt='%Y-%m-%dT%H:%M:%SZ'):
    """return date pre-formated as UTC timestamp.
    """
    return (dt - (dt.utcoffset() or timedelta())).strftime(fmt)


class Feed(View):

    priority = 25.0

    def context(self, conf, env, data):
        env.engine.register('utc', utc)
        return env

    def generate(self, conf, env, data):
        entrylist = data['entrylist']
        entrylist = list(entrylist)[0:self.num_entries]
        tt = env.engine.fromfile('%s.xml' % self.type)

        path = joinurl(conf['output_dir'], self.path)
        if not path.endswith(('.xml', '.html')):
            path = joinurl(path, 'index.html')

        modified = any(entry.modified for entry in entrylist)
        if (isfile(path) and not (env.modified or tt.modified or modified)):
            event.skip(path)
            raise StopIteration

        updated = entrylist[0].date if entrylist else datetime.utcnow()
        html = tt.render(conf=conf, env=union(env, route=self.path,
                         updated=updated, entrylist=entrylist))
        yield html, path


class FeedPerTag(tag.Tag, Feed):

    def context(self, conf, env, data):
        self.populate_tags(data)

        return env

    def generate(self, data):

        entrylist = [entry for entry in data['entrylist']
                     if not entry.draft]

        self.original_path = self.path
        for tag in self.tags:

            entrylist = HashableList(entry for entry in self.tags[tag])
            new_data = data
            new_data['entrylist'] = entrylist
            self.path = expand(self.original_path, {'name': tag})
            for html, path in Feed.generate(self, new_data):
                yield html, path


class Atom(Feed):

    def init(self, conf, env, num_entries=25):
        self.num_entries = num_entries
        self.type = 'atom'
        self.filters.append('absolute')


class RSS(Feed):

    def init(self, conf, env, num_entries=25):

        from wsgiref.handlers import format_date_time
        from time import mktime

        self.num_entries = num_entries
        env.engine.register(
            'rfc822', lambda x: unicode(format_date_time(mktime(x.timetuple()))))
        self.type = 'rss'
        self.filters.append('absolute')


class AtomPerTag(FeedPerTag):

    def init(self, conf, env, num_entries=25):
        self.filters.append('absolute')
        self.num_entries = num_entries
        self.type = 'atom'


class RssPerTag(FeedPerTag):

    def init(self, conf, env, num_entries=25):

        from wsgiref.handlers import format_date_time
        from time import mktime

        self.filters.append('absolute')
        self.num_entries = num_entries
        env.engine.register(
            'rfc822', lambda x: format_date_time(mktime(x.timetuple())))
        self.type = 'rss'
