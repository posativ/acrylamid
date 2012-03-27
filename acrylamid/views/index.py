# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py
# -*- encoding: utf-8 -*-

from os.path import exists

from acrylamid.views import View
from acrylamid.utils import union, joinurl, event, paginate, expand


class Index(View):

    def init(self, items_per_page=10, pagination='/page/:num/'):
        self.items_per_page = items_per_page
        self.pagination = pagination

    def generate(self, request):
        """Creates nicely paged listing of your posts.  First page is the
        index.hml used to have this nice url: http://yourblog.com/ with a recent
        list of your (e.g. summarized) Posts. Other pages are enumerated to /page/n+1
        """

        entrylist = request['entrylist']
        ipp = self.items_per_page

        tt_entry = self.env['tt_env'].get_template('entry.html')
        tt_main = self.env['tt_env'].get_template('main.html')

        for i, entries, has_changed in paginate(entrylist, ipp, lambda e: not e.draft,
                                                orphans=self.conf['default_orphans']):

            # curr = current page, next = newer pages, prev = older pages
            if i == 0:
                next = None
                curr = self.path
            else:
                curr = expand(self.pagination, {'num': str(i+1)})
                next = self.path if i == 1 else expand(self.pagination, {'num': str(i)})
            prev = None if i >= len(list(entries))-1 \
                        else expand(self.pagination, {'num': str(i+2)})

            directory = self.conf['output_dir']
            if i == 0:
                directory = joinurl(self.conf['output_dir'], self.path)
            else:
                directory = joinurl(self.conf['output_dir'],
                                expand(self.pagination, {'num': str(i+1)}))

            p = joinurl(directory, 'index.html')
            message = self.path if i==0 else expand(self.pagination, {'num': str(i+1)})

            if exists(p) and not has_changed:
                if not (tt_entry.has_changed or tt_main.has_changed):
                    event.skip(message, path=p)
                    continue

            html = tt_main.render(conf=self.conf, env=union(self.env, entrylist=entries,
                                  type='index', prev=prev, curr=curr, next=next,
                                  items_per_page=ipp, num_entries=len(entrylist)))

            yield html, p, message
