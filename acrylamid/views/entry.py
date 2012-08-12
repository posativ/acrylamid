# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os
from os.path import isfile

from acrylamid.views import View
from acrylamid.helpers import expand, union, joinurl, event, link, memoize, md5
from acrylamid.errors import AcrylamidException


class Entry(View):
    """Creates single full-length entry
    (`Example <http://blog.posativ.org/2012/nginx/>`_).

    To enable Entry view, add this to your :doc:`conf.py`:

    .. code-block:: python

        '/:year/:slug/': {
            'view': 'entry',
            'template': 'main.html'  # default, includes entry.html
        }

    The entry view renders an post to a unique location and should be used as
    permalink URL. The url is user configurable, but may be overwritten by
    setting ``ENTRY_PERMALINK`` explicitly to a URL in your configuration.

    This view takes no other arguments and uses *main.html* and *entry.html* as
    template."""

    def init(self, template='main.html'):
        self.template = template

    def generate(self, request):

        tt = self.env.engine.fromfile(self.template)

        entrylist = request['entrylist']
        pathes = set()

        has_changed = False
        hv = md5(*entrylist, attr=lambda e: e.permalink)  # detect changes in prev and next

        if memoize('entry-permalinks') != hv:
            memoize('entry-permalinks', hv)
            has_changed = True

        for i, entry in enumerate(entrylist):
            if entry.hasproperty('permalink'):
                path = joinurl(self.conf['output_dir'], entry.permalink)
            else:
                path = joinurl(self.conf['output_dir'], expand(self.path, entry))

            if path.endswith('/'):
                path = joinurl(path, 'index.html')

            if isfile(path) and path in pathes:
                try:
                    os.remove(path)
                finally:
                    f = lambda e: e is not entry and e.permalink == entry.permalink
                    raise AcrylamidException("title collision %r in %r with %r." %
                        (entry.permalink, entry.filename, filter(f, entrylist)[0].filename))

            ext = None if i == 0 else link(entrylist[i-1].title,
                                            entrylist[i-1].permalink.rstrip('/'),
                                            entrylist[i-1])
            prev = None if i == len(entrylist) - 1 else link(entrylist[i+1].title,
                                                          entrylist[i+1].permalink.rstrip('/'),
                                                          entrylist[i+1])
            # detect collisions
            pathes.add(path)

            if isfile(path) and not any([has_changed, entry.has_changed, tt.has_changed]):
                event.skip(path)
                continue

            html = tt.render(conf=self.conf, entry=entry, env=union(self.env,
                             entrylist=[entry], type='entry', prev=prev, next=ext))

            yield html, path
