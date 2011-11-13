#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import sys, os, glob, fnmatch
import logging

sys.path.insert(0, os.path.dirname(__file__))
log = logging.getLogger('acrylamid.views')

callbacks = []

def get_views():
    
    global callbacks
    return [cb for cb in callbacks if getattr(sys.modules['acrylamid.views'], cb.__module__).enabled]


def index_views(module, conf, env):
    """Goes through the modules' contents and indexes all the funtions/classes
    having a __call__ and __match__ attribute.

    Arguments:
    module -- the module to index
    """

    global callbacks
    
    if not hasattr(module, 'enabled'):
        raise ImportError("'enabled' property is missing")

    cs = [getattr(module, c) for c in dir(module) if not c.startswith('_')]
    for mem in cs:
        if hasattr(mem, '__view__') and getattr(mem, '__view__') \
        and hasattr(mem, '__call__') and hasattr(mem, '__init__'):
            callbacks.append(mem(conf, env))


def initialize(ext_dir, conf, env):
    
    global callbacks

    # handle ext_dir
    for mem in ext_dir[:]:
        if os.path.isdir(mem):
            sys.path.insert(0, mem)
        else:
            ext_dir.remove(mem)
            log.error("Extension directory '%s' does not exist. -- skipping" % mem)

    ext_dir.extend([os.path.dirname(__file__)])
    ext_list = []
    for mem in ext_dir:
        files = glob.glob(os.path.join(mem, "*.py"))
        ext_list += files
    
    for mem in [os.path.basename(x).replace('.py', '') for x in ext_list]:
        if mem.startswith('_'):
            continue
        try:
            _module = __import__(mem)
            sys.modules[__package__].__dict__[mem] = _module
            index_views(_module, conf, env)
        except (ImportError, Exception), e:
            print `mem`, 'ImportError:', e
            continue


class View:
    
    __view__ = True