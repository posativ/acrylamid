# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

from acrylamid import log
from acrylamid.filters import Filter
from acrylamid.utils import render

from jinja2 import Environment, TemplateError


class Jinja2(Filter):
    """Jinja2 filter that pre-processes in Markdown/reStructuredText
    written posts and offers some extensions."""

    __name__ = 'Jinja2'
    __match__ = ['Jinja2', 'jinja2']
    __priority__ = 90.0

    def __init__(self, conf, env, *args):

        self.env = env
        self.conf = conf
        self.jinja2_env = Environment(cache_size=0)

    def __call__(self, content, req):

        try:
            return render(self.jinja2_env.from_string(content), conf=self.conf,
                          env=self.env, entry=req)
        except TemplateError as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.message, req.filename))
            return content
