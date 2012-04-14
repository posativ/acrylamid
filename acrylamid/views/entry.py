# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from os.path import exists

from acrylamid.views import View
from acrylamid.utils import expand, union, joinurl, event
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

        for path, entry in pathes.iteritems():
            if exists(path) and not entry.has_changed and not tt.has_changed:
                event.skip(path)
                continue

            html = tt.render(env=union(self.env, entrylist=[entry], type='entry'),
                             conf=self.conf, entry=entry)

            yield html, path
