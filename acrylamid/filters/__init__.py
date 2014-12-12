# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import os
import sys
import traceback

from os.path import join, dirname, basename

from acrylamid import log, helpers, compat
from acrylamid.errors import AcrylamidException
from acrylamid.compat import string_types, filter
from acrylamid.lib.lazy import _demandmod as LazyModule

# module-level variable to store all used filters during compilation
__filter_list = None


def get_filters():

    global __filter_list
    return __filter_list


def index_filters(module):
    """Goes through the modules' contents and indexes all classes derieved
    from Filter and have a `match` attribute.

    :param module: the module to index
    :param conf: user config
    :param env: environment
    """

    global __filter_list

    cs = [getattr(module, c) for c in dir(module) if not c.startswith('_')]
    for mem in cs:
        if isinstance(mem, LazyModule):
            continue  # weird things happen when instance-checking with meta
        if isinstance(mem, meta) and hasattr(mem, 'match'):
            __filter_list.append(mem)


def discover(directories, filterfunc=lambda filename: True):
    """Discover and yield python modules (aka files that endswith .py) if
    `filterfunc` returns True for that filename."""

    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for fname in files:
                if fname.endswith('.py') and filterfunc(fname):
                    yield join(root, fname)


def initialize(directories, conf, env):
    """Import and initialize filters butskip modules that start with an
    underscore, md_x or rstx_ as they have special meaning to Acrylamid.

    :param directories: list of directories
    :param conf: user config
    :param env: environment"""

    global __filter_list
    __filter_list = FilterList()

    directories += [dirname(__file__)]
    helpers.discover(
        directories, index_filters,
        lambda path: not basename(path).startswith(('_', 'mdx_', 'rstx_'))
    )


class RegexList(list):

    def __contains__(self, other):
        for value in self:
            if isinstance(value, string_types):
                if value == other:
                    return True
            else:
                if value.match(other):
                    return True
        else:
            return False


class meta(type):
    """Python metaclass magic to provide an easy filter API.  You can write complex
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
                        log.warn(e.args[0])
                        setattr(cls, 'transform', lambda cls, x, y, *z: x)
                        self.initialized = True
                        return lambda cls, x, y, *z: x
                    traceback.print_exc(file=sys.stdout)
                    raise AcrylamidException('ImportError: %s' % e.args[0])
            return func

        init = dct.get('init', lambda s, x, y: None)
        transform = lambda cls, x, y, *z: initialize(
            cls, dct.get('transform', bases[0].transform))(cls, x, y, *z)

        super(meta, cls).__init__(name, bases, dct)
        setattr(cls, 'init', init)
        setattr(cls, 'transform', transform)

        if 'match' in dct:
            setattr(cls, 'match', RegexList(dct['match']))


class Filter(compat.metaclass(meta, object)):
    """All text transformation is done via filters. A filter takes some text and
    returns it modified or untouched. Per default custom filters are stored in
    ``filters/`` directory inside your blog. On startup, Acrylamid will parse this
    plugin, report accidential syntax errors and uses this filter if required.

    .. code-block:: python

        from acrylamid.filters import Filter

        class Example(Filter):

            match = ['keyword', 'another']

            def transform(self, content, entry, *args):
                return content

    This is a minimal filter implementation that does nothing but returning
    the content that you can apply with ``filter: keyword``. A Filter may
    provide an :func:`init` that gets called once before we apply
    :func:`transform` to the content.

    .. attribute:: version

       Current version of this filter. If you made fundamental changes to your
       filter you can increment the version and all cached entries using that
       filter will recompile automatically on next run.

    .. attribute:: priority

       A filter chain is sorted by priority, so if you do textual modification
       you should have a priority ≥ 70.0 (default for Markdown, reST and so
       on).

    .. attribute:: match

       A list of strings or regular expressions (mixed works too) that will
       match this filter and uses this in the rendering process.

    .. attribute:: conflicts

       A list of strings (no regular expressions!) that describe conflicting
       :doc:`filters`. For example conflicts Markdown with ``['rst', 'plain',
       'textile']``. It is sufficient that one filter provides conflicting
       filters.

    .. attribute:: uses

       Override this property to include configuration and/or environment
       parameters. They are used to determine whether a cache object is still
       valid or not.

       You don't have to include configuration variables within the namespace
       of the filter yourself, as ``conf.fetch(self.cname)`` is automatically
       included into the filter hash.

    .. method:: init(self, conf, env)

       At demand initialization. A filter gets only initialized when he's
       actually used. This part is executed only once before :func:`transform`
       and should be used to import plugins or set some constants. Note that you
       may also check explicitly for ImportErrors from a statement like ``import
       foo`` that will not throw an :class:`ImportError` because we delay the
       actual import. Just make write ``foo.bar`` in :func:`init` and when it
       throws an ImportError, it is automatically handled.

       Have a look at ``acrylamid/filters/md.py`` or ``acrylamid/filters/typography.py``
       for example implementations.

       :param conf: :doc:`conf.py` dictionary
       :param env: environment dictionary

    .. method:: transform(self, content, entry, *args)

       Modify the content and return it. Each continuous transformation is
       automatically saved to disk (= caching). Don't import modules here,
       use module space or :func:`init` for that.

       :param content: a text you can modify
       :param entry: current :class:`readers.Entry`
       :param args: a list of additional arguments
    """

    initialized = False
    conflicts = []
    priority = 50.0
    version = 1

    def __init__(self, conf, env, fname, *args):

        self.conf = conf
        self.env = env

        self.cname = self.__class__.__name__.lower()  # common name
        self.name = fname
        self.args = args

        # precalculate __hash__ because we need it quite often in tree
        self.hv = helpers.hash(
            self.cname, tuple(self.args), self.version, self.priority,
            helpers.hash(self.uses), helpers.hash(self.conf.fetch(self.cname + '_')))

    def __repr__(self):
        return "<%s@%s %2.f:%s>" % (self.cname, self.version, self.priority, self.name)

    def __hash__(self):
        return self.hv

    def __eq__(self, other):
        return True if hash(other) == hash(self) else False

    @property
    def uses(self):
        return ''


def disable(fx):
    """Disable :class:`Filter` safely."""

    newfx = type(str(fx.__class__.__name__), (Filter, ), {
        '__hash__': lambda cls: hash(fx.name),
        'match': [fx.__class__.__name__],
        'conflicts': fx.conflicts,
        'transform': lambda cls, x, y, *z: x
    })

    return newfx(fx.conf, fx.env, fx.name)


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
            if [k for k in self if x in k.match]:
                return True

        # check if any filter in list conflicts with y
        for x in self:
            if [k for k in x.conflicts if k in y.match]:
                return True
        return False

    def __getitem__(self, item):

        try:
            f = next(filter(lambda x: item in x.match, self))
        except StopIteration:
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

        raise NotImplementedError('XXX get context with some magic')

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
