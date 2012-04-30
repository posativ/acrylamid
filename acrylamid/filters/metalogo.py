# Copyright 2012 sebix <szebi@gmx.at>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
# Idea by http://nitens.org/taraborelli/texlogo

from acrylamid.filters import Filter
from acrylamid.errors import AcrylamidException

class Tex(Filter):

    match = ['metalogo']
    version = '1.0.0'

    priority = 70.0

    def transform(self, text, entry, *args):
        replacings = (('LaTeX', '<span class="latex">L<sup>a</sup>T<sub>e</sub>X</span>'),
                        ('XeTeX', '<span class="latex">X<sub>&#398;</sub>T<sub>e</sub>X</span>'),
                        ('TeX', '<span class="latex">T<sub>e</sub>X</span>'))
        for k in replacings:
            text = text.replace(k[0], k[1])
        return text
