# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from os.path import exists

from acrylamid.views import View
from acrylamid.helpers import expand, union, joinurl, event, link, memoize, md5
from acrylamid.errors import AcrylamidException


class Entry(View):
    """Creates single full-length entry."""

    def generate(self, request):

        tt = self.env.jinja2.get_template('main.html')

        entrylist = request['entrylist']
        pathes = dict()

        for entry in entrylist:
            if entry.permalink != expand(self.path, entry):
                p = joinurl(self.conf['output_dir'], entry.permalink)
            else:
                p = joinurl(self.conf['output_dir'], expand(self.path, entry))

            if p.endswith('/'):
                p = joinurl(p, 'index.html')

            if p in pathes:
                raise AcrylamidException("title collision %r in %r" % (entry.permalink,
                                                                       entry.filename))
            pathes[p] = entry

        has_changed = False
        hv = md5(*entrylist, attr=lambda e: e.permalink)

        if memoize('entry-permalinks') != hv:
            memoize('entry-permalinks', hv)
            has_changed = True

        pathes = sorted(pathes.iteritems(), key=lambda k: k[1].date, reverse=True)
        for i, (path, entry) in enumerate(pathes):

            next = None if i == 0 else link(entrylist[i-1].title,
                                            entrylist[i-1].permalink.rstrip('/'),
                                            entrylist[i-1])
            prev = None if i == len(pathes) - 1 else link(entrylist[i+1].title,
                                                          entrylist[i+1].permalink.rstrip('/'),
                                                          entrylist[i+1])

            if exists(path) and not any([has_changed, entry.has_changed, tt.has_changed]):
                event.skip(path)
                continue

            html = tt.render(conf=self.conf, entry=entry, env=union(self.env,
                             entrylist=[entry], type='entry', prev=prev, next=next))

            yield html, path
