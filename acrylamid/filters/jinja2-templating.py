# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid import log
from acrylamid.filters import Filter
from acrylamid.helpers import system as defaultsystem
from acrylamid.errors import AcrylamidException

from jinja2 import Environment, TemplateError


class Jinja2(Filter):
    """Jinja2 filter that pre-processes in Markdown/reStructuredText
    written posts. XXX: and offers some jinja2 extensions."""

    match = ['Jinja2', 'jinja2']
    version = '1.0.0'

    priority = 90.0

    def init(self, conf, env, *args):

        def system(cmd, stdin=None):
            try:
                return defaultsystem(cmd, stdin, shell=True).strip()
            except (OSError, AcrylamidException) as e:
                log.warn('%s: %s' % (e.__class__.__name__, e.args[0]))
                return e.args[0]

        self.conf = conf
        self.env = env

        # jinja2 is stupid and can't import any module
        import time, datetime, urllib

        self.jinja2_env = Environment(cache_size=0)
        self.jinja2_env.filters['system'] = system
        self.jinja2_env.filters['split'] = unicode.split
        self.jinja2_env.filters.update({
            'time': time, 'datetime': datetime, 'urllib': urllib,
            })

        for module in (time, datetime, urllib):
            for name in dir(module):
                if name.startswith('_'):
                    continue

                self.jinja2_env.filters[module.__name__ + '.' + name] = getattr(module, name)

    def transform(self, content, entry):

        try:
            tt = self.jinja2_env.from_string(content)
            return tt.render(conf=self.conf, env=self.env, entry=entry)
        except (TemplateError, AcrylamidException) as e:
            log.warn('%s: %s in %r' % (e.__class__.__name__, e.args[0], entry.filename))
            return content
