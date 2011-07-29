#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see lilith.py

import locale
import logging

from lilith import core
from lilith import extensions
from lilith import tools

from jinja2 import Template

log = logging.getLogger('lilith')

class Lilith:
    """Main class for Lilith functionality.  It handles initialization,
    defines default behavior, and also pushes the request through all
    steps until the output is rendered and we're complete."""
    
    def __init__(self, conf, env=None, data=None):
        """Sets configuration and environment and creates the Request
        object
        
        config -- dict containing the configuration variables
        environ -- dict containing the environment variables
        """
        
        conf['lilith_name'] = "lilith"
        conf['lilith_version'] = env['VERSION']
        
        conf['output_dir'] = conf.get('output_dir', 'output/')
        conf['entries_dir'] = conf.get('entries_dir', 'content/')
        conf['layout_dir'] = conf.get('layout_dir', 'layouts/')
        
        self._config = conf
        self._data = data
        self._env = env
        self.request = Request(conf, env, data)
        
    def initialize(self):
        """The initialize step further initializes the Request by
        setting additional information in the ``data`` dict,
        registering plugins, and entryparsers.
        """
        data = self._data
        conf = self._config

        # initialize the locale, will silently fail if locale is not
        # available and uses system's locale
        try:
            locale.setlocale(locale.LC_ALL, conf.get('lang', False))
        except (locale.Error, TypeError):
            # invalid locale
            log.warn('unsupported locale `%s`' % conf['lang'])
            locale.setlocale(locale.LC_ALL, '')
            conf['lang'] = locale.getlocale()

        if conf.get('www_root', None):
            conf['www_root'] = conf.get('www_root', '')
            conf['protocol'] = 'https' if conf['www_root'].find('https') == 0 \
                                      else 'http'
        else:
            log.warn('no `www_root` specified, using localhost:8000')
            conf['www_root'] = 'http://localhost:8000/'
            conf['protocol'] = 'http'

        # take off the trailing slash for base_url
        if conf['www_root'].endswith("/"):
            conf['www_root'] = conf['www_root'][:-1]

        # import and initialize plugins
        extensions.initialize(conf.get("ext_dir", ['ext', ]),
                              exclude=conf.get("ext_ignore", []),
                              include=conf.get("ext_include", []))
        
        conf['extensions'] = [ex.__name__ for ex in extensions.plugins]
    
    def run(self):
        """This is the main loop for lilith.  This method will run
        the handle callback to allow registered handlers to handle
        the request. If nothing handles the request, then we use the
        ``_lilith_handler``.
        """
        
        self.initialize()
        
        # run the start callback, initialize jinja2 template
        log.debug('cb_start')
        request = tools.run_callback(
                        'start',
                        self.request,
                        defaultfunc=core.start)
        
        # run the default handler
        log.debug('cb_handle')
        request = tools.run_callback(
                        "handle",
                        request,
                        defaultfunc=lilith_handler)
                
        # do end callback
        tools.run_callback('end', request)


class Request(object):
    """This class holds the lilith request.  It holds configuration
    information, OS environment, and data that we calculate and
    transform over the course of execution."""
    
    def __init__(self, conf, env, data):
        """Sets configuration and data.
        
        Arguments:
        config: dict containing configuration variables
        data: dict containing data variables"""
        
        self._data = data
        self._config = conf
        self._env = env

def lilith_handler(request):
    """This is the default lilith handler.
        - cb_filelist
        - cb_filestat
        - cb_sortlist
        - cb_entryparser
            - cb_preformat
            - cb_format
            - cb_postformat
        - cb_prepare
    """
    
    from core import filelist, filestat, sortlist, entryparser, prepare, \
                     item, page
    
    conf = request._config
    data = request._data
                       
    # call the filelist callback to generate a list of entries
    #log.debug('cb_filelist')
    request =  tools.run_callback(
            "filelist",
            request,
            defaultfunc=filelist)
        
    # chance to modify specific meta data e.g. datetime
    request = tools.run_callback(
            'filestat', 
            request,
            defaultfunc=filestat)
    
    # use datetime to sort chronological
    request = tools.run_callback(
            'sortlist', 
            request,
            defaultfunc=sortlist)
            
    # entry specific callbacks
    for i,entry in enumerate(request._data['entry_list']):
        request._data['entry_list'][i] = tools.run_callback(
                'entryparser',
                {'entry': entry, 'config': request._config},
                defaultfunc=entryparser)
                
    request = tools.run_callback(
            'prepare',
            request,
            defaultfunc=prepare)
    
    from copy import deepcopy # performance? :S
    
    tools.run_callback(
        'item',
        deepcopy(request),
        defaultfunc=item)
    
    tools.run_callback(
        'page',
        deepcopy(request),
        defaultfunc=page)
    
    return request