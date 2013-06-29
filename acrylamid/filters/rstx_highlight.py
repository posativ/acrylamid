# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from docutils import nodes
from docutils.parsers.rst import Directive
from xml.sax.saxutils import escape


class Highlight(Directive):
    """Wrap source code to be used with `Highlight.js`_:

    .. _highlight.js: http://softwaremaniacs.org/soft/highlight/en/

    .. code-block:: rst

        .. highlight-js:: python

            print("Hello, World!")
    """

    optional_arguments = 1
    has_content = True

    def run(self):
        lang = None
        if len(self.arguments) >= 1:
            lang = self.arguments[0]
        if lang:
            tmpl = '<pre><code class="%s">%%s</code></pre>' % lang
        else:
            tmpl = '<pre><code>%s</code></pre>'
        html = tmpl % escape('\n'.join(self.content))
        raw = nodes.raw('', html, format='html')
        return [raw]


def register(roles, directives):
    directives.register_directive('highlight-js', Highlight)
