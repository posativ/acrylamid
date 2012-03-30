# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py
# -*- encoding: utf-8 -*-

from datetime import datetime
from os.path import exists

from acrylamid.views import View
from acrylamid.utils import joinurl, event, union


class Feed(View):

    def generate(self, request):

        entrylist = filter(lambda e: not e.draft, request['entrylist'])[:self.num_entries]
        tt = self.env.jinja2.get_template('%s.xml' % self.__class__.__name__)

        p = joinurl(self.conf['output_dir'], self.path)
        if not filter(lambda e: p.endswith(e), ['.xml', '.html']):
            p = joinurl(p, 'index.html')


        if exists(p) and not filter(lambda e: e.has_changed, entrylist):
            if not tt.has_changed:
                event.skip(p.replace(self.conf['output_dir'], ''), path=p)
                raise StopIteration

        updated=entrylist[0].date if entrylist else datetime.now()
        html = tt.render(conf=self.conf, env=union(self.env,
                         updated=updated, entrylist=entrylist))

        yield html, p


class Atom(Feed):

    path = '/atom/'

    def init(self, num_entries=25):
        self.num_entries = num_entries


class RSS(Feed):

    path = '/rss/'

    def init(self, num_entries=25):

        from wsgiref.handlers import format_date_time
        from time import mktime

        self.num_entries = num_entries
        self.env.jinja2.filters['rfc822'] = lambda x: format_date_time(mktime(x.timetuple()))
