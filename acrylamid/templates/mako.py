# -*- encoding: utf-8 -*-
#
# Copyright 2012 moschlar <mail@moritz-schlarb.de>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from __future__ import absolute_import

import os, stat

from acrylamid.templates import AbstractEnvironment, AbstractTemplate
from mako.lookup import TemplateLookup


class Environment(AbstractEnvironment):

    def init(self, layoutdir, cachedir):
        self.mako = TemplateLookup(directories=[layoutdir],
            module_directory=cachedir,
            input_encoding='utf-8')
        self.filters = {}
        return

    def register(self, name, func):
        self.filters[name] = func

    def fromfile(self, path):
        return Template(self.mako.get_template(path), self.filters)


class Template(AbstractTemplate):

    def __init__(self, template, filters={}):
        self.template = template
        self.filters = filters

    def render(self, **kw):
        # we inject the filter functions as top-level objects into the template,
        # that's probably the only way that works with Mako
        kw.update(self.filters)
        return self.template.render_unicode(**kw)
        # For debugging template compilation:
        # TODO: Integrate this with acrylamid somehow
        #from mako import exceptions as mako_exceptions
        #try:
        #    return self.template.render(**kw)
        #except:
        #    print mako_exceptions.text_error_template().render()
        #    return unicode(mako_exceptions.html_error_template().render())

    @property
    def has_changed(self):
        # inspired by mako.lookup.TemplateLookup._check
        template_stat = os.stat(self.template.filename)
        if self.template.last_modified < template_stat[stat.ST_MTIME]:
            return True
        else:
            return False
