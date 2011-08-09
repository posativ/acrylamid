#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
# 
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
# 
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of posativ <info@posativ.org>.

VERSION = "0.1.8-dev"
VERSION_SPLIT = tuple(VERSION.split('-')[0].split('.'))

import sys
reload(sys); sys.setdefaultencoding('utf-8')

import os, logging, locale
from optparse import OptionParser, make_option, OptionGroup
from datetime import datetime

from os.path import abspath

from lilith import extensions
from lilith import tools
from lilith import defaults
from lilith.tools import check_conf, ColorFormatter

import yaml
from jinja2 import Template

log = logging.getLogger('lilith')

class Lilith:
    """Main class for Lilith functionality.  It handles initialization,
    defines default behavior, and also pushes the request through all
    steps until the output is rendered and we're complete."""
    
    def __init__(self):
        """Sets configuration and environment and creates the Request
        object
        
        config -- dict containing the configuration variables
        environ -- dict containing the environment variables
        """
        
        options = [
            make_option("-q", "--quit", action="store_const", dest="verbose",
                              help="be silent (mostly)", const=logging.WARN,
                              default=logging.INFO),
            make_option("-v", "--verbose", action="store_const", dest="verbose",
                              help="debug information", const=logging.DEBUG),
            make_option("-f", "--force", action="store_true", dest="force",
                              help="force overwriting", default=False)
            ]
            
        parser = OptionParser(option_list=options)
        ext_group = OptionGroup(parser, "lilith.yaml override")
        
        for key, value in yaml.load(defaults.conf).iteritems():
            ext_group.add_option('--'+key.replace('_', '-'), action="store",
                            dest=key, metavar=value, default=value,
                            type=type(value) if type(value) != list else str)
                            
        parser.add_option_group(ext_group)
        (options, args) = parser.parse_args()
    
        console = logging.StreamHandler()
        console.setFormatter(ColorFormatter('[%(levelname)s]  %(message)s'))
        if options.verbose == logging.DEBUG:
            fmt = '%(msecs)d [%(levelname)s] %(name)s.py:%(lineno)s:%(funcName)s %(message)s'
            console.setFormatter(ColorFormatter(fmt))
        log = logging.getLogger('lilith')
        log.addHandler(console)
        log.setLevel(options.verbose)
        
        if 'init' in args:
            if len(args) == 2:
                defaults.init(args[1], options.force)
            else:
                defaults.init(overwrite=options.force)
            sys.exit(0)
        
        env={'VERSION': VERSION, 'VERSION_SPLIT': VERSION_SPLIT}
        
        try:
            conf = yaml.load(open(options.conf).read())
        except OSError:
            log.critical('no config file found: %s. Try "lilith init".', options.conf)
            sys.exit(1)
        
        if options.layout:
            conf['layout_dir'] = options.layout
        assert check_conf(conf)
                
        conf['lilith_name'] = "lilith"
        conf['lilith_version'] = env['VERSION']
        
        conf['output_dir'] = abspath(conf.get('output_dir', 'output/'))
        conf['entries_dir'] = abspath(conf.get('entries_dir', 'content/'))
        conf['layout_dir'] = abspath(conf.get('layout_dir', 'layouts/'))
        
        self._config = conf
        self._env = env
        self.request = Request(conf, env, {})
        
    def initialize(self):
        """The initialize step further initializes the Request by
        setting additional information in the ``data`` dict,
        registering plugins, and entryparsers.
        """
        
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
        
        
        if len(args) != 1:
            print conf['lilith_name'] + ' ' + conf['lilith_version']
            sys.exit(0)
        
        if args[0] == 'init':
            self.init(options = options)

                
    def run(self):
        """This is the main loop for lilith.  This method will run
        the handle callback to allow registered handlers to handle
        the request. If nothing handles the request, then we use the
        ``_lilith_handler``.
        """
        
        from lilith.core import start
        
        self.initialize()
        
        # run the start callback, initialize jinja2 template
        log.debug('cb_start')
        request = tools.run_callback(
                        'start',
                        self.request,
                        defaultfunc=start)
        
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
        
class FileEntry:
    """This class gets it's data and metadata from the file specified
    by the filename argument"""
    
    def __init__(self, request, filename, new=True):
        """Arguments:
        request -- the Request object
        filename -- the complete filename including path
        datadir --  the data dir
        """
        self._config = request._config
        self._filename = filename.replace(os.sep, '/')
        self._new = new
        
        self._date = datetime.fromtimestamp(os.path.getmtime(filename))
        self._populate()
        
    def __repr__(self):
        return "<fileentry f'%s'>" % (self._filename)
        
    def __contains__(self, key):
        return True if key in self.__dict__.keys() else False

    def __getitem__(self, key, default=None):
        # if key == 'body':
        #     print 1
        #     pass
        #     
        if key in self:
            return self.__dict__[key]
        else:
            return default
        
    def __setitem__(self, key, value):
        """Set metadata.  No underscore in front of `key` is allowed!"""
        if key.find('_') == 0:
            raise ValueError('invalid metadata variable: %s' % key)
        self.__dict__[key] = value
        
    def keys(self):
        return self.__dict__.keys()
        
    def has_key(self, key):
        return self.__contains__(key)
    
    def iteritems(self):
        for key in self.keys():
            yield (key, self[key])
        
    get = __getitem__

    def _populate(self):
        """Populates the yaml header and splits the content.  """
        f = open(self._filename, 'r')
        lines = f.readlines()
        f.close()
        
        data = {}
    
        # if file is empty, return a blank entry data object
        if len(lines) == 0:
            data['title'] = ''
            data['story'] = []
        else:
            lines.pop(0) # first `---`
            meta = []
            for i, line in enumerate(lines):
                if line.find('---') == 0:
                    break
                meta.append(line)
            lines.pop(0) # last `---`            

            for key, value in yaml.load(''.join(meta)).iteritems():
                data[key] = value

            # optional newline after yaml header
            lines = lines[i:] if lines[i].strip() else lines[i+1:]

            # call the preformat function
            data['parser'] = data.get('parser', self._config.get('parser', 'plain'))
            data['story'] = lines
        
            for key, value in data.iteritems():
                self[key] = value

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