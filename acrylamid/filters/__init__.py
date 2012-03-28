#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import sys
import os
import glob
import fnmatch
import copy

from acrylamid import log
from acrylamid.errors import AcrylamidException


def get_filters():

    global callbacks
    return callbacks


def index_filters(module, conf, env):
    """Goes through the modules' contents and indexes all the funtions/classes
    having a __call__ and __match__ attribute.

    :param module: the module to index
    :param conf: user config
    :param env: environment
    """

    global callbacks

    cs = [getattr(module, c) for c in dir(module) if not c.startswith('_')]
    for mem in cs:
        if hasattr(mem, '__match__'):
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


class meta(type):
    def __init__(cls, name, bases, dct):
        super(meta, cls).__init__(name, bases, dct)
        setattr(cls, 'init', classmethod(dct.get('init', lambda s, x, y: None)))


class Filter:

    __metaclass__ = meta
    __priority__ = 50.0
    __conflicts__ = []

    def __init__(self, fname, *args):

        self.name = fname
        self.args = args

    def __repr__(self):
        return "<%s [%2.f] ~%s>" % (self.__class__.__name__,
                                    self.__priority__, self.name)

    def __hash__(self):
        return hash(self.name + repr(self.args))

    def __eq__(self, other):
        return True if hash(other) == hash(self) else False

    def init(self, conf, env):
        pass

    def transform(self, text, request, *args):
        raise NotImplemented


class FilterList(list):
    """a list containing tuples of (filtername, filterfunc, arguments).

    >>> x = FilterList()
    >>> x.append(MyFilter)
    >>> f = x[MyFilter]
    """

    def __contains__(self, y):
        """first checks, wether the item itself is in the list. Next, all Filters
        providing __conflicts__ are checked wether y conflicts with a filter.
        Otherwise y is not in FilterList.
        """
        for x in self:
            if x.__name__ == y.__name__:
                return True
        for f in y.__conflicts__:
            for x in self:
                if f in x.__match__:
                    return True
        return False

    def __getitem__(self, item):

        try:
            f = filter(lambda x: item in x.__match__, self)[0]
        except IndexError:
            raise ValueError('%s is not in list' % item)

        return f


class FilterStorage(dict):
    """store multiple keys per value and make __call__ do nothing, when
    filter is prefixed by *no*."""

    def __init__(self, *args):
        dict.__init__(self, args)
        self.map = {}

    def __contains__(self, key):
        return True if key in self.map else False

    def __setitem__(self, key, value):

        if isinstance(key, basestring):
            self.map[key] = key
            dict.__setitem__(self, key, value)
        else:
            for k in key:
                self.map[k] = key[0]
            dict.__setitem__(self, key[0], value)

    def __getitem__(self, key):

        q = key[2:] if key.startswith('no') else key
        try:
            f = dict.__getitem__(self, self.map[q])
        except KeyError:
            raise AcrylamidException('no such filter: %s' % key)
        if key.startswith('no'):
            f = copy.copy(f)
            f.__call__ = lambda x, y, *z: x
        return f

callbacks = FilterList() # FilterStorage()
