#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os, collections

from os.path import basename, splitext
from jinja2 import Template

import lilith, tools

def cb_item(request):
    """Creates single full-length entry.  Looks like
    http://yourblog.org/year/$lang/title/(index.html).
    
    required:
    entry.html -- layout of Post's entry
    main.html -- layout of the website
    """
    config = request._config
    data = request._data
    data['type'] = 'item'
    
    layout = config.get('layout_dir', 'layouts')
    tt_entry = Template(open(os.path.join(layout, 'entry.html')).read())
    tt_main = Template(open(os.path.join(layout, 'main.html')).read())

    # last preparations
    request = tools.run_callback(
            'prepare',
            request)
    
    dict = request._config
    entry_list = []
    mem = collections.defaultdict(list)
        
    for entry in data['entry_list']:
        
        name = splitext(basename(entry._filename))[0][:-2]
        if name[-1] == '.':
            # .de|en|fr detected (must be two characters)
            mem[name].append([x for x in data['entry_list']
                        if splitext(basename(x._filename))[0][:-2] == name])
    
    return request
                        
        # entrydict = dict.copy()
        # entrydict.update({'Post': entry})
        # dict.update({'entry_list':tt_entry.render(entrydict) })
        # html = tt_main.render( dict )
        # 
        # directory = os.path.join(config.get('output_dir', 'out'), 
        #                  str(entry.date.year),
        #                  entry.safe_title)
        # path = os.path.join(directory, 'index.html')
        # tools.mk_file(html, entry, path)