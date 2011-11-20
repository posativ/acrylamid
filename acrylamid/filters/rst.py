#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import os
import markdown

from acrylamid.filters import Filter
from acrylamid.filters import log

from docutils import nodes
from docutils.parsers.rst import directives, Directive
from docutils.core import publish_parts
        
from pygments.formatters import HtmlFormatter
from docutils import nodes
from docutils.parsers.rst import directives, Directive

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer

# Set to True if you want inline CSS styles instead of classes
inlinestyles = False

class Restructuredtext(Filter):
    
    __name__ = 'RestructuredText'
    __match__ = ['restructuredtext', 'rst', 'rest', 'reST', 'RestructuredText']
    __conflicts__ = ['markdown', 'plain']
    __priority__ = 70.00
    
    __ext__ = dict((x,x) for x in [])
        
    def __init__(self, conf, env):
        self.formatter = HtmlFormatter(noclasses=inlinestyles)
    
        class Pygments(Directive):
            """ Source code syntax hightlighting."""
            required_arguments = 1
            optional_arguments = 0
            final_argument_whitespace = True
            option_spec = dict([(key, directives.flag) for key in {}])
            has_content = True

            def run(self):
                self.assert_has_content()
                try:
                    lexer = get_lexer_by_name(self.arguments[0])
                except ValueError:
                    # no lexer found - use the text one instead of an exception
                    lexer = TextLexer()
                # take an arbitrary option if more than one is given
                formatter = HtmlFormatter(noclasses=inlinestyles)
                parsed = highlight(u'\n'.join(self.content), lexer, formatter)
                return [nodes.raw('', parsed, format='html')]
    
        directives.register_directive('sourcecode', Pygments)
            
    def __call__(self, content, request, *filters):
        initial_header_level = 1
        transform_doctitle = 0
        settings = {
            'initial_header_level': initial_header_level,
            'doctitle_xform': transform_doctitle
            }
        parts = publish_parts(content, writer_name='html', settings_overrides=settings)
        return parts['body'].encode('utf-8')
