# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.
#
# This module contains helper objects and function for writing third-party code.

import sys
import os
import io
import re
import imp
import shutil
import itertools
import subprocess

from unicodedata import normalize
from collections import defaultdict
from os.path import join, dirname, isdir, isfile, commonprefix, normpath

from acrylamid import log, PY3, __file__ as PATH
from acrylamid.errors import AcrylamidException

from acrylamid.core import cache
from acrylamid.utils import batch, hash, rchop

try:
    import translitcodec
except ImportError:
    translitcodec = None  # NOQA

try:
    from unidecode import unidecode
except ImportError:
    unidecode = None  # NOQA

__all__ = ['memoize', 'union', 'mkfile', 'hash', 'expand', 'joinurl',
           'safeslug', 'paginate', 'safe', 'system', 'event', 'rchop',
           'discover']

_slug_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


def memoize(key, value=None):
    """Persistent memory for small values, set and get in a single function.
    If you set a value, it returns whether the new value is different to the
    previous.

    >>> memoize("Foo", 1)
    False
    >>> memoize("Foo", 1)
    True
    >>> memoize("Foo", 2)
    False
    >>> memoize("Foo")
    2

    :param key: get value saved to key, if key does not exist, return None.
    :param value: set key to value
    """
    return cache.memoize(key, value)


def union(first, *args, **kwargs):
    """Takes a list of dictionaries and performs union of each.  Can take additional
    key=values as parameters to overwrite or add key/value-pairs. No side-effects,"""

    new = first.__class__()
    map(new.update, itertools.chain([first], args, [kwargs]))

    return new


def identical(obj, other, bs=4096):
    """Takes two file-like objects and return whether they are identical or not."""
    s, t = obj.tell(), other.tell()
    while True:
        a, b = obj.read(bs), other.read(bs)
        if not a or not b or a != b:
            break
    obj.seek(s), other.seek(t)
    return a == b


def mkfile(fileobj, path, ctime=0.0, ns=None, force=False, dryrun=False):
    """Creates entry in filesystem. Overwrite only if fileobj differs.

    :param fileobj: rendered html/xml as file-like object
    :param path: path to write to
    :param ctime: time needed to compile
    :param force: force overwrite, even nothing has changed (defaults to `False`)
    :param dryrun: don't write anything."""

    fileobj.seek(0)

    if isinstance(fileobj, io.TextIOBase):
        open = lambda path, mode: io.open(path, mode + 't', encoding='utf-8')
    else:
        open = lambda path, mode: io.open(path, mode + 'b')

    if isfile(path):
        with open(path, 'r') as other:
            if identical(fileobj, other):
                return event.identical(ns, path)
        if not dryrun:
            if hasattr(fileobj, 'name'):
                shutil.copy(fileobj.name, path)
            else:
                with open(path, 'w') as fp:
                    fp.write(fileobj.read())
        event.update(ns, path, ctime)
    else:
        if not dryrun and not isdir(dirname(path)):
            os.makedirs(dirname(path))
        if not dryrun:
            if hasattr(fileobj, 'name'):
                shutil.copy(fileobj.name, path)
            else:
                with open(path, 'w') as fp:
                    fp.write(fileobj.read())
        event.create(ns, path, ctime)


def expand(url, obj, re=re.compile(r':(\w+)')):
    """Substitutes/expands URL parameters beginning with a colon.

    :param url: a URL with zero or more :key words
    :param obj: a dictionary where we get key from

    >>> expand('/:year/:slug/', {'year': 2012, 'slug': 'awesome title'})
    '/2011/awesome-title/'
    """
    if isinstance(obj, dict):
        return re.sub(lambda m: unicode(obj.get(m.group(1), m.group(1))), url)
    else:
        return re.sub(lambda m: unicode(getattr(obj, m.group(1), m.group(1))), url)


def joinurl(*args):
    """Joins multiple urls pieces to one single URL without loosing the root
    (first element). If the URL ends with a slash, Acrylamid automatically
    appends ``index.html``.

    >>> joinurl('/hello/', '/world/')
    '/hello/world/index.html'
    """
    rv = [unicode(mem) for mem in args]
    if rv[-1].endswith('/'):
        rv.append('index.html')
    return normpath('/'.join(rv))


def safeslug(slug):
    """Generates an ASCII-only slug.  Borrowed from
    http://flask.pocoo.org/snippets/5/"""

    result = []
    if translitcodec:
        slug = u"" + slug.encode('translit/long')
    if unidecode:
        slug = u"" + unidecode(slug)
    for word in _slug_re.split(slug.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8').strip()
        if word:
            result.append(word)
    return u'-'.join(result)


def paginate(lst, ipp, salt="", orphans=0):
    """paginate(lst, ipp, func=lambda x: x, salt=None, orphans=0)

    Yields a triple ((next, current, previous), list of entries, has
    changed) of a paginated entrylist. It will first filter by the specified
    function, then split the ist into several sublists and check wether the
    list or an entry has changed.

    :param lst: the entrylist containing Entry instances.
    :param ipp: items per page
    :param salt: uses as additional identifier in memoize
    :param orphans: avoid N orphans on last page

    >>> for x, values, _, paginate(entryrange(20), 6, orphans=2):
    ...    print x, values
    (None, 0, 1), [entries 1..6]
    (0, 1, 2), [entries 7..12]
    (1, 2, None), [entries 12..20]"""

    # detect removed or newly added entries
    modified = cache.memoize('paginate-' + salt, hash(*lst))

    # slice into batches
    res = list(batch(lst, ipp))

    if len(res) >= 2 and len(res[-1]) <= orphans:
        res[-2].extend(res[-1])
        res.pop(-1)

    j = len(res)
    for i, entries in enumerate(res):

        i += 1
        next = None if i == 1 else i-1
        curr = i
        prev = None if i >= j else i+1

        yield (next, curr, prev), entries, modified or any(e.modified for e in entries)


def safe(string):
    """Safe string to fit in to the YAML standard (hopefully). Counterpart
    to :func:`acrylamid.readers.unsafe`."""

    if not string:
        return '""'

    if len(string) < 2:
        return string

    for char in ':%#*?{}[]':
        if char in string:
            if '"' in string:
                return '\'' + string + '\''
            else:
                return '\"' + string + '\"'

    for char, repl in ('\'"', '"\''):
        if string.startswith(char) and string.endswith(char):
            return repl + string + repl
    return string


def link(title, href=None):
    """Return a link struct, that contains title and optionally href. If only
    title is given, we use title as href too.  It provides a __unicode__ to
    be compatible with older templates (≤ 0.3.4).

    :param title: link title and href if no href is given
    :param href: href"""

    return type('Link', (object, ), {
        'title': title,
        'href': title if href is None else href,
        '__str__' if PY3 else '__unicode__': lambda cls: cls.href,
        '__add__': lambda self, other: unicode(self) + other,
        '__radd__': lambda self, other: other + unicode(self)
    })()


def system(cmd, stdin=None, **kwargs):
    """A simple front-end to python's horrible Popen-interface which lets you
    run a single shell command (only one, semicolon and && is not supported by
    os.execvp(). Does not catch OSError!

    :param cmd: command to run (a single string or a list of strings).
    :param stdin: optional string to pass to stdin.
    :param kwargs: is passed to :class:`subprocess.Popen`."""

    try:
        if stdin:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE, **kwargs)
            result, err = p.communicate(stdin.encode('utf-8'))
        else:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
            result, err = p.communicate()

    except OSError as e:
        raise OSError(e.strerror)

    retcode = p.poll()
    if err or retcode != 0:
        if not err.strip():
            err = 'process exited with %i.' % retcode
        raise AcrylamidException(err.strip() if PY3 else err.strip().decode('utf-8'))
    return result.strip().decode('utf-8')


def metavent(cls, parents, attrs):
    """Add classmethod to each callable, track given methods and intercept
    methods with callbacks added to cls.callbacks"""

    def intercept(func):
        """decorator which calls callback registered to this method."""
        name, doc = func.func_name, func.__doc__

        def dec(cls, ns, path, *args, **kwargs):
            for callback in  cls.callbacks[name]:
                callback(ns, path)
            if name in cls.events:
                attrs['counter'][name] += 1
            return func(cls, path, *args, **kwargs)
        dec.__doc__ = func.__doc__  # sphinx
        return dec

    for name, func in attrs.items():
        if not name.startswith('_') and callable(func):
            if name in attrs['events']:
                func = intercept(func)
            attrs[name] = classmethod(func)

    return type(cls, parents, attrs)


class event:
    """This helper class provides an easy mechanism to give user feedback of
    created, changed or deleted files.  As side-effect every it allows you to
    register your own functions to these events.

    Acrylamid has the following, fairly self-explanatory events: ``create``,
    ``update``, ``skip``, ``identical`` and ``remove``. A callback receives
    the current namespace and the path. The namespace might be None if not
    specified by the originator, but it is recommended to achieve a informal
    standard:

       * the views supply their lowercase name such as ``'entry'`` or
         ``'archive'`` as namespace.
       * asset generation uses the ``'assets'`` namespace.
       * the init, import and new task use their name as namespace.

    To make this clear, the following example just records all newly created
    items from the entry view:

    .. code-block:: python

        from acrylamid.hepers import event

        skipped = []

        def callback(ns, path):

            if ns == 'entry':
                skipped.add(path)

        event.register(callback, to=['create'])

    .. Note:: This class is a singleton and should not be initialized

    .. method:: count(event)

       :param event: count calls of this particular event
       :type event: string"""

    __metaclass__ = metavent

    # intercept these event
    events = ('create', 'update', 'remove', 'skip', 'identical')

    callbacks = defaultdict(list)
    counter = defaultdict(int)

    def __init__(self):
        raise TypeError("You can't construct event.")

    def register(self, callback, to=[]):
        """Register a callback to a list of events. Everytime the event
        eventuates, your callback gets called with all arguments of this
        particular event handler.

        :param callback: a function
        :param to: a list of events when your function gets called"""

        for item in to:
            event.callbacks[item].append(callback)

    def count(self, event):
        return self.counter.get(event, 0)

    def reset(self):
        for key in self.counter:
            self.counter[key] = 0

    def create(self, path, ctime=None):
        if ctime:
            log.info("create  [%.2fs] %s", ctime, path)
        else:
            log.info("create  %s", path)

    def update(self, path, ctime=None):
        if ctime:
            log.info("update  [%.2fs] %s", ctime, path)
        else:
            log.info("update  %s", path)

    def skip(self, path):
        log.skip("skip  %s", path)

    def identical(self, path):
        log.skip("identical  %s", path)

    def remove(self, path):
        log.info("remove  %s", path)


def discover(directories, index, filterfunc=lambda filename: True):
    """Import and initialize modules from `directories` list.

    :param directories: list of directories
    :param index: index function"""

    def find(directories, filterfunc):
        """Discover and yield python modules (aka files that endswith .py) if
        `filterfunc` returns True for that filename."""

        for directory in directories:
            for root, dirs, files in os.walk(directory):
                for fname in files:
                    if fname.endswith('.py') and filterfunc(join(root, fname)):
                        yield join(root, fname)

    for filename in find(directories, filterfunc):
        modname, ext = os.path.splitext(os.path.basename(rchop(filename, os.sep + '__init__.py')))
        fp, path, descr = imp.find_module(modname, directories)

        prefix = commonprefix((PATH, filename))
        if prefix:
            modname = 'acrylamid.'
            modname += rchop(filename[len(prefix):].replace(os.sep, '.'), '.py')

        try:
            mod = sys.modules[modname]
        except KeyError:
            try:
                mod = imp.load_module(modname, fp, path, descr)
            except (ImportError, SyntaxError, ValueError) as e:
                log.exception('%r %s: %s', modname, e.__class__.__name__, e)
                continue

        index(mod)
