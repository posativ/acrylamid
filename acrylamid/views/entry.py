# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from os.path import exists

from acrylamid.views import View
from acrylamid.utils import expand, union, joinurl, event
from acrylamid.errors import AcrylamidException

class Entry(View):
    """Creates single full-length entry."""

    path = '/:year/:slug/'
    filters = []

    def generate(self, request):

        entrylist = request['entrylist']

        tt_entry = self.env['tt_env'].get_template('entry.html')
        tt_main = self.env['tt_env'].get_template('main.html')
        pathes = dict()

        for entry in entrylist:
            if entry.permalink != expand(self.path, entry):
                p = joinurl(self.conf['output_dir'], entry.permalink)
            else:
                p = joinurl(self.conf['output_dir'], expand(self.path, entry))

            if not filter(lambda e: p.endswith(e), ['.xml', '.html']):
                p = joinurl(p, 'index.html')

            if p in pathes:
                raise AcrylamidException("title collision %r in %r" % (entry.permalink,
                                                                       entry.filename))
            pathes[p] = entry

        for p, entry in pathes.iteritems():
            if exists(p) and not entry.has_changed:
                if not (tt_entry.has_changed or tt_main.has_changed):
                    event.skip(entry.title, path=p)
                    continue

            html = tt_main.render(env=union(self.env, entrylist=[entry], type='entry'),
                                  conf=self.conf, entry=entry)

            yield html, p, entry.title
