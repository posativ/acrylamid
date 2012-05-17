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
from acrylamid.errors import AcrylamidException


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
    """Python metaclass magic to provide a easy filter API.  You can write complex
    calculations into your initialization, but it is only called when this filter
    is actually needed and then also only once.

    This is done via decorators around :func:`Filter.transform` and is hidden from
    the developer.

    Here we also wrap ``Filter.match`` into :class:`RegexList`."""

    def __init__(cls, name, bases, dct):

        def initialize(self, func):

            if not self.initialized:
                try:
                    self.init(self.conf, self.env)
                    self.initialized = True
                except ImportError as e:
                    if self.env.options.ignore:
                        log.warn(str(e))
                        setattr(cls, 'transform', lambda cls, x, y, *z: x)
                        self.initialized = True
                        return lambda cls, x, y, *z: x
                    raise AcrylamidException('%s: %s' % (self.__class__.__name__, str(e)))
            return func

        init = dct.get('init', lambda s, x, y: None)
        transform = lambda cls, x, y, *z: initialize(cls, dct['transform'])(cls, x, y, *z)

        super(meta, cls).__init__(name, bases, dct)
        setattr(cls, 'init', init)
        setattr(cls, 'transform', transform)

        if 'match' in dct:
            setattr(cls, 'match', RegexList(dct['match']))


class Filter(object):

    __metaclass__ = meta

    initialized = False
    version = "1.0.0"
    priority = 50.0
    conflicts = []

    def __init__(self, conf, env, fname, *args):

        self.conf = conf
        self.env = env

        self.name = fname
        self.args = args

        # precalculate __hash__ because we need it quite often in tree
        h = hash(fname + repr(args))
        setattr(self, '__hash__', lambda : h)

    def __repr__(self):
        return "<%s@%s %2.f:%s>" % (self.__class__.__name__, self.version,
                                    self.priority, self.name)

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


class Node(dict):
    """This is a root, an edge and a leaf. Stores predecessor and
    count of views using this leaf."""

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.refs = 1
        self.prev = None


class FilterTree(list):
    """Store all applied filters of an entry in a tree structure to find
    common paths where we can share computed intermediates."""

    def __init__(self, *args, **kwargs):

        # its a list after all ;-)
        super(FilterTree, self).__init__(*args, **kwargs)

        self.root = Node()
        self.views = {None: self}
        self.paths = {None: []}

    def __iter__(self):
        """Iterating over list of filters of given context."""

        raise NotImplemented('XXX get context with some magic')

    def add(self, lst, context):
        """This adds a list of filters and stores the context and the
        reference to that path in self.views."""

        node = self.root
        for key in lst:
            if key not in node:
                node[key] = Node()
                node[key].prev = node
                node = node[key]
            else:
                node = node[key]
                node.refs += 1

        self.views[context] = node
        self.paths[context] = lst

    def path(self, context):
        """Return the actual 'path' a view would use."""

        return self.paths[context]

    def iter(self, context):
        """This returns a generator which yields a tuple containing the zero-index
        and the filter list itself using a given context."""

        path, node = self.path(context)[:], self.root
        n = self.root[path[0]].refs

        while True:

            ls = []
            for key in path[:]:
                if node[key].refs != n:
                    n = node[key].refs
                    break

                ls.append(key)
                node = node[key]
                path.pop(0)

            if not ls:
                raise StopIteration

            yield ls


callbacks = FilterList()
