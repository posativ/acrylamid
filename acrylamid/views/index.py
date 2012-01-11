# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py
# -*- encoding: utf-8 -*-

from os.path import exists

from acrylamid.views import View
from acrylamid.utils import render, mkfile, joinurl, event, paginate, expand


class Index(View):

    __name__ = 'index'
    filters = []
    path = '/'
    items_per_page = 10
    pagination = '/page/:num/'

    def __init__(self, conf, env, **kw):
        for key, value in kw.iteritems():
            if not hasattr(self, key):
                log.warn("no such option `%s'", key)
                continue
            setattr(self, key, value)

    def __call__(self, request):
        """Creates nicely paged listing of your posts.  First page is the
        index.hml used to have this nice url: http://yourblog.com/ with a recent
        list of your (e.g. summarized) Posts. Other pages are enumerated to /page/n+1

        required:
        items_per_page -- posts displayed per page (defaults to 6)
        entry.html -- layout of Post's entry
        main.html -- layout of the website
        """

        conf = request['conf']
        env = request['env']
        entrylist = request['entrylist']
        ipp = self.items_per_page

        tt_entry = env['tt_env'].get_template('entry.html')
        tt_main = env['tt_env'].get_template('main.html')

        pages, has_changed = paginate(entrylist, ipp, lambda e: not e.draft)
        for i, mem in enumerate(pages):
            # curr = current page, next = newer pages, prev = older pages
            if i == 0:
                next = None
                curr = self.path
            else:
                curr = expand(self.pagination, {'num': str(i+1)})
                next = self.path if i == 1 else expand(self.pagination, {'num': str(i)})

            prev = None if i == (len(entrylist)/ipp + 1) - 1 \
                        else expand(self.pagination, {'num': str(i+2)})
            directory = conf['output_dir']

            if i == 0:
                directory = joinurl(conf['output_dir'], self.path)
            else:
                directory = joinurl(conf['output_dir'],
                                expand(self.pagination, {'num': str(i+1)}))

            p = joinurl(directory, 'index.html')
            message = self.path if i==0 else expand(self.pagination, {'num': str(i+1)})

            if exists(p) and not has_changed:
                if not (tt_entry.has_changed or tt_main.has_changed):
                    event.skip(message, path=p)
                    continue

            mem = [render(tt_entry, conf, env, entry, type="page") for entry in mem]

            html = render(tt_main, conf, env, type='page', prev=prev, curr=curr, next=next,
                        entrylist='\n'.join(mem), num_entries=len(entrylist),
                        items_per_page=ipp)

            mkfile(html, p, message)
