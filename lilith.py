#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# TODO:
# - callback after rendering, but before write to file (e.g. tidy)
# - use file ext for markup, if #parser not specifed

VERSION = "0.1-dev"
VERSION_SPLIT = tuple(VERSION.split('-')[0].split('.'))

import sys, os
reload(sys); sys.setdefaultencoding('utf-8')

import locale
import yaml
import extensions, tools


class Lilith:
    """Main class for Lilith functionality.  It handles initialization,
    defines default behavior, and also pushes the request through all
    steps until the output is rendered and we're complete."""
    
    def __init__(self, config, environ, data=None):
        """Sets configuration and environment and creates the Request
        object
        
        config -- dict containing the configuration variables
        environ -- dict containing the environment variables
        """
        
        config['lilith_name'] = "lilith"
        config['lilith_version'] = VERSION
        
        self._config = config
        self._data = data
        self.request = Request(config, environ, data)
        
    def initialize(self):
        """The initialize step further initializes the Request by
        setting additional information in the ``data`` dict,
        registering plugins, and entryparsers.
        """
        data = self._data
        config = self._config

        # initialize the locale, if wanted (will silently fail if locale
        # is not available)
        if config.get('lang', None):
            try:
                locale.setlocale(locale.LC_ALL, config['lang'])
            except locale.Error:
                # invalid locale
                pass

        config['www_root'] = config.get('www_root', '')

        # take off the trailing slash for base_url
        if config['www_root'].endswith("/"):
            config['www_root'] = config['www_root'][:-1]

        # import and initialize plugins
        extensions.initialize(config.get("ext_dir", ['ext', ]),
                              exclude=config.get("ext_ignore", []))

        # entryparser callback is run here first to allow other
        # plugins register what file extensions can be used
    
    def run(self):
        """This is the main loop for lilith.  This method will run
        the handle callback to allow registered handlers to handle
        the request. If nothing handles the request, then we use the
        ``_lilith_handler``.
        """
        
        self.initialize()
        
        # run the start callback
        request = tools.run_callback('start', self.request)
        
        # run the default handler
        request = tools.run_callback("handle",
                        request,
                        mapping=lambda x,y:x)
                
        # do end callback
        request = tools.run_callback('end', request)
        
        from copy import deepcopy # performance? :S
        
        tools.run_callback('page', deepcopy(request),
                        mapping=lambda x,y: x)
        
        tools.run_callback('item', deepcopy(request),
                        mapping=lambda x,y: x)
        
        tools.run_callback('feed', deepcopy(request),
                        mapping=lambda x,y: x)
            
class Request(object):
    """This class holds the lilith request.  It holds configuration
    information, OS environment, and data that we calculate and
    transform over the course of execution."""
    
    def __init__(self, config, environ, data):
        """Sets configuration and environment.
        
        Arguments:
        config: dict containing configuration variables
        environ: dict containing environment variables
        adata: dict containing data variables"""
        
        self._data = data
        self._config = config
        self._environ = environ

if __name__ == '__main__':
    
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-c", "--config-file", dest="conf", metavar="FILE",
                      help="an alternative conf to use", default="lilith.conf")
    #parser.add_option("-o", "--overwrite", dest="force",
    #                  help="force overwrite", default=False)
    parser.add_option("-l", "--layout_dir", dest="layout", metavar="DIR",
                      help="force overwrite", default=False)
    
    (options, args) = parser.parse_args()
    
    conf = yaml.load(open(options.conf).read())
    if options.layout:
        conf['layout_dir'] = options.layout
    assert tools.check_conf(conf)
    l = Lilith(config=conf, environ={}, data={})
    l.run()
