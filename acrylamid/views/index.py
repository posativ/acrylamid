# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from os.path import isfile

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
            'pagination': '/page/:num/',
            'items_per_page': 10
        }
    """

    def init(self, conf, env, template='main.html', items_per_page=10, pagination='/page/:num/'):
        self.template = template
        self.items_per_page = items_per_page
        self.pagination = pagination
        self.filters.append('relative')

    def generate(self, conf, env, data):

        ipp = self.items_per_page
        tt = env.engine.fromfile(self.template)

        entrylist = data['entrylist']
        paginator = paginate(entrylist, ipp, self.path, conf.default_orphans)
        route = self.path

        for (next, curr, prev), entries, modified in paginator:
            # curr = current page, next = newer pages, prev = older pages

            next = None if next is None \
                else link(u'Next', self.path.rstrip('/')) if next == 1 \
                    else link(u'Next', expand(self.pagination, {'num': next}))

            curr = link(curr, self.path) if curr == 1 \
                else link(expand(self.pagination, {'num': curr}))

            prev = None if prev is None \
               else link(u'Previous', expand(self.pagination, {'num': prev}))

            path = joinurl(conf['output_dir'], curr.href)

            if isfile(path) and not (modified or tt.modified or env.modified or conf.modified):
                event.skip('index', path)
                continue

            html = tt.render(conf=conf, env=union(env, entrylist=entries,
                                  type='index', prev=prev, curr=curr, next=next,
                                  items_per_page=ipp, num_entries=len(entrylist), route=route))
            yield html, path
