# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py
# -*- encoding: utf-8 -*-

from acrylamid.views import View
from acrylamid.utils import render, mkfile, joinurl, safeslug

from collections import defaultdict
from jinja2 import Template


filters = []
path = '/tag/'
items_per_page = 10
enabled = True

class Tag(View):
    
    def __init__(self, conf, env):
        pass
        
    def __call__(self, request):
        """Creates paged listing by tag.
                
        required:
        items_per_page -- posts displayed per page (defaults to 10)
        entry.html -- layout of Post's entry
        main.html -- layout of the website
        """
        conf = request['conf']
        env = request['env']
        entrylist = request['entrylist']
        ipp = items_per_page

        tt_entry = Template(env['tt_entry'])
        tt_main = Template(env['tt_main'])

        tags = defaultdict(list)
        for e in entrylist:
            for tag in e.tags:
                tags[safeslug(tag)].append(e)
        
        for tag in tags:
            entrylist = [render(tt_entry, conf, env, entry, type="tag") for entry in tags[tag]]
            for i, mem in enumerate([entrylist[x*ipp:(x+1)*ipp] for x in range(len(entrylist)/ipp+1)]):
                
                html = render(tt_main, conf, env, type='tag', page=i+1,
                            entrylist='\n'.join(mem), num_entries=len(entrylist),
                            items_per_page=items_per_page)
                directory = joinurl(conf['output_dir'], path, tag)
                p = joinurl(directory, str(i+1) if i>0 else '', 'index.html')
                mkfile(html, {'title': joinurl(path, tag, str(i+1) if i>0 else '')}, p)
