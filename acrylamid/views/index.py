# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py
# -*- encoding: utf-8 -*-

from acrylamid.views import View
from acrylamid.utils import render, mkfile, joinurl

filters = []
path = '/page/'
items_per_page = 10
paginating = True
enabled = True

class Index(View):
    
    def __init__(self, conf, env):
        pass
        
    def __call__(self, request):
        """Creates nicely paged listing of your posts.  First page is the
        index.hml used to have this nice url: http://yourblog.com/ with a recent
        list of your (e.g. summarized) Posts. Other pages are enumerated to /page/n+1

        required:
        items_per_page -- posts displayed per page (defaults to 6)
        entry.html -- layout of Post's entry
        main.html -- layout of the website
        """
        conf = request['conf']
        env = request['env']
        entrylist = request['entrylist']
        ipp = items_per_page

        tt_entry = env['tt_env'].get_template('entry.html')
        tt_main = env['tt_env'].get_template('main.html')
        
        entrylist = [render(tt_entry, conf, env, entry, type="page") for entry in entrylist]

        for i, mem in enumerate([entrylist[x*ipp:(x+1)*ipp] for x in range(len(entrylist)/ipp+1)]):

            if i == 0:
                next = None
                curr = path
            else:
                curr = joinurl(path, i+1)
                next = path if i==1 else joinurl(path, i)
            prev = None if i==(len(entrylist)/ipp+1)-1 else joinurl(path, i+2)

            html = render(tt_main, conf, env, type='page', prev=prev, curr=curr, next=next,
                        entrylist='\n'.join(mem), num_entries=len(entrylist),
                        items_per_page=items_per_page)
            directory = conf['output_dir']
            if i > 0:
                directory = joinurl(conf['output_dir'], (path + str(i+1)))
                
            p = joinurl(directory, 'index.html')
            mkfile(html, {'title': '/' if i==0 else (path+str(i+1))}, p)
