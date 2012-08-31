# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from os.path import exists

from acrylamid.views import View
from acrylamid.helpers import union, joinurl, event, paginate, expand, link


class Index(View):
    """Creates nicely paged listing of your posts. First page renders to ``route``
    (defaults to */*) with a recent list of your (e.g. summarized) articles. Other
    pages enumerate to the variable ``pagination`` (*/page/:num/* per default).


    .. code-block:: python

        '/' : {
            'view': 'index',
            'template': 'main.html',
            'pagination': '/page/:num',
            'items_per_page': 10
        }
    """

    def init(self, template='main.html', items_per_page=10, pagination='/page/:num/'):
        self.template = template
        self.items_per_page = items_per_page
        self.pagination = pagination

    def generate(self, request):

        ipp = self.items_per_page
        tt = self.env.engine.fromfile(self.template)

        entrylist = [entry for entry in request['entrylist'] if not entry.draft]
        paginator = paginate(entrylist, ipp, orphans=self.conf['default_orphans'])
        route = self.path

        for (next, curr, prev), entries, has_changed in paginator:
            # curr = current page, next = newer pages, prev = older pages

            next = None if next is None \
                else link(u'« Next', self.path.rstrip('/')) if next == 1 \
                    else link(u'« Next', expand(self.pagination, {'num': next}))

            curr = link(curr, self.path) if curr == 1 \
                else link(expand(self.pagination, {'num': curr}))

            prev = None if prev is None \
               else link(u'Previous »', expand(self.pagination, {'num': prev}))

            path = joinurl(self.conf['output_dir'], curr.href, 'index.html')

            if exists(path) and not has_changed and not tt.has_changed:
                event.skip(path)
                continue

            html = tt.render(conf=self.conf, env=union(self.env, entrylist=entries,
                                  type='index', prev=prev, curr=curr, next=next,
                                  items_per_page=ipp, num_entries=len(entrylist), route=route))

            yield html, path
