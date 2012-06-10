# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from __future__ import unicode_literals

from docutils import nodes
from docutils.parsers.rst import directives, Directive

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

match = ['code-block', 'sourcecode', 'pygments']


class Pygments(Directive):
    """ Source code syntax hightlighting using Pygments.

    Usage example::

        .. sourcecode:: python
            :linenos:

            #!/usr/bin/env python
            print "Hello World!

    ``linenos`` enables line numbering. A pygment CSS is not provided by
    acrylamid but can easily get one by using the ``pygmentize`` script
    shipped with Pygments.

    ::

        $> pygmentize -S trac -f html > pygments.css

    To get a list of all available styles use the interactive python interpreter.

    ::

        >>> from pygments import styles
        >>> print list(styles.get_all_styles())
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        'linenos': directives.flag,
    }

    def run(self):
        self.assert_has_content()
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()
        formatter = HtmlFormatter(noclasses=False)
        if 'linenos' in self.options:
            formatter.linenos = 2
        parsed = highlight('\n'.join(self.content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]


def makeExtension():
    return Pygments
