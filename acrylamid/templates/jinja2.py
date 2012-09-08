# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from __future__ import absolute_import

from io import StringIO
from os.path import exists, getmtime

from jinja2 import Environment as J2Environemnt, FileSystemBytecodeCache
from jinja2 import FileSystemLoader, meta

from acrylamid.templates import AbstractEnvironment, AbstractTemplate


class ExtendedFileSystemLoader(FileSystemLoader):
    """A custom :class:`jinja2.FileSystemLoader` to work with Acrylamid's
    caching requirements. Jinja2 does track template changes using the
    modification timestamp of the compiled but we need template dependencies
    as well as consistent has_changed values over the whole compilation
    process."""

    # remember already resolved templates
    resolved = {}

    # used templates
    used = set()

    def load(self, environment, name, globals=None):
        """patched `load` to add a has_changed attribute providing information
        whether the template or its parents have changed."""

        def resolve(parent):
            """We check whether any dependency (extend-block) has changed and
            update the bucket -- recursively. Returns True if the template
            itself or any parent template has changed. Otherwise False."""

            self.used.add(parent)

            if parent in self.resolved:
                return self.resolved[parent]

            source, filename, uptodate = self.get_source(environment, parent)
            bucket = bcc.get_bucket(environment, parent, filename, source)
            p = bcc._get_cache_filename(bucket)
            has_changed = getmtime(filename) > getmtime(p) if exists(p) else True

            if has_changed:
                # updating cached template if timestamp has changed
                code = environment.compile(source, parent, filename)
                bucket.code = code
                bcc.set_bucket(bucket)

                self.resolved[parent] = True
                return True

            ast = environment.parse(source)
            for name in meta.find_referenced_templates(ast):
                rv = resolve(name)
                if rv:
                    # XXX double-return to break this recursion?
                    return True

        if globals is None:
            globals = {}

        source, filename, uptodate = self.get_source(environment, name)

        bcc = environment.bytecode_cache
        bucket = bcc.get_bucket(environment, name, filename, source)
        has_changed = bool(resolve(name))

        code = bucket.code
        if code is None:
            code = environment.compile(source, name, filename)

        tt = environment.template_class.from_code(environment, code,
                                                  globals, uptodate)
        tt.has_changed = has_changed
        return tt


class Environment(AbstractEnvironment):

    def init(self, layoutdir, cachedir):
        self.jinja2 = J2Environemnt(loader=ExtendedFileSystemLoader(layoutdir),
                                    bytecode_cache=FileSystemBytecodeCache(cachedir))

        # jinja2 is stupid and can't import any module during runtime
        import time, datetime, urllib

        for module in (time, datetime, urllib):
            self.jinja2.globals[module.__name__] = module

            for name in dir(module):
                if name.startswith('_'):
                    continue
                if callable(getattr(module, name)):
                    self.jinja2.filters[module.__name__ + '.' + name] = getattr(module, name)

    def register(self, name, func):
        self.jinja2.filters[name] = func

    def fromfile(self, path):
        return Template(self.jinja2.get_template(path))

    @property
    def templates(self):
        return self.jinja2.loader.used


class Template(AbstractTemplate):

    def __init__(self, template):
        self.template = template

    def render(self, **kw):
        buf = StringIO()
        self.template.stream(**kw).dump(buf)
        return buf

    @property
    def has_changed(self):
        return self.template.has_changed
