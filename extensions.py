#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys, os, glob, fnmatch
import logging

plugins = []
callbacks = {}
log = logging.getLogger('lilith.extensions')

def index_plugin(module):
    """Goes through the plugin's contents and indexes all the funtions
    that start with cb_.  These functions are callbacks.
    
    Arguments:
    module -- the module to index
    """
    
    global callbacks
    
    props = dir(module)
    for mem in [item for item in props if item.startswith('cb_')]:
        func = getattr(module, mem)
        memadj = mem[3:]
        if callable(func):
            callbacks.setdefault(memadj, []).append(func)
            
def get_callback_chain(chain):
    """
    Returns a list of functions registered with the callback.

    @returns: list of functions registered with the callback (or an
        empty list)
    @rtype: list of functions
    """
    global callbacks
    
    return callbacks.get(chain, [])
            
def initialize(ext_dir, include=[], exclude=[]):
    """Imports and initializes extensions from the directories in the list
    specified by 'ext_dir'.  If no such list exists, the we don't load any
    plugins. 'include' and 'exclude' may contain a list of shell patterns
    used for fnmatch. If empty, this filter is not applied.
    
    Arguments:
    ext_dir -- list of directories
    include -- a list of filename patterns to include
    exclude -- a list of filename patterns to exclude
    """
    
    def get_name(filename):
        """Takes a filename and returns the module name from the filename."""
        return os.path.splitext(os.path.split(filename)[1])[0]
    
    def get_extension_list(ext_dir, include, exclude):
        """Load all plugins that matches include/exclude pattern in
        given lust of directories.  Arguments as in initializes(**kw)."""
        
        def pattern(name, incl, excl):
            for i in incl:
                if fnmatch.fnmatch(name, i): return True
            for e in excl:
                if fnmatch.fnmatch(name, e): return False
            if not incl:
                return True
            else:
                return False
                
        ext_list = []
        for mem in ext_dir:
            files = glob.glob(os.path.join(mem, "*.py"))
            files = [get_name(f) for f in files
                                    if pattern(get_name(f), include, exclude)]
            ext_list += files
        
        return sorted(ext_list)
    
    global plugins
    callbacks.clear()
    
    # handle ext_dir
    for mem in ext_dir[:]:
        if os.path.isdir(mem):
            sys.path.insert(0, mem)
        else:
            ext_dir.remove(mem)
            log.error("Extension directory '%s' does not exist. -- skipping" % mem)
            
    ext_list = get_extension_list(ext_dir, include, exclude)
    
    for mem in ext_list:
        try:
            _module = __import__(mem)
        except (SystemExit, KeyboardInterrupt):
            raise
        except:
            log.error("ImportError: %s.py" % mem)
            continue
        
        index_plugin(_module)
        plugins.append(_module)
    
    