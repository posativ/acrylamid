# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py
# -*- encoding: utf-8 -*-

from time import time
from os.path import exists

from acrylamid import log
from acrylamid.views import View
from acrylamid.utils import union, mkfile, joinurl, event, paginate, expand, cache


class Index(View):

    def __init__(self, conf, env, items_per_page=10, pagination='/page/:num/', *args, **kwargs):
        View.__init__(self, *args, **kwargs)
        self.items_per_page = items_per_page
        self.pagination = pagination

    def __call__(self, request, *args, **kwargs):
        """Creates nicely paged listing of your posts.  First page is the
        index.hml used to have this nice url: http://yourblog.com/ with a recent
        list of your (e.g. summarized) Posts. Other pages are enumerated to /page/n+1
        """

        conf = request['conf']
        env = request['env']
        entrylist = request['entrylist']
        ipp = self.items_per_page

        tt_entry = env['tt_env'].get_template('entry.html')
        tt_main = env['tt_env'].get_template('main.html')

        pages, has_changed = paginate(entrylist, ipp, lambda e: not e.draft)

        try:
            rv = cache.memoize('index-hash')
            has_changed = False
            if rv != [repr(e) for e in entrylist if not e.draft]:
                raise KeyError
        except KeyError:
            cache.memoize('index-hash', [repr(e) for e in entrylist if not e.draft])
            has_changed = True

        for i, entries in enumerate(pages):
            ctime = time()

            # curr = current page, next = newer pages, prev = older pages
            if i == 0:
                next = None
                curr = self.path
            else:
                curr = expand(self.pagination, {'num': str(i+1)})
                next = self.path if i == 1 else expand(self.pagination, {'num': str(i)})
            prev = None if i >= len(list(pages))-1 \
                        else expand(self.pagination, {'num': str(i+2)})

            directory = conf['output_dir']
            if i == 0:
                directory = joinurl(conf['output_dir'], self.path)
            else:
                directory = joinurl(conf['output_dir'],
                                expand(self.pagination, {'num': str(i+1)}))

            p = joinurl(directory, 'index.html')
            message = self.path if i==0 else expand(self.pagination, {'num': str(i+1)})

            if exists(p) and not has_changed and not entrylist.has_changed:
                if not (tt_entry.has_changed or tt_main.has_changed):
                    event.skip(message, path=p)
                    continue

            html = tt_main.render(conf=conf, env=union(env, entrylist=entries, type='index',
                                    prev=prev, curr=curr, next=next,  items_per_page=ipp,
                                    num_entries=len(entrylist)))

            mkfile(html, p, message, ctime=time()-ctime, **kwargs)
