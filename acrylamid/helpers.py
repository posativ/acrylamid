# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# This module contains helper objects and function for writing third-party code.

import sys
import os
import io
import re
import hashlib
import traceback
import subprocess

from datetime import datetime
from collections import defaultdict
from os.path import join, exists, dirname, basename, getmtime

from acrylamid import log
from acrylamid.errors import AcrylamidException

from acrylamid.core import cache
from acrylamid.utils import cached_property
from acrylamid.filters import FilterTree

try:
    import translitcodec
except ImportError:
    from unicodedata import normalize
    translitcodec = None

try:
    import yaml
except ImportError:
    yaml = None

__all__ = ['memoize', 'union', 'mkfile', 'md5', 'expand', 'joinurl',
           'safeslug', 'paginate', 'escape', 'system', 'event', 'FileEntry']

_slug_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


def read(filename, encoding, remap={}):
    """Open and read content using the specified encoding and return position
    where the actual content begins and all collected properties.

    If ``pyyaml`` is available we use this parser but we provide a dumb
    fallback parser that can handle simple assigments in YAML.

    :param filename: path to an existing text file
    :param encoding: encoding of this file
    :param remap: remap deprecated/false-written YAML keywords
    """

    def distinguish(value):
        if value == '':
            return None
        elif value.isdigit():
            return int(value)
        elif value.lower() in ['true', 'false']:
             return True if value.capitalize() == 'True' else False
        elif value[0] == '[' and value[-1] == ']':
            return list([unicode(x.strip())
                for x in value[1:-1].split(',') if x.strip()])
        else:
            return unicode(value.strip('"').strip("'"))

    head = []
    i = 0

    with io.open(filename, 'r', encoding=encoding, errors='replace') as f:
        while True:
            line = f.readline(); i += 1
            if i == 1 and line.startswith('---'):
                pass
            elif i > 1 and not line.startswith('---'):
                head.append(line)
            elif i > 1 and line.startswith('---'):
                break

    if head and yaml:
        try:
            props = yaml.load(''.join(head))
        except yaml.YAMLError as e:
            raise AcrylamidException('YAMLError: %s' % str(e))
        for key, to in remap.iteritems():
            if key in props:
                props[to] = props[key]
                del props[key]
    else:
        props = {}
        for j, line in enumerate(head):
            if line[0] == '#' or not line.strip():
                continue
            try:
                key, value = [x.strip() for x in line.split(':', 1)]
                if key in remap:
                    key = remap[key]
            except ValueError:
                raise AcrylamidException('%s:%i ValueError: %s\n%s' %
                    (filename, j, line.strip('\n'),
                    ("Either your YAML is malformed or our "
                    "naïve parser is to dumb to read it. Revalidate\n"
                    "your YAML or install PyYAML parser: easy_install -U pyyaml")))
            props[key] = distinguish(value)

    return i, props


class FileEntry(object):
    """This class represents a single entry. Every property from this class is
    available during templating including custom key-value pairs from the
    header. The formal structure is first a YAML with some key/value pairs and
    then the actual content. For example::

        ---
        title: My Title
        date: 12.04.2012, 14:12
        tags: [some, values]

        custom: key example
        image: /path/to/my/image.png
        ---

        Here we start!

    Where you can access the image path via ``entry.image``.

    For convenience Acrylamid maps "filter" and "tag" automatically to "filters"
    and "tags" and also converts a single string into an array containing only
    one string.

    :param filename: valid path to an entry
    :param conf: acrylamid configuration

    .. attribute:: lang

       Language used in this article. This is important for the hyphenation pattern."""

    __keys__ = ['permalink', 'date', 'year', 'month', 'day', 'filters', 'tags',
                'title', 'content', 'description', 'draft', 'slug',
                'extension']

    def __init__(self, filename, conf):

        self.filename = filename
        self.mtime = os.path.getmtime(filename)
        self.props = dict((k, v) for k, v in conf.iteritems()
                        if k in ['author', 'lang', 'encoding', 'date_format',
                                 'permalink_format', 'email'])

        i, props = read(filename, self.props['encoding'],
                        remap={'tag': 'tags', 'filter': 'filters', 'static': 'draft'})
        self.offset = i
        self.props.update(props)

        fx = self.props.get('filters', [])
        if isinstance(fx, basestring):
            fx = [fx]

        self.filters = FilterTree(fx)

    def __repr__(self):
        return "<FileEntry f'%s'>" % self.filename

    @cached_property
    def permalink(self):
        """Actual permanent link, depends on entry's property and ``permalink_format``.
        If you set permalink in the YAML header, we use this as permalink otherwise
        the URL without trailing *index.html.*"""

        try:
            return self.props['permalink']
        except KeyError:
            return expand(self.props['permalink_format'].rstrip('index.html'), self)

    @cached_property
    def date(self):
        """parse date value and return :class:`datetime.datetime` object,
        fallback to modification timestamp of the file if unset.
        You can set a ``DATE_FORMAT`` in your :doc:`../conf.py` otherwise
        Acrylamid tries several format strings and throws an exception if
        no pattern works.

        As shortcut you can access ``date.day``, ``date.month``, ``date.year``
        via ``entry.day``, ``entry.month`` and ``entry.year``."""

        # alternate formats from pelican.utils, thank you!
        # https://github.com/ametaireau/pelican/blob/master/pelican/utils.py
        formats = ['%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M',
                   '%Y-%m-%d', '%Y/%m/%d',
                   '%d-%m-%Y', '%Y-%d-%m', # Weird ones
                   '%d/%m/%Y', '%d.%m.%Y',
                   '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S']

        if 'date' not in self.props:
            log.warn("using mtime from %r" % self.filename)
            return datetime.fromtimestamp(self.mtime)

        string = re.sub(' +', ' ', self.props['date'])
        formats.insert(0, self.props['date_format'])

        for date_format in formats:
            try:
                return datetime.strptime(string, date_format)
            except ValueError:
                pass
        else:
            raise AcrylamidException("%r is not a valid date" % string)

    @property
    def year(self):
        return self.date.year

    @property
    def month(self):
        return self.date.month

    @property
    def day(self):
        return self.date.day

    @property
    def tags(self):
        """Tags applied to this entry, if any.  If you set a single string it
        is converted to an array containing this string."""

        fx = self.props.get('tags', [])
        if isinstance(fx, basestring):
            return [fx]
        return fx

    @property
    def title(self):
        """Title of this entry (required)."""
        return self.props.get('title', 'No Title!')

    @property
    def draft(self):
        """If set to True, the entry will not appear in articles, index, feed and tag view."""
        return True if self.props.get('draft', False) else False

    @property
    def extension(self):
        """Filename's extension without leading dot"""
        return os.path.splitext(self.filename)[1][1:]

    @property
    def source(self):
        """Returns the actual, unmodified content."""
        with io.open(self.filename, 'r', encoding=self.props['encoding'],
        errors='replace') as f:
            return u''.join(f.readlines()[self.offset:]).strip()

    @property
    def content(self):
        """Returns the processed content.  This one of the core functions of
        acrylamid: it compiles incrementally the filter chain using a tree
        representation and saves final output or intermediates to cache, so
        we can rapidly re-compile the whole content.

        The cache is rather dumb: acrylamid can not determine wether it's
        abandoned or differs only in a single character. Thus, to minimize
        the overhead the content is zlib-compressed."""

        # previous value
        pv = None

        # this is our cache filename
        path = join(cache.cache_dir, self.md5)

        # growing dependencies of the filter chain
        deps = []

        for fxs in self.filters.iter(context=self.context):

            # extend dependencies
            deps.extend(fxs)

            # key where we save this filter chain
            key = md5(*deps)

            try:
                rv = cache.get(path, key, mtime=self.mtime)
                if rv is None:
                    res = self.source if pv is None else pv
                    for f in fxs:
                        res = f.transform(res, self, *f.args)
                    pv = cache.set(path, key, res)
                    self.has_changed = True
                else:
                    pv = rv
            except (IndexError, AttributeError):
                # jinja2 will ignore these Exceptions, better to catch them before
                traceback.print_exc(file=sys.stdout)

        return pv

    @property
    def slug(self):
        """ascii safe entry title"""
        return safeslug(self.title)

    @property
    def description(self):
        """first 50 characters from the source"""
        # XXX this is really poor
        return self.source[:50].strip() + '...'

    @cached_property
    def md5(self):
        return md5(self.filename, self.title, self.date)

    @property
    def has_changed(self):
        """Check wether the entry has changed using the following conditions:

        - cache file does not exist -> has changed
        - cache file does not contain required filter intermediate -> has changed
        - entry's file is newer than the cache's one -> has changed
        - otherwise -> not changed"""

        # with new-style classes we can't delete/overwrite @property-ied methods,
        # so we try to return a fixed value otherwise continue
        try:
            return self._has_changed
        except AttributeError:
            pass

        path = join(cache.cache_dir, self.md5)
        deps = []

        for fxs in self.filters.iter(self.context):

            # extend filter dependencies
            deps.extend(fxs)

            if not cache.has_key(path, md5(*deps)):
                return True
        else:
            return getmtime(self.filename) > cache.getmtime(path)

    @has_changed.setter
    def has_changed(self, value):
        self._has_changed = value

    def keys(self):
        return list(iter(self))

    def __iter__(self):
        for k in self.__keys__ + self.props.keys():
            yield k

    def __getattr__(self, attr):
        try:
            return self.props[attr]
        except KeyError:
            raise AttributeError

    __getitem__ = lambda self, attr: getattr(self, attr)


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
        d.update(dict)

    d.update(kwargs)
    return d


def mkfile(content, path, ctime=0.0, force=False, dryrun=False, **kwargs):
    """Creates entry in filesystem. Overwrite only if content differs.

    :param content: rendered html/xml to write
    :param path: path to write to
    :param ctime: time needed to compile
    :param force: force overwrite, even nothing has changed (defaults to `False`)
    :param dryrun: don't write anything."""

    # XXX use hashing for comparison
    if exists(dirname(path)) and exists(path):
        with io.open(path, 'r') as fp:
            old = fp.read()
        if content == old and not force:
            event.identical(path)
        else:
            if not dryrun:
                with io.open(path, 'w') as fp:
                    fp.write(content)
            event.update(path=path, ctime=ctime)
    else:
        try:
            if not dryrun:
                os.makedirs(dirname(path))
        except OSError:
            # dir already exists (mostly)
            pass
        if not dryrun:
            with io.open(path, 'w') as fp:
                fp.write(content)
        event.create(path=path, ctime=ctime)


def md5(*objs,  **kw):
    """A multifunctional hash function that can take one or more objects
    and a getter from which you want calculate the MD5 sum.

    :param obj: one or more objects
    :param attr: a getter, defaults to ``lambda o: o.__str__()``"""

    attr = kw.get('attr', lambda o: o.__str__())  # positional arguments before *args issue
    h = hashlib.md5()
    for obj in objs:
        h.update(attr(obj))

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
            url = url.replace(':'+k, str(obj[k]))
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
            mem = str(mem).lstrip('/')
        r.append(mem)
    return join(*r)


def safeslug(slug):
    """Generates an ASCII-only slug.  Borrowed from
    http://flask.pocoo.org/snippets/5/"""

    result = []
    if translitcodec:
        slug = slug.encode('translit/long').strip()
    for word in _slug_re.split(slug.lower()):
        if not translitcodec:
            word = normalize('NFKD', word).encode('ascii', 'ignore').strip()
            log.once(warn="no 'translitcodec' found, using NFKD algorithm")
        if word and not word[0] in '-:':
            result.append(word)
    return unicode('-'.join(result))


def paginate(list, ipp, func=lambda x: x, salt=None, orphans=0):
    """Yields a triple ((next, current, previous), list of entries, has
    changed) of a paginated entrylist. It will first filter by the specified
    function, then split the ist into several sublists and check wether the
    list or an entry has changed.

    :param list: the entrylist containing FileEntry instances.
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
    res = filter(func, list)
    res = [res[x*ipp:(x+1)*ipp] for x in range(len(res)/ipp+1)
           if res[x*ipp:(x+1)*ipp]]

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
            # check if a FileEntry-instance has changed
            if any(filter(lambda e: e.has_changed, entries)):
                has_changed = True
            else:
                has_changed = False
        else:
            # save new value for next run
            cache.memoize(hkey, hv)
            has_changed = True

        yield (next, curr, prev), entries, has_changed


def escape(string):
    """Escape string to fit in to the YAML standard, but I don't read the specs"""

    if filter(lambda c: c in string, '\'\"#:'):
        if '"' in string:
            return '\'' + string + '\''
        else:
            return '\"' + string + '\"'
    return string


def system(cmd, stdin=None, **kwargs):
    """A simple front-end to python's horrible Popen-interface which lets you
    run a single shell command (only one, semicolon and && is not supported by
    os.execvp(). Does not catch OSError!

    :param cmd: command to run (a single string or a list of strings).
    :param stdin: optional string to pass to stdin.
    :param kwargs: is passed to :class:`subprocess.Popen`.
    """

    try:
        if stdin:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE, **kwargs)
            result, err = p.communicate(stdin)
        else:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
            result, err = p.communicate()

    except OSError as e:
        raise OSError(e.strerror)

    retcode = p.poll()
    if err or retcode != 0:
        if not err.strip():
            err = 'process exited with %i.' % retcode
        raise AcrylamidException(err.strip())
    return result.strip()


def metavent(cls, parents, attrs):
    """Add classmethod to each callable, track given methods and intercept
    methods with callbacks added to cls.callbacks"""

    def intercept(func):
        """decorator which calls callback registered to this method."""
        name, doc = func.func_name, func.__doc__
        def dec(cls, path, *args, **kwargs):
            for callback in  cls.callbacks[name]:
                callback(path, *args, **kwargs)
            cls.called.add(name)
            return func(cls, path, *args, **kwargs)
        dec.__doc__ = func.__doc__  # sphinx
        return dec

    for name, func in attrs.items():
        if not name.startswith('_') and callable(func):
            func = intercept(func)
            attrs[name] = classmethod(intercept(func))

    return type(cls, parents, attrs)


class event:
    """This helper class provides an easy mechanism to give user feedback of
    created, changed or deleted files.  As side-effect every non-destructive
    call will add the given path to the global tracking list and makes it
    possible to remove unused files (e.g. after you've changed your permalink
    scheme or just reworded your title).

    .. Note:: This class is a singleton and should not be initialized

    .. attribute:: called

         A set of events like ``set(['create', 'skip'])`` that have been called
         during the rendering processs. When a event occurs it's directly added
         into ``called``."""

    __metaclass__ = metavent
    callbacks = defaultdict(list)
    called = set([])

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
