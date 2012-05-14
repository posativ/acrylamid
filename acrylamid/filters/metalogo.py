# Copyright 2012 sebix <szebi@gmx.at>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
# Idea by http://nitens.org/taraborelli/texlogo

from acrylamid.filters import Filter

CSS = """\
/* LaTeX */

.latex {
  font-family: Times, "Times New Roman", serif;
  letter-spacing: 1px;
}

.latex sup {
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85em;
  vertical-align: 0.15em;
  margin-left: -0.36em;
  margin-right: -0.15em;
}

.latex sub {
  text-transform: uppercase;
  vertical-align: -0.5ex;
  margin-left: -0.1667em;
  margin-right: -0.125em;
  font-size: 1em;
}"""

class Tex(Filter):

    match = ['metalogo']
    version = '1.0.0'

    priority = 70.0

    def inject(self):

        return {
            'text/css': CSS,
        }

    def transform(self, text, entry, *args):
        replacings = (('LaTeX', '<span class="latex">L<sup>a</sup>T<sub>e</sub>X</span>'),
                        ('XeTeX', '<span class="latex">X<sub>&#398;</sub>T<sub>e</sub>X</span>'),
                        ('TeX', '<span class="latex">T<sub>e</sub>X</span>'))
        for k in replacings:
            text = text.replace(k[0], k[1])
        return text
