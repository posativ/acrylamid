# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid import log
from acrylamid.filters import Filter
from acrylamid.utils import system as defaultsystem
from acrylamid.errors import AcrylamidException

from jinja2 import Environment, TemplateError


class Jinja2(Filter):
    """Jinja2 filter that pre-processes in Markdown/reStructuredText
    written posts. XXX: and offers some jinja2 extensions."""

    match = ['Jinja2', 'jinja2']
    version = '1.0.0'

    priority = 90.0

    def init(self, conf, env, *args):

        def system(cmd):
            try:
                return defaultsystem(cmd, shell=True).strip()
            except (OSError, AcrylamidException) as e:
                log.warn('%s: %s' % (e.__class__.__name__, str(e)))
                return str(e)

        self.conf = conf
        self.env = env

        self.jinja2_env = Environment(cache_size=0)
        self.jinja2_env.filters['system'] = system

    def transform(self, content, entry):

        try:
            tt = self.jinja2_env.from_string(content)
            return tt.render(conf=self.conf, env=self.env, entry=entry)
        except (TemplateError, AcrylamidException, OSError, TypeError) as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.message, entry.filename))
            return content
