# -*- encoding: utf-8 -*-
#
# Copyright 2012 sebix <szebi@gmx.at>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
# Idea by http://nitens.org/taraborelli/texlogo

from acrylamid.filters import Filter

LaTeX = """\
<span style="font-family: cmr10, LMRoman10-Regular, Times, serif; letter-spacing: 0.075em;">L
<span style="text-transform: uppercase; font-size: 70%; margin-left: -0.36em; vertical-align: 0.3em; line-height: 0; margin-right: -0.15em;">a</span>T
<span style="text-transform: uppercase; margin-left: -0.1667em; vertical-align: -0.5ex; line-height: 0; margin-right: -0.125em;">e
</span>X</span>
""".strip().replace('\n', '')

TeX = """\
<span style="font-family: cmr10, LMRoman10-Regular, Times, serif; letter-spacing: 0.075em;">T
<span style="text-transform: uppercase; margin-left: -0.1667em; vertical-align: -0.5ex; line-height: 0; margin-right: -0.125em;">e
</span>X</span>
""".strip().replace('\n', '')

XeTeX = u"""\
<span style="font-family: cmr10, LMRoman10-Regular, Times, serif; letter-spacing: 0.075em;">X
<span style="text-transform: uppercase; margin-left: -0.1367em; vertical-align: -0.5ex; line-height: 0; margin-right: -0.125em;">ǝ
</span>T
<span style="text-transform: uppercase; margin-left: -0.1667em; vertical-align: -0.5ex; line-height: 0; margin-right: -0.125em;">e
</span>X</span>
""".strip().replace('\n', '')


class Tex(Filter):

    match = ['metalogo']
    version = '1.2.0'

    def transform(self, text, entry, *args):
        replacings = (('LaTeX', LaTeX),
                        ('XeTeX', XeTeX),
                        ('TeX', TeX))
        for k in replacings:
            text = text.replace(k[0], k[1])
        return text
