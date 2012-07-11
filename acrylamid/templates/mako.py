# -*- encoding: utf-8 -*-
#
# Copyright 2012 moschlar <mail@moritz-schlarb.de>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from __future__ import absolute_import

from acrylamid.templates import AbstractEnvironment, AbstractTemplate
from mako.lookup import TemplateLookup


class Environment(AbstractEnvironment):

    def init(self, layoutdir, cachedir):
        self.mako = TemplateLookup(directories=[layoutdir],
            module_directory=cachedir, default_filters=['unicode'],
            input_encoding='utf-8')
        return

    def register(self, name, func):
        # TODO: Don't know how to do that in mako
        return

    def fromfile(self, path):
        return Template(self.mako.get_template(path))


class Template(AbstractTemplate):

    def __init__(self, template):
        self.template = template

    def render(self, **kw):
        return self.template.render(**kw)
        # For debugging template compilation:
        # TODO: Integrate this with acrylamid somehow
        #from mako import exceptions as mako_exceptions
        #try:
        #    return self.template.render(**kw)
        #except:
        #    print mako_exceptions.text_error_template().render()
        #    return unicode(mako_exceptions.html_error_template().render())

    def has_changed(self):
        # TODO: Dummy function
        return True
