# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import os

from os.path import join, isdir, dirname, getmtime, relpath
from itertools import chain

from acrylamid import core
from acrylamid.compat import map

from acrylamid.utils import cached_property
from acrylamid.helpers import event

from webassets.env import Environment, Resolver
from webassets.merge import FileHunk
from webassets.bundle import Bundle, has_placeholder
from webassets.updater import TimestampUpdater
from webassets.version import HashVersion


class Acrylresolver(Resolver):

    def __init__(self, conf, environment):
        super(Acrylresolver, self).__init__(environment)
        self.conf = conf

    def resolve_output_to_path(self, target, bundle):

        if not target.startswith(self.conf.output_dir):
            target = join(self.conf.output_dir, target)

        if not isdir(dirname(target)):
            os.makedirs(dirname(target))

        return target


class Acrylupdater(TimestampUpdater):
    """Keep incremental compilation even with ``depends``, which is currently
    not provided by webassets: https://github.com/miracle2k/webassets/pull/220.
    """
    id = 'acrylic'
    used, new = set(), set()

    def build_done(self, bundle, env):
        func = event.create if bundle in self.new else event.update
        func('webassets', bundle.resolve_output(env))
        return super(Acrylupdater, self).build_done(bundle, env)

    def needs_rebuild(self, bundle, env):

        if super(TimestampUpdater, self).needs_rebuild(bundle, env):
            return True

        try:
            dest = getmtime(bundle.resolve_output(env))
        except OSError:
            return self.new.add(bundle) or True

        src = [s[1] for s in bundle.resolve_contents(env)]
        deps = bundle.resolve_depends(env)

        for item in src + deps:
            self.used.add(item)

        if any(getmtime(deps) > dest for deps in src + deps):
            return True

        event.skip('assets', bundle.resolve_output(env))

        return False


class Acrylversion(HashVersion):
    """Hash based on the input (+ depends), not on the output."""

    id = 'acrylic'

    def determine_version(self, bundle, env, hunk=None):

        if not hunk and not has_placeholder(bundle.output):
            hunks = [FileHunk(bundle.resolve_output(env)), ]
        elif not hunk:
            src = sum(map(env.resolver.resolve_source, bundle.contents), [])
            hunks = [FileHunk(hunk) for hunk in src + bundle.resolve_depends(env)]
        else:
            hunks = [hunk, ]

        hasher = self.hasher()
        for hunk in hunks:
            hasher.update(hunk.data())
        return hasher.hexdigest()[:self.length]


class Webassets(object):

    def __init__(self, conf, env):
        self.conf = conf
        self.env = env

        self.environment = Environment(
            directory=conf.theme[0], url=env.path,
            updater='acrylic', versions='acrylic',
            cache=core.cache.cache_dir, load_path=[conf.theme[0]])

        # fix output directory creation
        self.environment.resolver = Acrylresolver(conf, self.environment)

    def excludes(self, directory):
        """Return used assets relative to :param:`directory`."""
        return [relpath(p, directory) for p in self.environment.updater.used]

    def compile(self, *args, **kw):

        assert 'output' in kw
        kw.setdefault('debug', False)

        bundle = Bundle(*args, **kw)
        for url in bundle.urls(env=self.environment):
            yield url


class Mixin:

    @cached_property
    def modified(self):
        """Iterate template dependencies for modification and check web assets
        if a bundle needs to be rebuilt."""

        for item in chain([self.path], self.loader.resolved[self.path]):
            if self.loader.modified[item]:
                return True

        for args, kwargs in self.loader.assets[self.path]:
            kwargs.setdefault('debug', False)
            bundle = Bundle(*args, **kwargs)
            rv = self.environment.webassets.environment.updater.needs_rebuild(
                bundle, self.environment.webassets.environment)
            if rv:
                return True

        return False
