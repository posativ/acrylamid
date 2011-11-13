#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see lilith.py

import os
import markdown

from lilith.filters import Filter
from lilith.filters import log

class Markdown(Filter):
    
    __name__ = 'Markdown'
    __match__ = ['md', 'mkdown', 'markdown', 'Markdown']
    __conflicts__ = ['rst', 'plain']
    
    __ext__ = dict((x,x) for x in ['abbr', 'fenced_code', 'footnotes',
                                   'headerid', 'tables', 'codehilite'])

    def __init__(self, **env):
        
        self.env = env
        # -- discover markdown extensions --
        
        for mem in os.listdir(os.path.dirname(__file__)):
            if mem.startswith('mdx_') and mem.endswith('.py'):
                try:
                    mod = __import__(mem.replace('.py', ''))
                    mdx = mod.makeExtension()
                    if isinstance(mod.__match__, basestring):
                        self.__match__.append(mod.__match__)
                        self.__ext__[mod.__name__] = mdx
                    else:
                        for name in mod.__match__:
                            self.__ext__[name] = mdx
                except (ImportError, Exception), e:
                    print `mem`, 'ImportError:', e

    def __contains__(self, key):
        return True if key in self.__ext__ else False
        
    def __call__(self, content, request, *filters):
        
        err = []; val = []
        for f in filters:
            if f in self:
                val.append(f)
            else:
                x = f.split('(', 1)[:1][0]
                if not x in self:
                    log.warn('%s is not available' % x)
                else:
                    val.append(x)
                    self.__ext__[x] = f

        md = markdown.Markdown(extensions=[self.__ext__[m] for m in val])
        return md.convert(content)
