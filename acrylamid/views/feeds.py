# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from os.path import isfile
from datetime import datetime, timedelta

from acrylamid.utils import HashableList, total_seconds
from acrylamid.views import View, tag
from acrylamid.helpers import joinurl, event, expand, union
from acrylamid.readers import Timezone

epoch = datetime.utcfromtimestamp(0).replace(tzinfo=Timezone(0))


def utc(dt, fmt='%Y-%m-%dT%H:%M:%SZ'):
    """return date pre-formated as UTC timestamp.
    """
    return (dt - (dt.utcoffset() or timedelta())).strftime(fmt)


class Feed(View):
    """Atom and RSS feed generation.  The feeds module provides several classes
    to generate feeds:

      - RSS -- RSS feed for all entries
      - Atom  -- same for Atom
      - RSSPerTag -- RSS feed for all entries for a given tag
      - AtomPerTag -- same for Atom

    All feed views have a ``num_entries`` argument that defaults to 25 and
    limits the list of posts to the 25 latest ones. In addition RSSPerTag and
    AtomPerTag expand ``:name`` to the current tag in your route.

    Examples:

    .. code-block:: python

        # per tag Atom feed
        '/tag/:name/feed/': {'filters': ..., 'view': 'atompertag'}

        # full Atom feed
        '/atom/full/': {'filters': ..., 'view': 'atom', 'num_entries': 1000}
    """

    priority = 25.0

    def init(self, conf, env):
        self.filters.append('absolute')
        self.route = self.path

    def context(self, conf, env, data):
        env.engine.register('utc', utc)
        return env

    def generate(self, conf, env, data):
        entrylist = data['entrylist']
        entrylist = list(entrylist)[0:self.num_entries]
        tt = env.engine.fromfile('%s.xml' % self.type)

        path = joinurl(conf['output_dir'], self.route)
        modified = any(entry.modified for entry in entrylist)

        if isfile(path) and not (conf.modified or env.modified or tt.modified or modified):
            event.skip(self.name, path)
            raise StopIteration

        updated = entrylist[0].date if entrylist else datetime.utcnow()
        html = tt.render(conf=conf, env=union(env, route=self.route,
                         updated=updated, entrylist=entrylist))
        yield html, path


class FeedPerTag(tag.Tag, Feed):

    def context(self, conf, env, data):
        self.populate_tags(data)

        return env

    def generate(self, conf, env, data):

        for tag in self.tags:

            entrylist = HashableList(entry for entry in self.tags[tag])
            new_data = data
            new_data['entrylist'] = entrylist
            self.route = expand(self.path, {'name': tag})
            for html, path in Feed.generate(self, conf, env, new_data):
                yield html, path


class Atom(Feed):

    def init(self, conf, env, num_entries=25):
        super(Atom, self).init(conf, env)

        self.num_entries = num_entries
        self.type = 'atom'


class RSS(Feed):

    def init(self, conf, env, num_entries=25):
        super(RSS, self).init(conf, env)

        from wsgiref.handlers import format_date_time
        from time import mktime

        self.num_entries = num_entries
        env.engine.register(
            'rfc822', lambda dt: format_date_time(total_seconds(dt - epoch)))
        self.type = 'rss'


class AtomPerTag(FeedPerTag):

    def init(self, conf, env, num_entries=25):
        super(AtomPerTag, self).init(conf, env)

        self.num_entries = num_entries
        self.type = 'atom'


class RssPerTag(FeedPerTag):

    def init(self, conf, env, num_entries=25):
        super(RssPerTag, self).init(conf, env)

        from wsgiref.handlers import format_date_time
        from time import mktime

        self.num_entries = num_entries
        env.engine.register(
            'rfc822', lambda dt: format_date_time(total_seconds(dt - epoch)))
        self.type = 'rss'
