# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from os.path import exists

from acrylamid.views import View
from acrylamid.utils import expand, render, mkfile, joinurl, event
from acrylamid.errors import AcrylamidException

class Entry(View):
    """Creates single full-length entry.
    entry.html -- layout of Post's entry
    main.html -- layout of the website
    """

    __name__ = 'entry'

    def __init__(self, conf, env, filters=[], path='/:year/:slug/'):

        self.filters = filters
        self.path = path

    def __call__(self, request, *args, **kwargs):

        conf = request['conf']
        env = request['env']
        entrylist = request['entrylist']

        tt_entry = env['tt_env'].get_template('entry.html')
        tt_main = env['tt_env'].get_template('main.html')
        pathes = dict()

        for entry in entrylist:
            if entry.permalink != expand(self.path, entry):
                p = joinurl(conf['output_dir'], entry.permalink)
            else:
                p = joinurl(conf['output_dir'], expand(self.path, entry))

            if not filter(lambda e: p.endswith(e), ['.xml', '.html']):
                p = joinurl(p, 'index.html')

            if p in pathes:
                raise AcrylamidException("title collision %r" % entry.filename)
            pathes[p] = entry

        for p, entry in pathes.iteritems():

            if exists(p) and not entry.has_changed:
                if not (tt_entry.has_changed or tt_main.has_changed):
                    event.skip(entry.title, path=p)
                    continue

            html = render(tt_main, conf, env, type='item',
                          entrylist=render(tt_entry, conf, env, entry, type='item'),
                          title=entry.title, description=entry.description, tags=entry.tags)

            mkfile(html, p, entry.title, **kwargs)
