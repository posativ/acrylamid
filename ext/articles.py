#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import tools, os.path

from copy import deepcopy
from collections import defaultdict
from jinja2 import Template
from shpaml import convert_text

def cb_end(request):
    """Generates a overview of all articles."""
    
    request = deepcopy(request)
    tools.run_callback('prepare', request) # needed for entry's url
    
    config = request._config
    data = request._data
    layout = os.path.join(config.get('layout_dir', 'layouts'), 'articles.html')
    tt_articles = Template(convert_text(open(layout).read()))
    articles = defaultdict(list)
    
    for entry in sorted(data['entry_list'], key=lambda k: k._date, reverse=True):
        url, title, year = entry['url'], entry['title'], entry._date.year
        
        articles[year].append((entry._date, url, title))
        
    articlesdict =config.copy()
    articlesdict.update({'articles': articles,
                 'num_entries': len(data['entry_list'])})
                 
    html = tt_articles.render(articlesdict)
    path = os.path.join(config.get('output_dir', 'out'), 'articles', 'index.html')
    
    tools.mk_file(html, {'title': 'articles/index.html'}, path)