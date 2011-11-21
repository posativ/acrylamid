# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py
# -*- encoding: utf-8 -*-

from acrylamid.views import View
from acrylamid.utils import render, mkfile, joinurl, safeslug

from collections import defaultdict


filters = []
path = '/tag/'
items_per_page = 10
enabled = True

class Tag(View):
    
    def __init__(self, conf, env):
        
        class Link:
            
            def __init__(self, title, href):
                self.title = title
                self.href = href if href.endswith('/') else href + '/'
        
        env['tt_env'].filters['safeslug'] = safeslug
        env['tt_env'].filters['tagify'] = lambda e: [Link(t, joinurl(path, safeslug(t))) for t in e]
        
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
        
        tt_entry = env['tt_env'].get_template('entry.html')
        tt_main = env['tt_env'].get_template('main.html')

        tags = defaultdict(list)
        for e in entrylist:
            for tag in e.tags:
                tags[safeslug(tag)].append(e)
        
        for tag in tags:
            entrylist = [render(tt_entry, conf, env, entry, type="tag") for entry in tags[tag]]
            for i, mem in enumerate([entrylist[x*ipp:(x+1)*ipp] for x in range(len(entrylist)/ipp+1)]):
                
                if i == 0:
                    next = None
                    curr = joinurl(path, tag)
                else:
                    curr = joinurl(path, tag, i+1)
                    next = joinurl(path, tag) if i==1 else joinurl(path, tag, i)
                prev = None if i==(len(entrylist)/ipp+1)-1 else joinurl(path, tag, i+2)
                
                html = render(tt_main, conf, env, type='tag', prev=prev, curr=curr, next=next,
                            entrylist='\n'.join(mem), num_entries=len(entrylist),
                            items_per_page=items_per_page)
                directory = joinurl(conf['output_dir'], curr, 'index.html')
                mkfile(html, {'title': curr}, directory)
