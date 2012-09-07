# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import os
import imp
import traceback

from acrylamid import log
from acrylamid.filters import Filter, discover

try:
    from docutils.core import publish_parts
    from docutils.parsers.rst import directives
except ImportError:
    publish_parts = None  # NOQA
    directives = None  # NOQA


class Restructuredtext(Filter):

    match = ['restructuredtext', 'rst', 'rest', 'reST', 'reStructuredText']
    version = '1.0.1'

    conflicts = ['markdown', 'plain']
    priority = 70.00

    def init(self, conf, env):

        self.extensions = {}
        self.ignore = env.options.ignore

        if not publish_parts or not directives:
            raise ImportError('reStructuredText: No module named docutils')

        # -- discover reStructuredText extensions --
        directories = conf['filters_dir'] + [os.path.dirname(__file__)]
        for filename in discover(directories, lambda path: path.startswith('rstx_')):
            modname, ext = os.path.splitext(os.path.basename(filename))
            fp, path, descr = imp.find_module(modname, directories)

            try:
                mod = imp.load_module(modname, fp, path, descr)
                rstx = mod.makeExtension()
                if isinstance(mod.match, basestring):
                    mod.match = [mod.__name__]
                for name in mod.match:
                    directives.register_directive(name, rstx)
            except (ImportError, Exception) as e:
                traceback.print_exc(file=sys.stdout)
                log.warn('%r %s: %s' % (filename, e.__class__.__name__, e))

    def transform(self, content, entry, *filters):

        settings = {
            'initial_header_level': 1,
            'doctitle_xform': 0
        }

        parts = publish_parts(content, writer_name='html', settings_overrides=settings)
        return parts['body']
