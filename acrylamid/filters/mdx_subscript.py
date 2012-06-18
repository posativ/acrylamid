# -*- encoding: utf-8 -*-
#
# Copyright (c) 2010, Shane Graber
#
# Subscript extension for Markdown.
#
# To subscript something, place a tilde symbol, '~', before and after the
# text that you would like in subscript: C~6~H~12~O~6~
# The numbers in this example will be subscripted. See below for more:
#
# Examples:
#
# >>> import markdown
# >>> md = markdown.Markdown(extensions=['subscript'])
# >>> md.convert('This is sugar: C~6~H~12~O~6~')
# u'<p>This is sugar: C<sub>6</sub>H<sub>12</sub>O<sub>6</sub></p>'
#
# Paragraph breaks will nullify subscripts across paragraphs. Line breaks
# within paragraphs will not.
#
# Modified to not subscript "~/Library. Foo bar, see ~/Music/".
#
# useful CSS rules:  sup, sub {
#                        vertical-align: baseline;
#                        position: relative;
#                        top: -0.4em;
#                    }
#                    sub { top: 0.4em; }

import markdown

match = ['subscript', 'sub']


class SubscriptPattern(markdown.inlinepatterns.Pattern):
    """Return a subscript Element: `C~6~H~12~O~6~'"""

    def handleMatch(self, m):

        text = m.group(3)

        if markdown.version_info < (2, 1, 0):
            el = markdown.etree.Element("sub")
            el.text = markdown.AtomicString(text)
        else:
            el = markdown.util.etree.Element("sub")
            el.text = markdown.util.AtomicString(text)

        return el


class SubscriptExtension(markdown.Extension):
    """Subscript Extension for Python-Markdown."""

    def extendMarkdown(self, md, md_globals):
        """Replace subscript with SubscriptPattern"""
        md.inlinePatterns['subscript'] = SubscriptPattern(r'(\~)([^\s\~]+)\2', md)


def makeExtension(configs=None):
    return SubscriptExtension(configs=configs)
