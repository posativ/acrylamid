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

_slug_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


def read(filename, encoding, remap={}):
    """Open filename and read content using specified encoding.  It will try
    to parse the YAML header with yaml.load or fallback (if not available) to
    a naïve key-value parser. Returns offset where the real content begins and
    YAML header.

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


class FileEntry:
    """This class gets it's data and metadata from the file specified
    by the filename argument.

    During templating, every (cached) property is available as well as additional
    key, value pairs defined in the YAML header. Note that *tag* is automatically
    mapped to *tags*, *filter* to *filters* and *static* to *draft*.

    If you have something like

    ::

        ---
        title: Foo
        image: /path/to/my/image.png
        ---

    it is available in jinja2 templates as entry.image"""

    __keys__ = ['permalink', 'date', 'year', 'month', 'day', 'filters', 'tags',
                'title', 'author', 'content', 'description', 'lang', 'draft',
                'extension', 'slug']

    def __init__(self, filename, conf):
        """parsing FileEntry's YAML header."""

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
        """return :class:`datetime.datetime` object.  Either converted from given key
        and ``date_format`` or fallback to modification timestamp of the file."""

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
        """entry's year (Integer)"""
        return self.date.year

    @property
    def month(self):
        """entry's month (Integer)"""
        return self.date.month

    @property
    def day(self):
        """entry's day (Integer)"""
        return self.date.day

    @property
    def tags(self):
        """per-post list of applied tags, if any.  If you applied a single string it
        is used as one-item array."""

        fx = self.props.get('tags', [])
        if isinstance(fx, basestring):
            return [fx]
        return fx

    @property
    def title(self):
        """entry's title."""
        return self.props.get('title', 'No Title!')

    @property
    def author(self):
        """entry's author as set in entry or from conf.py if unset"""
        return self.props['author']

    @property
    def email(self):
        """the author's email address"""
        return self.props['email']

    @property
    def draft(self):
        """If set to True, the entry will not appear in articles, index, feed and tag view."""
        return True if self.props.get('draft', False) else False

    @property
    def lang(self):
        return self.props['lang']

    @property
    def extension(self):
        """filename's extension without leading dot"""
        return os.path.splitext(self.filename)[1][1:]

    @property
    def source(self):
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
        - otherwise -> not changed
        """

        path = join(cache.cache_dir, self.md5)
        deps = []

        for fxs in self.filters.iter(self.context):

            # extend filter dependencies
            deps.extend(fxs)

            if not cache.has_key(path, md5(*deps)):
                return True
        else:
            return getmtime(self.filename) > cache.getmtime(path)

    def keys(self):
        return list(iter(self))

    def __iter__(self):
        for k in self.__keys__:
            yield k

    def __getitem__(self, key):
        if key in self.__keys__:
            return getattr(self, key)
        return self.props[key]


def memoize(key, value=None):
    """A shortcut to core.cache.memoize"""
    return cache.memoize(key, value)


def union(*args, **kwargs):
    """Takes a list of dictionaries and performs union of each.  Can take additional
    key=values as parameters which may overwrite or add a key/value-pair."""

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
    """A multifunctional hash function which can take one or multiple objects
    and you can specify which character-sequences you want calculate to a MD5."""

    attr = kw.get('attr', lambda o: o.__str__())  # positional arguments before *args issue
    h = hashlib.md5()
    for obj in objs:
        h.update(attr(obj))

    return h.hexdigest()


def expand(url, obj):
    """expanding '/:year/:slug/' scheme into e.g. '/2011/awesome-title/"""

    for k in obj:
        if not k.endswith('/') and (':' + k) in url:
            url = url.replace(':'+k, str(obj[k]))
    return url


def joinurl(*args):
    """joins multiple urls to one single domain without loosing root (first element)"""

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
    """Yields a triple (index, list of entries, has changed) of a paginated
    entrylist.  It will first filter by the specified function, then split the
    ist into several sublists and check wether the list or an entry has changed.

    :param list: the entrylist containing FileEntry instances.
    :param ipp: items per page
    :param func: filter list of entries by this function
    :param salt: uses as additional identifier in memoize
    :param orphans: avoid N orphans on last page.
    """

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
    """Escape string to fit to the YAML standard.  I did not read the
    specs, though."""

    if filter(lambda c: c in string, '\'\"#:'):
        if '"' in string:
            return '\'' + string + '\''
        else:
            return '\"' + string + '\"'
    return string


def system(cmd, stdin=None, **kw):
    """A simple front-end to python's horrible Popen-interface which lets you
    run a single shell command (only one, semicolon and && is not supported by
    os.execvp(). Does not catch OSError!

    :param cmd: command to run (a single string or a list of strings).
    :param stdin: optional string to pass to stdin.
    :param kw: everything there is passed to Popen.
    """

    try:
        if stdin:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE, **kw)
            result, err = p.communicate(stdin)
        else:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw)
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
        name = func.func_name
        def dec(cls, path, *args, **kwargs):
            for callback in  cls.callbacks[name]:
                callback(path, *args, **kwargs)
            cls.called.add(name)
            return func(cls, path, *args, **kwargs)
        return dec

    for name, func in attrs.items():
        if not name.startswith('_') and callable(func):
            func = intercept(func)
            attrs[name] = classmethod(intercept(func))

    return type(cls, parents, attrs)


class event:
    """this helper class provides an easy mechanism to give user feedback of
    created, changed or deleted files.  As side-effect every non-destructive
    call will add the given path to the global tracking list and makes it
    possible to remove unused files (e.g. after you've changed your permalink
    scheme or just reworded your title).

    This class is a singleton and should not be initialized."""

    __metaclass__ = metavent
    callbacks = defaultdict(list)
    called = set([])

    def __init__(self):
        raise AcrylamidException('Not Implemented')

    def register(self, callback, to=[]):
        for item in to:
            event.callbacks[item].append(callback)

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
