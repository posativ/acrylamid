# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from itertools import chain
from acrylamid.utils import cached_property

Bundle = lambda *args, **kwargs: None


class Webassets(object):

    def __init__(self, conf, env):
        pass

    def excludes(self, directory):
        return []

    def compile(self, *args, **kwargs):
        return ""


class Mixin(object):

    @cached_property
    def modified(self):
        """Iterate template dependencies for modification."""

        for item in chain([self.path], self.loader.resolved[self.path]):
            if self.loader.modified[item]:
                return True

        return False
