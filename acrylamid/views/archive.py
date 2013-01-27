# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from os.path import isfile

from acrylamid.utils import neighborhood, groupby
from acrylamid.views import View
from acrylamid.helpers import union, joinurl, event, expand, memoize, hash, link


class Archive(View):
    """A view that lists all posts per year/month/day (usually found in
    WordPress blogs). Configuration syntax:

    .. code-bock:: python

        '/:year/': {'view': 'archvie'},
        '/:year/:month/': {'view': 'archvie'},
        '/:year/:month/:day/': {'view': 'archvie'}

    Use `listings.html <https://gist.github.com/d82ae4641007b310c195>`_ as template.
    """

    def init(self, conf, env, template='listing.html'):
        self.template = template

    def generate(self, conf, env, data):

        tt = env.engine.fromfile(self.template)
        keyfunc = lambda k: (k.year, )

        if '/:month' in self.path:
            keyfunc = lambda k: (k.year, k.imonth)
        if '/:day' in self.path:
            keyfunc = lambda k: (k.year, k.imonth, k.iday)

        for next, curr, prev in neighborhood(groupby(data['entrylist'], keyfunc)):

            salt, group = '-'.join(str(i) for i in curr[0]), list(curr[1])
            modified = memoize('archive-' + salt, hash(*group)) or any(e.modified for e in group)

            if prev:
                prev = link(u'Previous »', expand(self.path, prev[1][0]))
            if next:
                next = link(u'« Next', expand(self.path, next[1][0]))

            route = joinurl(conf['output_dir'], expand(self.path, group[0]))
            path  = joinurl(route, 'index.html')

            if isfile(path) and not (modified or tt.modified or env.modified or conf.modified):
                event.skip(path)
                continue

            html = tt.render(conf=conf, env=union(env, entrylist=group,
                type='archive', prev=prev, curr=link(route), next=next,
                num_entries=len(group), route=path))

            yield html, path
