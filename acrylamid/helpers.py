# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# This module contains helper objects and function for writing third-party code.

import os
import io
import re
import hashlib
import shutil
import subprocess

from unicodedata import normalize
from collections import defaultdict
from os.path import join, dirname, basename, isdir, isfile

from acrylamid import log, PY3
from acrylamid.errors import AcrylamidException

from acrylamid.core import cache
from acrylamid.utils import batch

try:
    import translitcodec
except ImportError:
    translitcodec = None  # NOQA

try:
    from unidecode import unidecode
except ImportError:
    unidecode = None  # NOQA

__all__ = ['memoize', 'union', 'mkfile', 'md5', 'expand', 'joinurl',
           'safeslug', 'paginate', 'safe', 'system', 'event', 'rchop']

_slug_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


def memoize(key, value=None):
    """Persistent memory for small values, set and get in a single function.

    :param key: get value saved to key, if key does not exist, return None.
    :param value: set key to value
    """
    return cache.memoize(key, value)


def union(*args, **kwargs):
    """Takes a list of dictionaries and performs union of each.  Can take additional
    key=values as parameters to overwrite or add key/value-pairs."""

    d = args[0]
    for dikt in args[1:]:
        d.update(dikt)

    d.update(kwargs)
    return d


def identical(obj, other, bs=4096):
    """Takes two file-like objects and return if they are identical."""
    while True:
        a, b = obj.read(bs), other.read(bs)
        if not a or not b or a != b:
            break
    obj.seek(0), other.seek(0)
    return a == b


def mkfile(fileobj, path, ctime=0.0, force=False, dryrun=False, mode="t", **kw):
    """Creates entry in filesystem. Overwrite only if fileobj differs.

    :param fileobj: rendered html/xml as file-like object
    :param path: path to write to
    :param ctime: time needed to compile
    :param force: force overwrite, even nothing has changed (defaults to `False`)
    :param dryrun: don't write anything."""

    # reset pointer
    fileobj.seek(0)

    if isfile(path):
        with io.open(path, 'r' + mode) as other:
            if identical(fileobj, other):
                return event.identical(path)
        if not dryrun:
            if hasattr(fileobj, 'name'):
                shutil.copy(fileobj.name, path)
            else:
                with io.open(path, 'w' + mode) as fp:
                    fp.write(fileobj.read())
        event.update(path=path, ctime=ctime)
    else:
        if not dryrun and not isdir(dirname(path)):
            os.makedirs(dirname(path))
        if not dryrun:
            if hasattr(fileobj, 'name'):
                shutil.copy(fileobj.name, path)
            else:
                with io.open(path, 'w' + mode) as fp:
                    fp.write(fileobj.read())
        event.create(path=path, ctime=ctime)


def md5(*objs, **kw):
    """A multifunctional hash function that can take one or more objects
    and a getter from which you want calculate the MD5 sum.

    :param obj: one or more objects
    :param attr: a getter, defaults to ``lambda o: o.__str__()``"""

    # positional arguments before *args issue
    attr = kw.get('attr', lambda o: o.encode('utf-8') if isinstance(o, unicode) else o.__str__())
    h = hashlib.md5()

    for obj in objs:
        try:
            h.update(attr(obj))
        except (TypeError, UnicodeEncodeError):
            h.update(attr(obj).encode('utf-8'))

    return h.hexdigest()


def expand(url, obj):
    """Substitutes/expands URL parameters beginning with a colon.

    :param url: a URL with zero or more :key words
    :param obj: a dictionary where we get key from

    >>> expand('/:year/:slug/', {'year': 2012, 'slug': 'awesome title'})
    '/2011/awesome-title/'
    """

    for k in obj:
        if not k.endswith('/') and (':' + k) in url:
            url = url.replace(':'+k, unicode(obj[k]))
    return url


def joinurl(*args):
    """Joins multiple urls pieces to one single URL without loosing the root
    (first element).

    >>> joinurl('/hello/', '/world/')
    '/hello/world/'
    """
    r = []
    for i, mem in enumerate(args):
        if i > 0:
            mem = unicode(mem).lstrip('/')
        r.append(mem)
    return join(*r)


def safeslug(slug):
    """Generates an ASCII-only slug.  Borrowed from
    http://flask.pocoo.org/snippets/5/"""

    result = []
    if translitcodec:
        slug = u"" + slug.encode('translit/long').strip()
    if unidecode:
        slug = u"" + unidecode(slug)
    for word in _slug_re.split(slug.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8').strip()
        if not PY3 and translitcodec is None:
            log.once(warn="no 'translitcodec' found, using NFKD algorithm")
        if word:
            result.append(word)
    return u'-'.join(result)


def paginate(lst, ipp, func=lambda x: x, salt=None, orphans=0):
    """paginate(lst, ipp, func=lambda x: x, salt=None, orphans=0)

    Yields a triple ((next, current, previous), list of entries, has
    changed) of a paginated entrylist. It will first filter by the specified
    function, then split the ist into several sublists and check wether the
    list or an entry has changed.

    :param lst: the entrylist containing Entry instances.
    :param ipp: items per page
    :param func: filter list of entries by this function
    :param salt: uses as additional identifier in memoize
    :param orphans: avoid N orphans on last page

    >>> for x, values, _, paginate(entryrange(20), 6, orphans=2):
    ...    print x, values
    (None, 0, 1), [entries 1..6]
    (0, 1, 2), [entries 7..12]
    (1, 2, None), [entries 12..20]"""

    # apply filter function and prepare pagination with ipp
    res = filter(func, lst)
    res = list(batch(res, ipp))

    if len(res) >= 2 and len(res[-1]) <= orphans:
        res[-2].extend(res[-1])
        res.pop(-1)

    j = len(res)
    for i, entries in enumerate(res):

        i += 1
        next = None if i == 1 else i-1
        curr = i
        prev = None if i >= j else i+1

        # get caller, so we can set a unique and meaningful hash-key
        frame = log.findCaller()
        if salt is None:
            hkey = '%s:%s-hash-%i' % (basename(frame[0]), frame[2], i)
        else:
            hkey = '%s:%s-hash-%s-%i' % (basename(frame[0]), frame[2], salt, i)

        # calculating hash value and retrieve memoized value
        hv = md5(*entries, attr=lambda o: o.md5)
        rv = cache.memoize(hkey)

        if rv == hv:
            # check if an Entry-instance has changed
            if any(filter(lambda e: e.has_changed, entries)):
                has_changed = True
            else:
                has_changed = False
        else:
            # save new value for next run
            cache.memoize(hkey, hv)
            has_changed = True

        yield (next, curr, prev), entries, has_changed


def safe(string):
    """Safe string to fit in to the YAML standard (hopefully). Counterpart
    to :func:`acrylamid.readers.unsafe`."""

    if not string:
        return '""'

    if len(string) < 2:
        return string

    for char in ':%#*?{}':
        if char in string:
            if '"' in string:
                return '\'' + string + '\''
            else:
                return '\"' + string + '\"'

    for char, repl in ('\'"', '"\''):
        if string.startswith(char) and string.endswith(char):
            return repl + string + repl
    return string


def link(title, href=None, entry=None):
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
        raise AcrylamidException(err.strip().decode('utf-8'))
    return result.strip().decode('utf-8')


def metavent(cls, parents, attrs):
    """Add classmethod to each callable, track given methods and intercept
    methods with callbacks added to cls.callbacks"""

    # intercept these event
    events = ('create', 'update', 'remove', 'skip', 'identical')

    def intercept(func):
        """decorator which calls callback registered to this method."""
        name, doc = func.func_name, func.__doc__

        def dec(cls, path, *args, **kwargs):
            for callback in  cls.callbacks[name]:
                callback(path, *args, **kwargs)
            if name in events:
                attrs['counter'][name] += 1
            return func(cls, path, *args, **kwargs)
        dec.__doc__ = func.__doc__  # sphinx
        return dec

    for name, func in attrs.items():
        if not name.startswith('_') and callable(func):
            if name in events:
                func = intercept(func)
            attrs[name] = classmethod(func)

    return type(cls, parents, attrs)


class event:
    """This helper class provides an easy mechanism to give user feedback of
    created, changed or deleted files.  As side-effect every non-destructive
    call will add the given path to the global tracking list and makes it
    possible to remove unused files (e.g. after you've changed your permalink
    scheme or just reworded your title).

    .. Note:: This class is a singleton and should not be initialized

    .. method:: count(event)

       :param event: count calls of this particular event
       :type event: string"""

    __metaclass__ = metavent

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
        """:param path: path\n:param ctime: computing time"""
        if ctime:
            log.info("create  [%.2fs] %s", ctime, path)
        else:
            log.info("create  %s", path)

    def update(self, path, ctime=None):
        """:param path: path\n:param ctime: computing time"""
        if ctime:
            log.info("update  [%.2fs] %s", ctime, path)
        else:
            log.info("update  %s", path)

    def skip(self, path):
        """:param path: path"""
        log.skip("skip  %s", path)

    def identical(self, path):
        """:param path: path"""
        log.skip("identical  %s", path)

    def remove(self, path):
        """:param path: path"""
        log.info("remove  %s", path)


def rchop(original_string, substring):
    """Return the given string after chopping of a substring from the end.

    :param original_string: the original string
    :param substring: the substring to chop from the end
    """
    if original_string.endswith(substring):
        return original_string[:-len(substring)]
    return original_string
