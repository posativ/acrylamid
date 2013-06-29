# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from docutils.parsers.rst.directives import body

def register(roles, directives):
    for name in 'code-block', 'sourcecode', 'pygments':
        directives.register_directive(name, body.CodeBlock)
