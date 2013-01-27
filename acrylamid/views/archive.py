# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from itertools import groupby

from acrylamid.views import View
from acrylamid.helpers import union, joinurl, event, paginate, expand, link


class Archive(View):
    """A view that lists all posts per year/month/day (usually found in WordPress blogs).
    Configuration syntax:

    .. code-bock:: python

        '/:year/': {'view': 'archvie'},
        '/:year/:month/': {'view': 'archvie'},
        '/:year/:month/:day/': {'view': 'archvie'}
    """

    def init(self, conf, env, template='listing.html'):
        self.template = template

    def generate(self, conf, env, data):

        tt = env.engine.fromfile(self.template)
        keyfunc = lambda k: k.year

        if '/:month' in self.path:
            keyfunc = lambda k: (k.year, k.imonth)
        if '/:day' in self.path:
            keyfunc = lambda k: (k.year, k.imonth, k.iday)

        for group in (list(g) for k, g in groupby(data['entrylist'], keyfunc)):

            route = joinurl(conf['output_dir'], expand(self.path, group[0]))
            path  = joinurl(route, 'index.html')

            html = tt.render(conf=conf, env=union(env, entrylist=group,
                type='archive', prev=None, curr=None, next=None,
                num_entries=len(group), route=path))

            yield html, path
