# Copyright 2012 sebix <szebi@gmx.at>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid.filters import Filter
from acrylamid.errors import AcrylamidException

try:
    from textile import textile
except ImportError:
    textile = None


class PyTextile(Filter):

    match = ['Textile', 'textile', 'pytextile', 'PyTextile']
    conflicts = ['Markdown', 'reStructuredText', 'HTML', 'Pandoc']
    priority = 70.0

    def transform(self, text, entry, *args):

        if textile is None:
            raise AcrylamidException('Textile: PyTextile not available')
        return textile(text)
