# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import os
import glob
import traceback

from acrylamid import log
from acrylamid.errors import AcrylamidException

# module-wide callbacks variable contaning views, reset this on initialize!
__views_list = []


def get_views():

    global __views_list
    __views_list = sorted(__views_list, key=lambda v: v.__class__.__name__)
    return sorted(__views_list, key=lambda v: v.priority, reverse=True)


def index_views(module, urlmap, conf, env):
    """Stupid an naïve try getting attribute specified in `views` in
    various flavours and fail silent.

    We remove already mapped urls and pop views' name from kwargs to
    avoid the practical worst-case O(m*n), m=num rules, n=num modules.

    Views are stored into module-global variable `callbacks` and can be
    retrieved using :func:`views.get_views`.
    """

    global __views_list

    # Gather the available views in the module
    view_list = []
    view_map = {}
    for name in dir(module):
        cls = getattr(module, name)
        try:
            mro = cls.mro()
        except AttributeError:
            continue
        if View in mro:
            view_list.append(name)
            view_map[name.lower()] = name

    for view, rule in urlmap[:]:
        mem = None
        # First try to match the view name case sensitive...
        if view in view_list:
            mem = getattr(module, view)
        # ...then try again, but now ignore case.
        else:
            view_class = view_map.get(view.lower(), None)
            if view_class:
                mem = getattr(module, view_class)

        if mem:
            kwargs = conf['views'][rule].copy()
            kwargs['path'] = rule
            try:
                kwargs['condition'] = conf['views'][rule]['if']
            except KeyError:
                pass
            kwargs.pop('if', None)

            m = mem(conf, env, **kwargs)
            m.init(**m._getkwargs())

            __views_list.append(m)
            urlmap.remove((view, rule))


def initialize(ext_dir, conf, env):

    global __views_list
    __views_list = []

    # view -> path
    urlmap = [(conf['views'][k]['view'], k) for k in conf['views']]

    ext_dir.extend([os.path.dirname(__file__)])
    ext_list = []

    # handle ext_dir
    for mem in ext_dir[:]:
        if os.path.isdir(mem):
            sys.path.insert(0, mem)
        else:
            ext_dir.remove(mem)
            log.error("View directory %r does not exist. -- skipping" % mem)

    for mem in ext_dir:
        files = glob.glob(os.path.join(mem, "*.py"))
        files += [p.rstrip('/__init__.py') for p in \
                    glob.glob(os.path.join(mem, '*/__init__.py'))]
        ext_list += files

    for mem in [os.path.basename(x).replace('.py', '') for x in ext_list]:
        if mem.startswith('_'):
            continue
        try:
            _module = __import__(mem)
            #sys.modules[__package__].__dict__[mem] = _module
            index_views(_module, urlmap, conf, env)
        except (ImportError, Exception) as e:
            log.error('%r ImportError %r', mem, e)
            traceback.print_exc(file=sys.stdout)


class Views(list):
    """A compatibility layer for the view storage. It is actually a list
    but supports ``__getitem__`` for retrieval."""

    def __getitem__(self, key):
        if isinstance(key, (basestring, View)):
            try:
                return self[self.index(key)]
            except ValueError:
                raise IndexError(key)
        return list.__getitem__(self, key)


class View(object):
    """A view generally takes a template and generates HTML/XML or other
    kinds of text. It may filter a list of entries by a given attribute,
    apply per view specific filters, handle path routes.

    .. code-block:: python

        from acrylamid.views import View

        class Raw(View):

            def init(self, **kw):
                pass

            def context(self, env, request):
                return env

            def generate(self, request):
                yield 'Hello World', '/output/hello.txt'

    Above implements a minimal view that outputs text to a given path to
    :func:`acrylamid.helpers.mkfile` that handles directory creation and
    event handling. Note, that a view must implement a *skip*-mechanism
    by itself. If you :func:`acrylamid.helpers.paginate` you get a
    ``has_changed`` for the current list of entries and you only need
    to check wether the template has changed::

        from os.path import join

        if exists(path) and not has_changed and not tt.has_changed:
            event.skip(path)
            continue

    See the source of acrylamid's built-in views that all have implemented
    skipping. If you skip over entries you can take full advantage of lazy
    evaluation (no need to initialize filters, recompile/load from cache).

    A valid view only requires a :func:`generate` method.

    .. attribute:: conf

       Acrylamid configuration.

    .. attribute:: env

       Acrylamid environment.

    .. attribute:: priority

       From 0.0 to 100.0, by default 50.0. Useful if you want to run a view
       at first or at last.

    .. attribute:: filters

       A list of filters you applied to this view in your :doc:`conf.py`,
       default list is empty.

    .. attribute:: condition

       A filtering condition from :doc:`conf.py` that gets always applied,
       defaults to no filtering.

    .. attribute:: path

       The key to which you assign a configuration dict.

    .. method:: init(self, **kwargs)

       Initializing the view with configuration parameters. You can also load
       jinja/other templates here.

       :param kw: custom key/value pair from :doc:`conf.py` is available in here.

    .. method:: context(self, env, request)

       Add shared environment varialbes for all views, e.g. template filters and
       objects. You must return the environment.

       :param env: environment object
       :param request: reqest dictionary

    .. method:: generate(self, request)

       Render template and yield final output with full qualified path. If you don't
       generate output, raise :class:`StopIteration`. Make use of :mod:`acrylamid.helpers`
       especially :func:`acrylamid.helpers.expand`, :func:`acrylamid.helpers.joinurl`
       and :func:`acrylamid.helpers.union`.

       Load a template from ``env.engine`` and check wether it has changed::

           >>> tt = self.env.engine.fromfile('articles.html')
           >>> print tt.has_changed
           True

       If you skip over an entry make sure you :func:`acrylamid.helpers.event.skip` it,
       so Acrylamid can track this file to include it into your sitemap or won't wipe
       it during clean up.

       :param request: request dictionary"""

    priority = 50.0

    def __init__(self, conf, env, **kwargs):

        self.condition = kwargs.get('condition', lambda e: True)
        self.name = kwargs.get('view', 'View')
        self.path = kwargs.get('path', '/')
        self.filters = kwargs.get('filters', [])

        # single string --> [string, ]
        if isinstance(self.filters, basestring):
            self.filters = [self.filters, ]

        self.conf = conf
        self.env = env

        for k in ('condition', 'view', 'path', 'filters'):
            kwargs.pop(k, None)

        self._getkwargs = lambda : kwargs

    def __eq__(self, other):
        if isinstance(other, View):
            return hash(self) == hash(other)
        return self.name == other

    def init(self, **kwargs):
        pass

    def context(self, env, request):
        return env

    def generate(self, request):
        raise AcrylamidException('%s.generate not implemented' % self.__class__.__name__)
