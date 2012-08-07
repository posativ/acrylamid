# -*- encoding: utf-8 -*-
#
# Copyright 2012 moschlar <mail@moritz-schlarb.de>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid import log
from acrylamid.filters import Filter
from acrylamid.helpers import system as defaultsystem
from acrylamid.errors import AcrylamidException

from mako.template import Template
from mako.exceptions import MakoException


class Mako(Filter):
    """Mako filter that pre-processes in Markdown/reStructuredText
    written posts. XXX: and offers some Mako extensions."""

    match = ['Mako', 'mako']
    version = '1.0.0'

    priority = 90.0

    def init(self, conf, env, *args):

        def system(cmd):
            try:
                return defaultsystem(cmd, shell=True).strip()
            except (OSError, AcrylamidException) as e:
                log.warn('%s: %s' % (e.__class__.__name__, e.args[0]))
                return e.args[0]

        self.conf = conf
        self.env = env
        self.filters = {'system': system, 'split': unicode.split}

    def transform(self, content, entry):

        try:
            tt = Template(content, cache_enabled=False, input_encoding='utf-8')
            #tt = self.jinja2_env.from_string(content)
            return tt.render(conf=self.conf, env=self.env, entry=entry)
        except (MakoException, AcrylamidException, OSError, TypeError) as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.args[0], entry.filename))
            return content
