# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

# XXX: add some useful extensions, system-filter to run shell commands

from acrylamid import log
from acrylamid.filters import Filter
from acrylamid.utils import render
from acrylamid.errors import AcrylamidException

from jinja2 import Environment, TemplateError
from subprocess import check_output, CalledProcessError, STDOUT


class Jinja2(Filter):
    """Jinja2 filter that pre-processes in Markdown/reStructuredText
    written posts. XXX: and offers some extensions."""

    match = ['Jinja2', 'jinja2']
    priority = 90.0

    def init(self, conf, env, *args):

        def system(cmd):
            try:
                return check_output(cmd, shell=True, stderr=STDOUT).strip()
            except (CalledProcessError, OSError) as e:
                log.warn('%s: %s' % (e.__class__.__name__, str(e)))
                return str(e)

        self.env = env
        self.conf = conf
        self.jinja2_env = Environment(cache_size=0)
        self.jinja2_env.filters['system'] = system

    def transform(self, content, req):

        try:
            return render(self.jinja2_env.from_string(content), conf=self.conf,
                          env=self.env, entry=req)
        except (TemplateError, AcrylamidException, OSError, TypeError) as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.message, req.filename))
            return content
