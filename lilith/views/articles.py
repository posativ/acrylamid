# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see lilith.py

from lilith.views import View
from lilith.utils import mkfile, joinurl

from os.path import normpath, join
from collections import defaultdict
from jinja2 import Template

filters = []
path = '/articles/'
enabled = True

class Articles(View):
    """Generates a overview of all articles."""
    
    def __init__(self, conf, env):
        layout = join(conf['layout_dir'], 'articles.html')
        with file(layout) as f:
            self.tt_articles = Template(f.read())
        
    def __call__(self, request):
        
        articles = defaultdict(list)
        conf = request['conf']
        entrylist = request['entrylist']
        
        for entry in sorted(entrylist, key=lambda k: k.date, reverse=True):
            url, title, year = entry.permalink, entry.title, entry.date.year
        
            articles[year].append((entry.date, url, title))
        
        articlesdict = conf.copy()
        articlesdict.update({'articles': articles,
                     'num_entries': len(entrylist)})
                 
        html = self.tt_articles.render(articlesdict)
        p = joinurl(conf['output_dir'], path, 'index.html')
    
        mkfile(html, {'title': joinurl(path, 'index.html')}, p)
