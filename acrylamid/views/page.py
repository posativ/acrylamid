# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# XXX much copy'n'paste from entry.py, make it less repeat yourself

from os.path import isfile

from acrylamid.views import View
from acrylamid.helpers import expand, union, joinurl, event, link, memoize, md5
from acrylamid.errors import AcrylamidException


class Page(View):
    """Creates a static page

    To enable Entry view, add this to your :doc:`conf.py`:

    .. code-block:: python

        '/:year/:slug/': {
            'view': 'page',
            'template': 'main.html'  # default, includes entry.html
        }

    The page view renders an post to a unique location withouth any references
    to other blog entries. The url is user configurable, but may be overwritten by
    setting ``PAGE_PERMALINK`` explicitly to a URL in your configuration.

    This view takes no other arguments and uses *main.html* and *entry.html* as
    template."""

    def init(self, template='main.html'):
        self.template = template

    def generate(self, request):

        tt = self.env.engine.fromfile(self.template)

        pages = request['pages']
        pathes = set()

        for page in pages:
            if page.permalink != expand(self.path, page):
                path = joinurl(self.conf['output_dir'], page.permalink)
            else:
                path = joinurl(self.conf['output_dir'], expand(self.path, page))

            if path.endswith('/'):
                path = joinurl(path, 'index.html')

            if isfile(path) and path in pathes:
                try:
                    os.remove(path)
                finally:
                    other = [e for e in pages if e != page and e.filename == path][0]
                    raise AcrylamidException("title collision %r in %r with %r" %
                        (page.permalink, page.filename, other))

            # detect collisions
            pathes.add(path)

            if isfile(path) and not any([page.has_changed, tt.has_changed]):
                event.skip(path)
                continue

            html = tt.render(conf=self.conf, page=page, entry=page,
                             env=union(self.env, type='page'))

            yield html, path
