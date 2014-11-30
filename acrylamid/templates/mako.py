# -*- encoding: utf-8 -*-
#
# Copyright 2012 Moritz Schlarb <mail@moritz-schlarb.de>. All rights reserved.
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from __future__ import absolute_import

import os
import io
import re
import ast
import posixpath

from os.path import getmtime, isfile
from itertools import chain
from collections import defaultdict

from acrylamid.templates import AbstractEnvironment, AbstractTemplate
from mako.lookup import TemplateLookup
from mako import exceptions, runtime

try:
    from acrylamid.assets.web import Mixin
except ImportError:
    from acrylamid.assets.fallback import Mixin


class CallVisitor(ast.NodeVisitor):

    def __init__(self, callback):
        self.callback = callback
        super(CallVisitor, self).__init__()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.callback(node)


def unast(node):
    if isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.List):
        return [unast(item) for item in node.elts]
    raise NotImplementedError(node)


def find_assets(tt):
    """
    Parse AST from Mako template and yield *args, **kwargs from any
    `compile` call.
    """
    rv = []

    def collect(node):
        if node.func.id != "compile":
            return

        args = list(unast(x) for x in node.args)
        kwargs = dict((x.arg, unast(x.value)) for x in node.keywords)

        rv.append((args, kwargs))

    CallVisitor(collect).visit(ast.parse(tt.code))

    for args, kwargs in rv:
        yield args, kwargs


class ExtendedLookup(TemplateLookup):
    """
    Custom Mako template lookup that records dependencies, mtime and referenced
    web assets.
    """

    inherits = re.compile(r'<%inherit file="([^"]+)" />')
    includes = re.compile(r'<%namespace file="([^"]+)" import="[^"]+" />')

    def __init__(self, *args, **kwargs):
        # remember already resolved templates -> modified state
        # TODO don't assume macros.html never changes
        self.modified = {'macros.html': False}

        # requested template -> parents as flat list
        self.resolved = defaultdict(set)

        # assets in the form of theme/base.html -> (*args, **kwargs)
        self.assets = defaultdict(list)
        
        super(ExtendedLookup, self).__init__(*args, **kwargs)

    def get_template(self, uri):
        """This is stolen and truncated from mako.lookup:TemplateLookup."""

        u = re.sub(r'^/+', '', uri)
        for dir in self.directories:
            filename = posixpath.normpath(posixpath.join(dir, u))
            if os.path.isfile(filename):
                return self._load(filename, uri)
        else:
            raise exceptions.TopLevelLookupException(
                                "Cant locate template for uri %r" % uri)

    def _load(self, filename, uri):

        deps = [uri, ]
        while len(deps) > 0:

            child = deps.pop()
            if child in self.modified:
                continue

            for directory in self.directories:
                filename = posixpath.normpath(posixpath.join(directory, child))
                if isfile(filename):
                    break

            p = self.modulename_callable(filename, child)

            try:
                modified = getmtime(filename) > getmtime(p)
            except OSError:
                modified = True

            self.modified[child] = modified

            with io.open(filename, encoding='utf-8') as fp:
                source = fp.read()

            parents = chain(self.inherits.finditer(source), self.includes.finditer(source))
            for match in parents:
                self.resolved[child].add(match.group(1))
                deps.append(match.group(1))

            # TODO: definitely an ugly way (= side effect) to get the byte code
            tt = super(ExtendedLookup, self)._load(filename, child)
            for args, kwargs in find_assets(tt):
                self.assets[uri].append((args, kwargs))

        # already cached due side effect above
        return self._collection[uri]


class Environment(AbstractEnvironment):

    extension = ['.html', '.mako']

    def __init__(self, layoutdirs, cachedir):
        self._mako = ExtendedLookup(
            directories=layoutdirs,
            module_directory=cachedir,
            # similar to mako.template.Template.__init__ but with
            # leading cache_ for the acrylamid cache
            modulename_callable=lambda filename, uri:\
                os.path.join(os.path.abspath(cachedir), 'cache_' +
                    os.path.normpath(uri.lstrip('/')) + '.py'),
            input_encoding='utf-8')

        self.filters = {}

    def register(self, name, func):
        self.filters[name] = func

    def fromfile(self, env, path):
        return Template(env, path, self._mako.get_template(path))

    def extend(self, path):
        self._mako.directories.append(path)

    @property
    def loader(self):
        return self._mako


class Template(AbstractTemplate, Mixin):

    def render(self, **kw):
        # we inject the filter functions as top-level objects into the template,
        # that's probably the only way that works with Mako
        kw.update(self.engine.filters)
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
