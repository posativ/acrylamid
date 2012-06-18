# -*- encoding: utf-8 -*-
#
# - Copyright 2011, 2012 The Active Archives contributors
# - Copyright 2011, 2012 Alexandre Leray
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the <organization> nor the names of its contributors may
#    be used to endorse or promote products derived from this software without
#    specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE PYTHON MARKDOWN PROJECT ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL ANY CONTRIBUTORS TO THE PYTHON MARKDOWN PROJECT
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Del/Ins Extension for Python-Markdown
# =====================================
#
# Wraps the inline content with ins/del tags.
#
#
# Usage
# -----
#
# >>> import markdown
# >>> src = """This is ++added content++ and this is ~~deleted content~~"""
# >>> html = markdown.markdown(src, ['del_ins'])
# >>> print(html)
# <p>This is <ins>added content</ins> and this is <del>deleted content</del>
# </p>

import markdown
from markdown.inlinepatterns import SimpleTagPattern

match = ['delins']


class DelInsExtension(markdown.extensions.Extension):
    """Adds del_ins extension to Markdown class."""

    def extendMarkdown(self, md, md_globals):
        """Modifies inline patterns."""
        md.inlinePatterns.add('del', SimpleTagPattern(r"(\~\~)(.+?)(\~\~)", 'del'), '<not_strong')
        md.inlinePatterns.add('ins', SimpleTagPattern(r"(\+\+)(.+?)(\+\+)", 'ins'), '<not_strong')


def makeExtension(configs={}):
    return DelInsExtension(configs=dict(configs))
