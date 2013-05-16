# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.
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
    def fromfile(self, env, path):
        """Load (relative) :param path: template and return a
        :class:`AbstractTemplate`-like class`."""
        return

    @abc.abstractmethod
    def extend(self, path):
        """Extend search path for templates by `path`."""
        return

    @abc.abstractproperty
    def extension(self):
        """Return the default templating extension(s)."""
        return

    @abc.abstractproperty
    def templates(self):
        """A dictionary mapping of template name -> Template object."""
        return

    @abc.abstractproperty
    def modified(self):
        """A dictionary mapping of template name -> modified or not"""
        return

    @abc.abstractproperty
    def resolved(self):
        """A dictionary mapping of template name -> (fully resolved)
        referenced template names."""
        return

    @abc.abstractproperty
    def assets(self):
        """A dictionary mapping of template name/path -> bundle arguments and
        keyword arguments.

        You can fill this dictionary on-demand, that means this attribute is
        always called after parsing the template.
        """


class AbstractTemplate(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def name(self):
        """The name/path of the template (e.g. main.html or foo/bar.html, that
        means without the theme folder)."""
        return

    @abc.abstractproperty
    def environment(self):
        """The used environment (derieved from :class:`AbstractEnvironment`)."""
        return


    @abc.abstractmethod
    def render(self, **dikt):
        """Render template with :param dikt:"""
        return
