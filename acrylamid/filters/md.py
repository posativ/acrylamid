# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os
import imp
import markdown

from acrylamid.filters import Filter, discover
from acrylamid.errors import AcrylamidException


class Markdown(Filter):

    match = ['md', 'mkdown', 'markdown', 'Markdown']
    version = '1.0.0'

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
                if isinstance(mod.match, basestring):
                    self.match.append(mod.match)
                    self.extensions[mod.__name__] = mdx
                else:
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

        md = markdown.Markdown(extensions=[self.extensions[m] for m in val])
        return md.convert(text)
