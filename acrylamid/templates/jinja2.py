# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from __future__ import absolute_import

from io import StringIO
from os.path import getmtime
from collections import defaultdict

from jinja2 import Environment as J2Environemnt, FileSystemBytecodeCache
from jinja2 import FileSystemLoader, meta, nodes

from acrylamid.templates import AbstractEnvironment, AbstractTemplate

try:
    from acrylamid.assets.web import Mixin
except ImportError:
    from acrylamid.assets.fallback import Mixin


def unast(node):

    if isinstance(node, nodes.Const):
        return node.value
    elif isinstance(node, nodes.List):
        return [unast(item) for item in node.items]
    raise NotImplementedError(node)


def find_assets(ast):
    """Finds the {% for url in compile("foo.scss") %} syntax and yields
    the *args and **kwargs for Bundle(*args, **kwargs)."""

    for node in ast.find_all((nodes.Call, )):
        if isinstance(node.node, nodes.Name) and node.node.name == 'compile':
            yield [x.value for x in node.args], \
                dict((x.key, unast(x.value)) for x in node.kwargs)


class ExtendedFileSystemLoader(FileSystemLoader):

    def __init__(self, layoutdirs):
        # remember already resolved templates -> modified state
        # TODO don't assume macros.html never changes
        self.modified = {'macros.html': False}

        # requested template -> parents as flat list
        self.resolved = defaultdict(set)

        # assets in the form of theme/base.html -> (*args, **kwargs)
        self.assets = defaultdict(list)

        super(ExtendedFileSystemLoader, self).__init__(layoutdirs)

    def load(self, environment, name, globals=None):

        bcc = environment.bytecode_cache

        if globals is None:
            globals = {}

        deps = [name, ]
        while len(deps) > 0:

            child = deps.pop()
            if child in self.modified:
                continue

            source, filename, uptodate = self.get_source(environment, child)
            bucket = bcc.get_bucket(environment, child, filename, source)

            try:
                modified = getmtime(filename) > getmtime(bcc._get_cache_filename(bucket))
            except OSError:
                modified = True

            self.modified[child] = modified

            if modified:
                # updating cached template if timestamp has changed
                code = environment.compile(source, child, filename)
                bucket.code = code
                bcc.set_bucket(bucket)

            ast = environment.parse(source)
            for parent in meta.find_referenced_templates(ast):
                self.resolved[child].add(parent)
                deps.append(parent)

            for args, kwargs in find_assets(ast):
                self.assets[name].append((args, kwargs))

        source, filename, uptodate = self.get_source(environment, name)
        code = bcc.get_bucket(environment, name, filename, source).code

        if code is None:
            code = environment.compile(source, name, filename)

        tt = environment.template_class.from_code(environment, code,
                                                      globals, uptodate)
        return tt


class Environment(AbstractEnvironment):

    extension = ['.html', '.j2']
    loader = None

    def __init__(self, layoutdir, cachedir):

        self.templates = {}
        self.loader = ExtendedFileSystemLoader(layoutdir)

        self._jinja2 = J2Environemnt(
            loader=self.loader, bytecode_cache=FileSystemBytecodeCache(cachedir))

        # jinja2 is stupid and can't import any module during runtime
        import time, datetime, urllib

        for module in (time, datetime, urllib):
            self._jinja2.globals[module.__name__] = module

            for name in dir(module):
                if name.startswith('_'):
                    continue
                obj = getattr(module, name)
                if hasattr(obj, '__class__') and callable(obj):
                    self._jinja2.filters[module.__name__ + '.' + name] = obj

    def register(self, name, func):
        self._jinja2.globals[name] = func
        self._jinja2.filters[name] = func

    def fromfile(self, env, path):
        return self.templates.setdefault(path,
            Template(env, path, self._jinja2.get_template(path)))

    def extend(self, path):
        self.loader.searchpath.append(path)


class Template(AbstractTemplate, Mixin):

    def render(self, **kw):
        buf = StringIO()
        self.template.stream(**kw).dump(buf)
        return buf
