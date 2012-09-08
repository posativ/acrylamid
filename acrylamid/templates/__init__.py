# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# Provide a homogenous interface to Templating Engines like Jinja2

import abc


class AbstractEnvironment(object):
    """Generic interface for python templating engines like Jinja2 or Mako.
    They need to support filters and loading templates from files. To keep
    Acrylamid fast, they should cache them."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def init(self, layoutdir, cachedir):
        """Initialize templating engine and set default layoutdir as well
        as cache dir. You should use a custom cache filename prefix like
        *__engine_hexcode.cache*."""
        return

    @abc.abstractmethod
    def register(self, name, func):
        """Register a :param function: to :param name:"""
        return

    @abc.abstractmethod
    def fromfile(self, path):
        """Load (relative) :param path: template and return a
        :class:`AbstractTemplate`-like class`."""
        return

    @abc.abstractproperty
    def templates(self):
        """Return the path of all currently processed templates."""
        return


class AbstractTemplate(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def render(self, **dikt):
        """Render template with :param dikt:"""
        return

    @abc.abstractproperty
    def has_changed(self):
        """Return ``True`` when the template has changed but make sure this value
        does not change over the whole compilation process. Return ``False`` if the
        template has not changed, cache this too!"""
        return
