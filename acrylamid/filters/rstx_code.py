# -*- encoding: utf-8 -*-
#
# Copyright: (c) 2010-2012 by Rafael Goncalves Martins
# License: GPL-2, see https://hg.rafaelmartins.eng.br/blohg/file/tip/LICENSE for more details.

from docutils import nodes
from docutils.parsers.rst import Directive

match = 'code'


class Code(Directive):
    """reStructuredText directive that creates a pre tag suitable for
    decoration with http://alexgorbatchev.com/SyntaxHighlighter/

    Usage example::

        .. source:: python

           print "Hello, World!"

        .. raw:: html

            <script type="text/javascript" src="http://alexgorbatchev.com/pub/sh/current/scripts/shCore.js"></script>
            <script type="text/javascript" src="http://alexgorbatchev.com/pub/sh/current/scripts/shBrushPython.js"></script>
            <link type="text/css" rel="stylesheet" href="http://alexgorbatchev.com/pub/sh/current/styles/shCoreDefault.css"/>
            <script type="text/javascript">SyntaxHighlighter.defaults.toolbar=false; SyntaxHighlighter.all();</script>
    """

    required_arguments = 1
    optional_arguments = 0
    has_content = True

    def run(self):
        self.assert_has_content()
        self.options['brush'] = self.arguments[0]
        html = '''\

<pre class="brush: %s">
%s
</pre>

'''
        return [nodes.raw('', html % (self.options['brush'],
            "\n".join(self.content).replace('<', '&lt;')),
            format='html')]


def makeExtension():
    return Code
