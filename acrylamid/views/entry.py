# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from acrylamid.views import View
from acrylamid.utils import expand, render, mkfile, joinurl

from os.path import join
from jinja2 import Template

filters = []
path = '/:year/:slug/'
enabled = True

class Entry(View):
    """Creates single full-length entry.
    entry.html -- layout of Post's entry
    main.html -- layout of the website
    """
    
    def __init__(self, conf, env):
        pass
        
    def __call__(self, request):

        conf = request['conf']
        env = request['env']
        entrylist = request['entrylist']
        
        tt_entry = Template(env['tt_entry'])
        tt_main = Template(env['tt_main'])

        for entry in entrylist:
            html = render(tt_main, conf, env, type='item',
                                entrylist=render(tt_entry, conf, env,
                                                entry, type='item'))

            p = joinurl(conf['output_dir'],  expand(path, entry), 'index.html')
            mkfile(html, entry, p)
