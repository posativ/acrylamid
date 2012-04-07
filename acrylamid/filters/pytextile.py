# Copyright 2012 sebix <szebi@gmx.at>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid.filters import Filter
from acrylamid.errors import AcrylamidException

class PyTextile(Filter):

    match = ['Textile', 'textile', 'pytextile', 'PyTextile']
    conflicts = ['Markdown', 'reStructuredText', 'HTML', 'Pandoc']
    priority = 70.0

    def init(self, conf, env):
        self.ignore = env.options.ignore

    def transform(self, text, entry, *args):
        try:
            from textile import textile
        except ImportError:
            raise AcrylamidException('Textile: PyTextile not available')
        return textile(text)
