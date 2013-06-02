# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import os
import imp
import markdown

from acrylamid.errors import AcrylamidException
from acrylamid.compat import string_types
from acrylamid.filters import Filter, discover


class Markdown(Filter):

    match = ['md', 'mkdown', 'markdown', 'Markdown']
    version = 2

    conflicts = ['rst', 'plain']
    priority = 70.0

    extensions = dict((x, x) for x in ['abbr', 'fenced_code', 'footnotes', 'headerid',
        'tables', 'codehilite', 'def_list', 'extra', 'smart_strong', 'nl2br',
        'sane_lists', 'wikilink', 'attr_list'])

    def init(self, conf, env):

        self.failed = []
        self.ignore = env.options.ignore

        markdown.Markdown  # raises ImportError eventually

        # -- discover markdown extensions --
        directories = conf['filters_dir'] + [os.path.dirname(__file__)]
        for filename in discover(directories, lambda path: path.startswith('mdx_')):
            modname, ext = os.path.splitext(os.path.basename(filename))
            fp, path, descr = imp.find_module(modname, directories)

            try:
                mod = imp.load_module(modname, fp, path, descr)
                mdx = mod.makeExtension()
                if isinstance(mod.match, string_types):
                    mod.match = [mod.match]
                for name in mod.match:
                    self.extensions[name] = mdx
            except (ImportError, Exception) as e:
                self.failed.append('%r %s: %s' % (filename, e.__class__.__name__, e))

    def __contains__(self, key):
        return True if key in self.extensions else False

    def transform(self, text, entry, *filters):

        val = []
        for f in filters:
            if f in self:
                val.append(f)
            else:
                x = f.split('(', 1)[:1][0]
                if x in self:
                    val.append(x)
                    self.extensions[x] = f
                elif not self.ignore:
                    raise AcrylamidException('Markdown: %s' % '\n'.join(self.failed))

        return markdown.Markdown(
            extensions=[self.extensions[m] for m in val],
            output_format='xhtml5'
        ).convert(text)
