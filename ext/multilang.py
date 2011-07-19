#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os, collections, re
from os.path import basename, splitext
from jinja2 import Template
import logging

import lilith, tools
from tools import defaultfunc

log = logging.getLogger('lilith.extensions.multilang')

@defaultfunc
def cb_setlang(request):
    """copied from _prepare in lilith.py"""
    
    config = request._config
    data = request._data
    for i, entry in enumerate(data['entry_list']):
        if entry.get('translations', False) and entry.get('lang', False):
            lang = entry.get('lang', False) + '/'
        else:
            lang = ''
        safe_title = re.sub('[\W]+', '-', entry['title'], re.U).lower().strip('-')
        url = config.get('www_root', '') + '/' \
            + str(entry.date.year) + '/' + lang + safe_title + '/'
        data['entry_list'][i]['url'] = url
    
    return request

@defaultfunc
def cb_item(request):
    """Creates single full-length entry.  Looks like
    http://domain.tld/year/$lang/title/(index.html).
    
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
            
    request = tools.run_callback(
            'setlang',
            request)
    
    dict = request._config
    entry_list = []
    mem = collections.defaultdict(list)
        
    for entry in data['entry_list']:
        
        translations = filter(lambda e: e != entry and
                e.get('translations', '') == entry.get('translations', False),
                data['entry_list'])
        log.debug("%s's translations: %s" % (entry.title, repr(translations)))
        
        if translations and not entry.get('lang', None):
            #log.warn
            pass
        print entry.url
                        
        entrydict = dict.copy()
        entrydict.update({'Post': entry})
        dict.update({'entry_list':tt_entry.render(entrydict) })
        # html = tt_main.render( dict )
        # 
        directory = os.path.join(config.get('output_dir', 'out'), 
                      str(entry.date.year),
                      entry.safe_title)
        path = os.path.join(directory, 'index.html')
        #tools.mk_file(html, entry, path)
    
    return request