#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# TODO: donefunc chaos

import os, re
from datetime import datetime

import tools
from tools import FileEntry

from shpaml import convert_text
from jinja2 import Template

def cb_handle(request):
    """This is the default lilith handler.
        - cb_filelist
        - cb_filestat
        - cb_sortlist
        - cb_entryparser
            - cb_preformat
            - cb_format
            - cb_postformat
        - cb_item|feed|tags
        - cb_prepare
    """
    
    config = request._config
    data = request._data
                       
    # call the filelist callback to generate a list of entries
    request =  tools.run_callback(
            "filelist",
            request,
            donefunc=lambda x: x != None)
        
    # chance to modify specific meta data e.g. datetime
    request = tools.run_callback(
            'filestat', 
            request,
            donefunc=lambda x: x != None)
    
    # use datetime to sort chronological
    request  = tools.run_callback(
            'sortlist', 
            request,
            donefunc=lambda x: x != None)
            
    for i,entry in enumerate(request._data['entry_list']):
        request._data['entry_list'][i] = tools.run_callback(
                'entryparser',
                {'entry': entry, 'config': request._config},
                donefunc=lambda x: x != None)

def cb_filelist(request):
    """This is the default handler for getting entries.  It takes the
    request object in and figures out which entries bases on the default
    behavior that we want to show and generates a list of EntryBase
    subclass objects which it returns.
    
    Arguments:
    args -- dict containing the incoming Request object
    
    Returns the content we want to render"""
    
    data = request._data
    config = request._config
    
    filelist = []
    for root, dirs, files in os.walk(config.get('entries_dir', 'content')):
        filelist += [os.path.join(root, file) for file in files]
    
    entry_list = [FileEntry(request, e, config['entries_dir']) for e in filelist]
    data['entry_list'] = entry_list
    
    return request
    
def cb_filestat(request):
    
    entry_list = request._data['entry_list']
    for i in range(len(entry_list)):
        if entry_list[i].has_key('date'):
            entry_list[i]._date = datetime.strptime(entry_list[i]['date'],
                                            '%d.%m.%Y, %H:%M')
    return request
    
def cb_sortlist(request):
    
    entry_list = request._data['entry_list']
    entry_list.sort(key=lambda k: k._date, reverse=True)
    return request

def cb_entryparser(request):
    
    entry = request['entry']
    config = request['config']
    
    entry['body'] = tools.run_callback(
            'preformat',
            {'entry': entry, 'config': config},
            donefunc=lambda x: x != None,
            defaultfunc=lambda x: ''.join(x['entry']['story']))
            
    entry['body'] = tools.run_callback(
            'format',
            {'entry': entry, 'config': config},
            donefunc=lambda x: x != None)
            
    entry['body'] = tools.run_callback(
            'postformat',
            {'entry': entry, 'config': config},
            donefunc=lambda x: x != None,
            defaultfunc=lambda x: x['entry']['body'])
    
    return entry

def cb_format(args):
    entry = args['entry']
    config = args['config']
    
    parser = entry.get('parser', config.get('parser', 'plain'))
    
    if parser.lower() in ['markdown', 'mkdown', 'md']:
        from markdown import markdown
        return markdown(entry['body'],
                        extensions=['codehilite(css_class=highlight)'])
    elif parser.lower() in ['restructuredtest', 'rst', 'rest']:
        return entry['body']
    
    return entry['body']
    
def cb_prepare(request):
    
    config = request._config
    data = request._data
    for i, entry in enumerate(data['entry_list']):
        safe_title = re.sub('[\W]+', '-', entry['title'], re.U).lower()
        url = config.get('www_root', '') + '/' \
              + str(entry['_date'].year) + '/' + safe_title + '/'
        data['entry_list'][i]['safe_title'] = safe_title
        data['entry_list'][i]['url'] = url
        
    return request
    
def cb_item(request):

    tt_entry = Template(convert_text(open('layouts/entry.html').read()))
    tt_main = Template(open('layouts/main.html').read())
    config = request._config
    data = request._data
    
    data['type'] = 'item'
    
    # last preparations
    request = tools.run_callback(
            'prepare',
            request)
    
    dict = request._config
    entry_list = []
    
    for entry in data['entry_list']:
        dict.update({'entry_list': tt_entry.render({'Post': entry}) })
        html = tt_main.render( dict )
        
        directory = os.path.join(config.get('output_dir', 'out'),
                         str(entry._date.year),
                         entry.safe_title)
        path = os.path.join(directory, 'index.html')
        tools.mk_file(html, entry, path)

def cb_page(request):
    
    tt_entry = Template(convert_text(open('layouts/entry.html').read()))
    tt_main = Template(open('layouts/main.html').read())
    config = request._config
    data = request._data
    
    data['type'] = 'page'
    ipp = config.get('items_per_page', 6)
    
    # last preparations
    request = tools.run_callback(
            'prepare',
            request)
            
    dict = request._config
    entry_list = []
    for entry in data['entry_list']:
        entry_list.append(tt_entry.render({'Post': entry}))
                
    for i, mem in enumerate([entry_list[x*ipp:(x+1)*ipp] for x in range(len(entry_list))]):
        
        dict.update( {'entry_list': '\n'.join([entry for entry in mem])} )
        html = tt_main.render( dict )
        directory = os.path.join(config.get('output_dir', 'out'),
                         '' if i == 0 else 'page/%s' % (i+1))
        path = os.path.join(directory, 'index.html')
        tools.mk_file(html, {'title': 'page/%s' % (i+1)}, path)
        