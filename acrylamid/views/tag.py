# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py
#
# -*- encoding: utf-8 -*-

from os.path import exists
from collections import defaultdict

from acrylamid import log
from acrylamid.views import View
from acrylamid.utils import render, mkfile, joinurl, safeslug, event, \
                            paginate, EntryList, expand


class Tag(View):

    def __init__(self, conf, env, items_per_page=25,
                 pagination='/tag/:name/:num/', *args, **kwargs):
        View.__init__(self, *args, **kwargs)
        self.items_per_page = items_per_page
        self.pagination = pagination

        class Link:

            def __init__(self, title, href):
                self.title = title
                self.href = href if href.endswith('/') else href + '/'

        def tagify(tags):
            href = lambda t: expand(self.path, {'name': safeslug(t)})
            return [Link(t, href(t)) for t in tags]

        env['tt_env'].filters['safeslug'] = safeslug
        env['tt_env'].filters['tagify'] = tagify

    def __call__(self, request, *args, **kwargs):
        """Creates paged listing by tag.

        required:
        items_per_page -- posts displayed per page (defaults to 10)
        entry.html -- layout of Post's entry
        main.html -- layout of the website
        """
        conf = request['conf']
        env = request['env']
        entrylist = request['entrylist']
        ipp = self.items_per_page

        tt_entry = env['tt_env'].get_template('entry.html')
        tt_main = env['tt_env'].get_template('main.html')

        tags = defaultdict(list)
        for e in entrylist:
            for tag in e.tags:
                tags[safeslug(tag)].append(e)

        for tag in tags:
            entrylist = EntryList([entry for entry in tags[tag]])
            pages, has_changed = paginate(entrylist, ipp, lambda e: not e.draft)
            for i, mem in enumerate(pages):
                # e.g.: curr = /page/3, next = /page/2, prev = /page/4
                if i == 0:
                    next = None
                    curr = expand(self.path, {'name': tag})
                else:
                    curr = expand(self.pagination, {'num': str(i+1), 'name': tag})
                    next = expand(self.path, {'name': tag}) if i==1 \
                             else expand(self.pagination, {'name': tag, 'num': str(i)})

                prev = None if i == (len(entrylist)/ipp + 1) - 1 \
                            else expand(self.pagination, {'name': tag, 'num': str(i+2)})
                p = joinurl(conf['output_dir'], curr, 'index.html')

                if exists(p) and not has_changed:
                    if not (tt_entry.has_changed or tt_main.has_changed):
                        event.skip(curr, path=p)
                        continue

                mem = [render(tt_entry, conf, env, entry, type="tag") for entry in mem]
                html = render(tt_main, conf, env, type='tag', prev=prev, curr=curr, next=next,
                            entrylist='\n'.join(mem), num_entries=len(entrylist),
                            items_per_page=ipp)

                mkfile(html, p, curr, **kwargs)
