# Copyright (c) 2010-2011, Gabriele Favalessa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import re
import markdown
import asciimathml

__match__ = ['mathml', 'math', 'asciimathml', 'MathML', 'Math', 'AsciiMathML']
__author__ = 'Gabriele Favalessa'

RE = re.compile(r'^(.*)\$([^\$]*)\$(.*)$', re.M)  # $ a $


class ASCIIMathMLExtension(markdown.Extension):
    def __init__(self, configs):
        pass

    def extendMarkdown(self, md, md_globals):
        self.md = md

        md.inlinePatterns.add('', ASCIIMathMLPattern(RE), '_begin')

    def reset(self):
        pass


class ASCIIMathMLPattern(markdown.inlinepatterns.Pattern):
    def getCompiledRegExp(self):
        return RE

    def handleMatch(self, m):
        math = asciimathml.parse(m.group(2).strip(), markdown.etree.Element, markdown.AtomicString)
        math.set('xmlns', 'http://www.w3.org/1998/Math/MathML')
        return math


def makeExtension(configs=None):
    return ASCIIMathMLExtension(configs=configs)
