# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from __future__ import unicode_literals

from docutils import nodes
from docutils.parsers.rst import directives, Directive

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer


class Pygments(Directive):
    """Source code syntax highlighting using Pygments.

    .. code-block:: rst

        .. sourcecode:: python
            :linenos:

            #!/usr/bin/env python
            print("Hello World!)

    ``linenos`` enables line numbering (and is optional). A style sheet is not
    shipped with acrylamid, but you can easily get one with the ``pygmentize``
    script:

    ::

        $ pygmentize -S trac -f html > pygments.css

    To get a list of all available styles use the interactive python interpreter.

    ::

        >>> from pygments import styles
        >>> print list(styles.get_all_styles())

    .. _Pygments: http://pygments.org/
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


def register(roles, directives):
    for name in 'code-block', 'sourcecode', 'pygments':
        directives.register_directive(name, Pygments)
