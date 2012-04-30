#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import os
import glob
import fnmatch

from acrylamid import log


def get_filters():

    global callbacks
    return callbacks


def index_filters(module, conf, env):
    """Goes through the modules' contents and indexes all classes derieved
    from Filter and have a `match` attribute.

    :param module: the module to index
    :param conf: user config
    :param env: environment
    """

    global callbacks

    cs = [getattr(module, c) for c in dir(module) if not c.startswith('_')]
    for mem in cs:
        if isinstance(mem, meta) and hasattr(mem, 'match'):
            mem.init(conf, env)
            callbacks.append(mem)


def initialize(ext_dir, conf, env, include=[], exclude=[]):
    """Imports and initializes extensions from the directories in the list
    specified by 'ext_dir'.  If no such list exists, the we don't load any
    plugins. 'include' and 'exclude' may contain a list of shell patterns
    used for fnmatch. If empty, this filter is not applied.

    :param ext_dir: list of directories
    :param conf: user config
    :param env: environment
    :param include: a list of filename patterns to include
    :param exclude: a list of filename patterns to exclude
    """

    def get_name(filename):
        """Takes a filename and returns the module name from the filename."""
        return os.path.splitext(os.path.split(filename)[1])[0]

    def get_extension_list(ext_dir, include, exclude):
        """Load all plugins that matches include/exclude pattern in
        given lust of directories.  Arguments as in initializes(**kw)."""

        def pattern(name, incl, excl):
            for i in incl:
                if fnmatch.fnmatch(name, i):
                    return True
            for e in excl:
                if fnmatch.fnmatch(name, e):
                    return False
            if not incl:
                return True
            else:
                return False

        ext_list = []
        for mem in ext_dir:
            files = glob.glob(os.path.join(mem, "*.py"))
            files = [get_name(f) for f in files
                                    if pattern(get_name(f), include, exclude)]
            ext_list += files

        return sorted(ext_list)

    global plugins

    exclude.extend(['mdx_*', 'rstx_*'])
    ext_dir.extend([os.path.dirname(__file__)])

    for mem in ext_dir[:]:
        if os.path.isdir(mem):
            sys.path.insert(0, mem)
        else:
            ext_dir.remove(mem)
            log.error("Filter directory '%s' does not exist. -- skipping" % mem)

    ext_list = get_extension_list(ext_dir, include, exclude)
    for mem in ext_list:
        try:
            _module = __import__(mem)
        except (ImportError, Exception), e:
            log.warn('%r %s: %s', mem, e.__class__.__name__, e)
            continue

        index_filters(_module, conf, env)


class RegexList(list):

    def __contains__(self, other):
        for value in self:
            if isinstance(value, basestring):
                if value == other:
                    return True
            else:
                if value.match(other):
                    return True
        else:
            return False


class meta(type):

    def __init__(cls, name, bases, dct):

        super(meta, cls).__init__(name, bases, dct)
        setattr(cls, 'init', classmethod(dct.get('init', lambda s, x, y: None)))

        if 'match' in dct:
            setattr(cls, 'match', RegexList(dct['match']))


class Filter(object):

    __metaclass__ = meta

    version = "1.0.0"
    priority = 50.0
    conflicts = []

    def __init__(self, fname, *args):

        self.name = fname
        self.args = args

    def __repr__(self):
        return "<%s@%s %2.f:%s>" % (self.__class__.__name__, self.version,
                                    self.priority, self.name)

    def __hash__(self):
        return hash(self.name + repr(self.args))

    def __eq__(self, other):
        return True if hash(other) == hash(self) else False

    def transform(self, text, entry, *args):
        raise NotImplemented


class FilterList(list):
    """a list containing tuples of (filtername, filterfunc, arguments).

    >>> x = FilterList()
    >>> x.append(MyFilter)
    >>> f = x[MyFilter]
    """

    def __contains__(self, y):
        """first checks, wether the item itself is in the list. Next, all Filters
        providing `conflicts` are checked wether y conflicts with a filter.
        Otherwise y is not in FilterList.
        """
        # check wether it's the same filter
        for x in self:
            if x.__class__.__name__ == y.__class__.__name__:
                return True

        # check if y.conflicts matches a filter in list
        for x in y.conflicts:
            if filter(lambda k: x in k.match, self):
                return True

        # check if any filter in list conflicts with y
        for x in self:
            if filter(lambda k: k in y.match, x.conflicts):
                return True
        return False

    def __getitem__(self, item):

        try:
            f = filter(lambda x: item in x.match, self)[0]
        except IndexError:
            raise ValueError('%s is not in list' % item)

        return f


callbacks = FilterList()
