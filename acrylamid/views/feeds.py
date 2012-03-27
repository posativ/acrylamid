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
        tt = self.env['tt_env'].get_template('%s.xml' % self.__class__.__name__)

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

        # result = []
        # for entry in entrylist[:self.num_entries]:
        #     _id = 'tag:' + self.conf.get('www_root', '').replace(env['protocol'] + '://', '') \
        #                  + ',' + entry.date.strftime('%Y-%m-%d') + ':' \
        #                  + entry.permalink

        #     result.append(render(self.tt_entry, env, self.conf, entry, id=_id))

        # XXX let user modify the path
        # xml = render(self.tt_body, env, self.conf, {'entrylist': '\n'.join(result),
        #               'updated': },
        #               atom=Atom, rss=RSS)

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
        self.env['tt_env'].filters['rfc822'] = lambda x: format_date_time(mktime(x.timetuple()))
