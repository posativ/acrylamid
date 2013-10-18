# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.
#
# Provide a homogenous interface to Templating Engines like Jinja2

import abc


class AbstractEnvironment(object):
    """Generic interface for python templating engines like Jinja2 or Mako."""

    __metaclass__ = abc.ABCMeta

    extension = ['.html']

    @abc.abstractmethod
    def __init__(self, layoutdir, cachedir):
        """Initialize templating engine and set default layoutdir as well
        as cache dir. You should use a custom cache filename prefix like
        *__engine_hexcode.cache*."""
        return

    @abc.abstractmethod
    def register(self, name, func):
        """Register a :param function: to :param name:"""
        return

    @abc.abstractmethod
    def fromfile(self, env, path):
        """Load (relative) :param path: template and return a
        :class:`AbstractTemplate`-like class`."""
        return

    @abc.abstractmethod
    def extend(self, path):
        """Extend search PATH for templates by `path`."""
        return

    @abc.abstractproperty
    def loader(self):
        return


class AbstractTemplate(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, environment, path, template):
        self.environment = environment

        self.path = path
        self.template = template

        self.engine = environment.engine
        self.loader = environment.engine.loader

    @abc.abstractmethod
    def render(self, **dikt):
        """Render template with :param dikt:"""
        return
