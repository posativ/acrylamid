#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import tools
from datetime import datetime
from tools import FileEntry

def cb_handle(request):
    """This is the default lilith handler.
        - cb_filelist
        - cb_filestat
        - cb_sortlist
        - cb_entryparser
            - cb_preformat
            - cb_format
            - cb_postformat
        - cb_layout
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
        print entry['body']
        break
        

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
    entry_list.sort(key=lambda k: k._date)
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
        return markdown(entry['body'], extensions=['codehilite(css_class=highlight)'])
    elif parser.lower() in ['restructuredtest', 'rst', 'rest']:
        return entry['body']
    
    return entry['body']