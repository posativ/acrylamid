# -*- encoding: utf-8 -*-
#
# Copyright 2014 Christian Koepp <ckoepp@gmail.com>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from acrylamid import log
from acrylamid.filters import Filter

class Replace(Filter):
    match = ['replace']
    version = 1
    priority = 0.0

    def init(self, conf, env, *args):
        try:
            self._db = conf.replace_rules
        except AttributeError:
            log.warn('No configuration named REPLACE_RULES found. Replace filter has nothing to do.')
            self._db = dict()

    def transform(self, content, entry, *args):
        if len(self._db) == 0:
            return content

        for k,v in self._db.items():
            content = content.replace(k, v)
        return content