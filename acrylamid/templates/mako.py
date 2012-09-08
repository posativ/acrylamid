# -*- encoding: utf-8 -*-
#
# Copyright 2012 moschlar <mail@moritz-schlarb.de>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from __future__ import absolute_import

import os
import io
import re
import posixpath

from os.path import getmtime, isfile, basename

from acrylamid.templates import AbstractEnvironment, AbstractTemplate
from mako.lookup import TemplateLookup
from mako import exceptions, runtime


class ExtendedLookup(TemplateLookup):

    inherits = re.compile(r'\<%inherit file="([^"]+)" /\>')
    includes = re.compile(r'\<%namespace file="([^"]+)" import="[^"]+" /\>')

    # remember already resolved templates
    resolved = {}

    # used templates
    used = set()

    def get_template(self, uri):
        """This is stolen and truncated from mako.lookup:TemplateLookup."""

        u = re.sub(r'^\/+', '', uri)
        for dir in self.directories:
            filename = posixpath.normpath(posixpath.join(dir, u))
            if os.path.isfile(filename):
                return self._load(filename, uri)
        else:
            raise exceptions.TopLevelLookupException(
                                "Cant locate template for uri %r" % uri)

    def _load(self, filename, uri):

        def resolve(uri):
            """Check whether any referenced template has changed -- recursively."""

            self.used.add(uri)

            if uri in self.resolved:
                return self.resolved[uri]

            filename = posixpath.normpath(posixpath.join(self.directories[0], uri))
            p = self.modulename_callable(filename, uri)
            has_changed = getmtime(filename) > getmtime(p) if isfile(p) else True

            if has_changed:
                self.resolved[uri] = True
                return True

            with io.open(filename) as fp:
                source = fp.read()

            for match in self.inherits.finditer(source):
                if resolve(match.group(1)):
                    return True

            for match in self.includes.finditer(source):
                if resolve(match.group(1)):
                    return True

            return False

        try:
            template = self._collection[uri]
        except KeyError:
            template = super(ExtendedLookup, self)._load(filename, uri)

        try:
            template.has_changed = resolve(basename(template.filename))
        except (OSError, IOError):
            raise exceptions.TemplateLookupException(
                                "Can't locate template for uri %r" % uri)
        return template


class Environment(AbstractEnvironment):

    def init(self, layoutdir, cachedir):
        self.mako = ExtendedLookup(
            directories=[layoutdir],
            module_directory=cachedir,
            # similar to mako.template.Template.__init__ but with
            # leading cache_ for the acrylamid cache
            modulename_callable=lambda filename, uri:\
                os.path.join(os.path.abspath(cachedir), 'cache_' +
                    os.path.normpath(uri.lstrip('/')) + '.py'),
            input_encoding='utf-8')
        self.filters = {}
        return

    def register(self, name, func):
        self.filters[name] = func

    def fromfile(self, path):
        return Template(self.mako.get_template(path), self.filters)

    @property
    def templates(self):
        return self.mako.used


class Template(AbstractTemplate):

    def __init__(self, template, filters={}):
        self.template = template
        self.filters = filters

    def render(self, **kw):
        # we inject the filter functions as top-level objects into the template,
        # that's probably the only way that works with Mako
        kw.update(self.filters)
        buf = io.StringIO()
        ctx = runtime.Context(buf, **kw)
        self.template.render_context(ctx)
        return buf
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
        return self.template.has_changed
