# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import os
import re
import codecs
import tempfile
import subprocess
import hashlib
import zlib

from fnmatch import fnmatch
from datetime import datetime
from os.path import join, exists, dirname, getmtime, basename
from collections import defaultdict

from acrylamid import log
from acrylamid.errors import AcrylamidException

import traceback
from jinja2 import FileSystemLoader, meta

try:
    import cPickle as pickle
except ImportError:
    import pickle

_slug_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')
_tracked_files = set([])

try:
    import translitcodec
except ImportError:
    from unicodedata import normalize
    translitcodec = None

try:
    import yaml
except ImportError:
    yaml = None


# Borrowed from werkzeug._internal
class _Missing(object):

    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'


# Borrowed from werkzeug.utils
class cached_property(object):
    """A decorator that converts a function into a lazy property. The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

    class Foo(object):

    @cached_property
    def foo(self):
    # calculate something important here
    return 42

    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor. non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead. If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func
        self._missing = _Missing()

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, self._missing)
        if value is self._missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


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

    with codecs.open(filename, 'r', encoding=encoding, errors='replace') as f:
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


class Node(dict):
    """This is a root, an edge and a leaf. Stores predecessor and
    count of views using this leaf."""

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.refs = 1
        self.prev = None


class FilterTree(list):

    def __init__(self, *args, **kwargs):

        # its a list after all ;-)
        super(FilterTree, self).__init__(*args, **kwargs)

        self.root = Node()
        self.views = {None: self}
        self.paths = {None: []}

    def __iter__(self):
        """Iterating over list of filters of given context."""

        raise NotImplemented('XXX get context with some magic')
        res = []
        context = None
        node = self.views[context]

        while node.prev is not None:
            res.append(node.obj)
            node = node.prev

        return reversed(res)

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
        """This returns a generator which yields a tuple containing the count
        of views using this filter list and the filter list itself."""

        path, node = self.path(context)[:], self.root
        i, j = 0, self.root[path[0]].refs

        while True:

            ls = []
            for key in path[:]:
                if node[key].refs != j:
                    j = node[key].refs
                    break

                ls.append(key)
                node = node[key]
                path.pop(0)

            if not ls:
                raise StopIteration

            i += 1
            yield i, ls


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
        with codecs.open(self.filename, 'r', encoding=self.props['encoding'],
        errors='replace') as f:
            return ''.join(f.readlines()[self.offset:]).strip()

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
        obj = md5(self.filename)

        for i, fxs in self.filters.iter(context=self.context):
            key = md5(i, fxs)

            try:
                rv = cache.get(obj, key, mtime=self.mtime)
                if rv is None:
                    res = self.source if pv is None else pv
                    for f in fxs:
                        res = f.transform(res, self, *f.args)
                    pv = cache.set(obj, key, data=res)
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

    @property
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

        path = md5(self.filename)
        filters = self.filters.iter(self.context)

        for i, fxs in filters:
            if not cache.has_key(path, md5(i, fxs)):
                return True
        else:
            return getmtime(self.filename) > cache.get_mtime(path)

    def keys(self):
        return list(iter(self))

    def __iter__(self):
        for k in self.__keys__:
            yield k

    def __getitem__(self, key):
        if key in self.__keys__:
            return getattr(self, key)
        return self.props[key]


class ExtendedFileSystemLoader(FileSystemLoader):

    # Acrylamid views (should) process templates on the fly thus we
    # don't have a 1. "select template", 2. "render template" stage
    resolved = {}

    def load(self, environment, name, globals=None):
        """patched `load` to add a has_changed property providing information
        whether the template or its parents have changed."""

        def resolve(parent):
            """We check whether any dependency (extend-block) has changed and
            update the bucket -- recursively. Returns True if the template
            itself or any parent template has changed. Otherwise False."""

            if parent in self.resolved:
                return self.resolved[parent]

            source, filename, uptodate = self.get_source(environment, parent)
            bucket = bcc.get_bucket(environment, parent, filename, source)
            p = bcc._get_cache_filename(bucket)
            has_changed = getmtime(filename) > getmtime(p) if exists(p) else True

            if has_changed:
                # updating cached template if timestamp has changed
                code = environment.compile(source, parent, filename)
                bucket.code = code
                bcc.set_bucket(bucket)

                self.resolved[parent] = True
                return True

            ast = environment.parse(source)
            for name in meta.find_referenced_templates(ast):
                rv = resolve(name)
                if rv:
                    # XXX double-return to break this recursion?
                    return True

        if globals is None:
            globals = {}

        source, filename, uptodate = self.get_source(environment, name)

        bcc = environment.bytecode_cache
        bucket = bcc.get_bucket(environment, name, filename, source)
        has_changed = bool(resolve(name))

        code = bucket.code
        if code is None:
            code = environment.compile(source, name, filename)

        tt = environment.template_class.from_code(environment, code, globals, uptodate)
        tt.has_changed = has_changed
        return tt


def filelist(content_dir, entries_ignore=[]):
    """Gathering all entries in content_dir except entries_ignore via fnmatch."""

    flist = []
    for root, dirs, files in os.walk(content_dir):
        for f in files:
            if f[0] == '.':
                continue
            path = join(root, f)
            fn = filter(lambda p: fnmatch(path, os.path.join(content_dir, p)), entries_ignore)
            if not fn:
                flist.append(path)
    return flist


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
        with file(path) as f:
            old = f.read()
        if content == old and not force:
            event.identical(path)
        else:
            if not dryrun:
                with open(path, 'w') as f:
                    f.write(content)
            event.changed(path=path, ctime=ctime)
    else:
        try:
            if not dryrun:
                os.makedirs(dirname(path))
        except OSError:
            # dir already exists (mostly)
            pass
        if not dryrun:
            with open(path, 'w') as f:
                f.write(content)
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
            if bool(filter(lambda e: e.has_changed, entries)):
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


class cache(object):
    """A cache that stores the entries on the file system.  Borrowed from
    werkzeug.contrib.cache, see their AUTHORS and LICENSE for additional
    copyright information.

    cache is designed as singleton and should not constructed using __init__ .
    >>> cache.init('.mycache/')
    >>> cache.get(key, default=None, mtime=0.0)
    >>> cache.set(key, value)"""

    _fs_transaction_suffix = '.__ac_cache'
    cache_dir = '.cache/'
    tracked = defaultdict(set)
    mode = 0600

    @classmethod
    def _get_filename(self, hash):
        return join(self.cache_dir, hash)

    @classmethod
    def _list_dir(self):
        """return a list of (fully qualified) cache filenames"""
        return [join(self.cache_dir, fn) for fn in os.listdir(self.cache_dir)
                if not fn.endswith('.cache')]

    @classmethod
    def init(self, cache_dir=None, mode=0600):
        """
        :param cache_dir: the directory where cache files are stored.
        :param mode: the file mode wanted for the cache files, default 0600
        """
        if cache_dir:
            self.cache_dir = cache_dir
        if mode:
            self.mode = mode
        if not exists(self.cache_dir):
            try:
                os.mkdir(self.cache_dir, 0700)
            except OSError:
                log.fatal("could not create directory '%s'" % self.cache_dir)
                sys.exit(1)

    @classmethod
    def clear(self):
        for fname in self._list_dir():
            try:
                os.remove(fname)
            except (IOError, OSError):
                pass

    @classmethod
    def clean(self, dryrun=False):
        """Remove abandoned cache files that are not accessed during a compilation.
        This does not affect jinja2 templates or cache's memoize file *.cache/info*.

        This does also remove abandoned intermediates from a cache file (they accumulate
        over time).

        :param dryrun: don't remove files
        """
        # first we search for cache files from entries that have vanished
        for path in set(self._list_dir()).difference(set(self.tracked.keys())):
            if not dryrun:
                os.remove(path)

        # next we clean the cache files itself
        for path, keys in self.tracked.iteritems():

            try:
                with open(path, 'rb') as fp:
                    obj = pickle.load(fp)
                    found = set(obj.keys())
            except (OSError, IOError, pickle.PickleError):
                obj, found = {}, set([])

            try:
                for key in found.difference(set(keys)):
                    obj.pop(key)
                with open(path, 'wb') as fp:
                    pickle.dump(obj, fp, pickle.HIGHEST_PROTOCOL)
            except (OSError, IOError, pickle.PickleError):
                pass

    @classmethod
    def has_key(self, obj, key):
        """check wether cache file has key and track them as used (= not abandoned)."""
        filename = self._get_filename(obj)
        self.tracked[filename].add(key)

        try:
            with open(filename, 'rb') as fp:
                return key in pickle.load(fp)
        except (OSError, IOError, pickle.PickleError):
            return False

    @classmethod
    def get(self, obj, key, default=None, mtime=0.0):
        """Restore data from obj[key] if mtime has not changed or return default.

        :param obj: object's hash that will be used as filename
        :param key: key of this data
        :param default: default return value
        :param mtime: modification timestamp as float value
        """
        try:
            filename = self._get_filename(obj)
            if mtime > getmtime(filename):
                os.remove(filename)
                return default
            with open(filename, 'rb') as fp:
                return zlib.decompress(pickle.load(fp)[key])
            os.remove(filename)
        except (OSError, IOError, KeyError, pickle.PickleError, zlib.error):
            pass
        return default

    @classmethod
    def set(self, obj, key, data):
        """Save a key, value pair into a blob using pickle and moderate zlib
        compression (level 6). We simply save a dictionary containing all
        different intermediates (from every view) of an entry.

        :param obj: the object's hash, used as filename
        :param key: dictionary key where we store the data
        :param data: a string we compress with zlib and afterwards save
        """
        filename = self._get_filename(obj)

        if exists(filename):
            try:
                with open(filename, 'rb') as fp:
                    rv = pickle.load(fp)
            except pickle.PickleError:
                rv = {}
            try:
                with open(filename, 'wb') as fp:
                    rv[key] = zlib.compress(data, 6)
                    pickle.dump(rv, fp, pickle.HIGHEST_PROTOCOL)
            except (IOError, OSError):
                pass
        else:
            try:
                fd, tmp = tempfile.mkstemp(suffix=self._fs_transaction_suffix,
                                           dir=self.cache_dir)
                with os.fdopen(fd, 'wb') as fp:
                    pickle.dump({key: zlib.compress(data, 6)}, fp, pickle.HIGHEST_PROTOCOL)
                os.rename(tmp, filename)
                os.chmod(filename, self.mode)
            except (IOError, OSError):
                pass

        return data

    @classmethod
    def get_mtime(self, key, default=0.0):
        filename = self._get_filename(key)
        try:
            mtime = getmtime(filename)
        except (OSError, IOError):
            return default
        return mtime

    @classmethod
    def memoize(self, key, value=None):
        """Memoize (stores) key/value pairs into a single file in
        `cache_dir`/info."""

        filename = join(self.cache_dir, 'info')
        self.tracked[filename].add(key)

        if not exists(filename):
            try:
                fd, tmp = tempfile.mkstemp(suffix=self._fs_transaction_suffix,
                                           dir=self.cache_dir)
                with os.fdopen(fd, 'wb') as fp:
                    pickle.dump({}, fp, pickle.HIGHEST_PROTOCOL)
                os.rename(tmp, filename)
                os.chmod(filename, self.mode)
            except (IOError, OSError) as e:
                raise AcrylamidException(str(e.message))

        if not isinstance(key, basestring):
            raise TypeError('key must be a string')

        if value is not None:
            with open(filename, 'rb') as fp:
                values = pickle.load(fp)
            values[key] = value
            with open(filename, 'wb') as fp:
                pickle.dump(values, fp, pickle.HIGHEST_PROTOCOL)
        else:
            with open(filename, 'rb') as fp:
                return pickle.load(fp).get(key, None)


def track(f):
    """decorator to track files when event.create|change|skip is called."""
    def dec(cls, path, *args, **kwargs):
        global _tracked_files
        _tracked_files.add(path)
        return f(cls, path, *args, **kwargs)
    return dec


def get_tracked_files():
    global _tracked_files
    return _tracked_files


class event:
    """this helper class provides an easy mechanism to give user feedback of
    created, changed or deleted files.  As side-effect every non-destructive
    call will add the given path to the global tracking list and makes it
    possible to remove unused files (e.g. after you've changed your permalink
    scheme or just reworded your title).

    This class is a singleton and should not be initialized."""

    @classmethod
    def __init__(self):
        raise NotImplemented

    @classmethod
    @track
    def create(self, path, ctime=None):
        if ctime:
            log.info("create  [%.2fs] %s", ctime, path)
        else:
            log.info("create  %s", path)

    @classmethod
    @track
    def changed(self, path, ctime=None):
        if ctime:
            log.info("update  [%.2fs] %s", ctime, path)
        else:
            log.info("update  %s", path)

    @classmethod
    @track
    def skip(self, path):
        log.skip("skip  %s", path)

    @classmethod
    @track
    def identical(self, path):
        log.skip("identical  %s", path)

    @classmethod
    def removed(self, path):
        log.info("removed  %s", path)
