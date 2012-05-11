# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os
import io
import zlib
import hashlib
import tempfile

from collections import defaultdict
from os.path import join, exists, getmtime

from acrylamid import log
from acrylamid.errors import AcrylamidException
from acrylamid.utils import memoized

from jinja2 import FileSystemLoader, meta

try:
    import cPickle as pickle
except ImportError:
    import pickle


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


class Memory(dict):

    __call__ = lambda self, k, v=None: self.__setitem__(k, v) if v else self.get(k, None)


def track(f):
    """decorator to track used cache files"""
    def dec(cls, path, key, *args, **kw):

        rv = f(cls, path, key, *args, **kw)

        if rv is not None:
            cls.tracked[path].add(key)

        return rv
    return dec


class cache(object):
    """A cache that stores the entries on the file system.  Borrowed from
    werkzeug.contrib.cache, see their AUTHORS and LICENSE for additional
    copyright information.

    This version is a bit more advanced and can track used cache objects to
    remove them, it reduces I/O so we can call `has_key` very often. After
    a run, we can automatically remove dead objects from cache.

    cache is designed as singleton and should not constructed using __init__ .

    >>> cache.init('.mycache/')
    >>> cache.get(obj, key, default=None, mtime=0.0)
    None
    >>> cache.set("My Object's name", "mykey", value)
    `value`
    >>> cache.get("My Object's name", "mykey", value)
    `value`
    >>> cache.has_key("My objects's key", "mykey")
    True
    >>> cache.has_key("Foo", "Bar")
    False
    """

    _fs_transaction_suffix = '.__ac_cache'
    cache_dir = '.cache/'
    mode = 0600

    tracked = defaultdict(set)
    objects = defaultdict(set)

    memoize = Memory()

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
                raise AcrylamidException("could not create directory '%s'" % self.cache_dir)

        # get all cache objects
        for path in self._list_dir():
            try:
                with io.open(path, 'rb') as fp:
                    self.objects[path] = set(pickle.load(fp).keys())
            except pickle.PickleError:
                os.remove(path)
            except AttributeError:
                # this may happen after a refactor
                log.info('notice  invalid cache objects, recompile everything.' \
                         + ' This may take a while...')
                for obj in self._list_dir():
                    cache.remove(obj)
                break
            except IOError:
                continue

        # load memorized items
        try:
            with io.open(join(cache.cache_dir, 'info'), 'rb') as fp:
                cache.memoize.update(pickle.load(fp))
        except (IOError, pickle.PickleError):
            pass

    @classmethod
    def shutdown(self):
        """Remove abandoned cache files that are not accessed during a compilation.
        This does not affect jinja2 templates or cache's memoize file *.cache/info*.

        This does also remove abandoned intermediates from a cache file (they accumulate
        over time)."""

        # save memoized items to disk
        try:
            path = join(self.cache_dir, 'info')
            self.tracked[path] = set(self.memoize.keys())
            with io.open(path, 'wb') as fp:
                pickle.dump(self.memoize, fp, pickle.HIGHEST_PROTOCOL)
        except (IOError, pickle.PickleError) as e:
            log.warn('%s: %s' % (e.__class__.__name__, e))

        # first we search for cache files from entries that have vanished
        for path in set(self._list_dir()).difference(set(self.tracked.keys())):
            os.remove(path)

        # next we clean the cache files itself
        for path, keys in self.tracked.iteritems():

            try:
                with io.open(path, 'rb') as fp:
                    obj = pickle.load(fp)
                    found = set(obj.keys())
            except (IOError, pickle.PickleError):
                obj, found = {}, set([])

            try:
                for key in found.difference(set(keys)):
                    obj.pop(key)
                with io.open(path, 'wb') as fp:
                    pickle.dump(obj, fp, pickle.HIGHEST_PROTOCOL)
            except pickle.PickleError:
                try:
                    os.remove(path)
                except OSError as e:
                    log.warn('OSError: %s' % e)
            except IOError:
                pass

    @classmethod
    def remove(self, path):
        """Remove a cache object completely from disk, objects and tracked files."""
        try:
            os.remove(path)
        except OSError as e:
            log.debug('OSError: %s' % e)

        self.objects.pop(path, None)
        self.tracked.pop(path, None)

    @classmethod
    def clear(self):
        for path in self._list_dir():
            cache.remove(path)

    @classmethod
    @track
    def get(self, path, key, default=None, mtime=0.0):
        """Restore value from obj[key] if mtime has not changed or return default.

        :param path: path of this cache object
        :param key: key of this value
        :param default: default return value
        :param mtime: modification timestamp as float value
        """
        try:
            if mtime > getmtime(path):
                cache.remove(path)
                return default
            with io.open(path, 'rb') as fp:
                return zlib.decompress(pickle.load(fp)[key])
        except (OSError, KeyError):
            pass
        except (IOError, pickle.PickleError, zlib.error):
            cache.remove(path)

        return default

    @classmethod
    @track
    def set(self, path, key, value):
        """Save a key, value pair into a blob using pickle and moderate zlib
        compression (level 6). We simply save a dictionary containing all
        different intermediates (from every view) of an entry.

        :param path: path of this cache object
        :param key: dictionary key where we store the value
        :param value: a string we compress with zlib and afterwards save
        """
        if exists(path):
            try:
                with io.open(path, 'rb') as fp:
                    rv = pickle.load(fp)
            except (pickle.PickleError, IOError):
                cache.remove(path)
                rv = {}
            try:
                with io.open(path, 'wb') as fp:
                    rv[key] = zlib.compress(value, 6)
                    pickle.dump(rv, fp, pickle.HIGHEST_PROTOCOL)
            except (IOError, pickle.PickleError) as e:
                log.warn('%s: %s' % (e.__class__.__name__, e))
        else:
            try:
                fd, tmp = tempfile.mkstemp(suffix=self._fs_transaction_suffix,
                                           dir=self.cache_dir)
                with io.open(fd, 'wb') as fp:
                    pickle.dump({key: zlib.compress(value, 6)}, fp, pickle.HIGHEST_PROTOCOL)
                os.rename(tmp, path)
                os.chmod(path, self.mode)
            except (IOError, OSError, pickle.PickleError, zlib.error) as e:
                log.warn('%s: %s' % (e.__class__.__name__, e))

        self.objects[path].add(key)
        return value

    @classmethod
    @track
    def has_key(self, path, key):
        """Check wether cache file has key and track them as used (= not abandoned)."""
        return key in self.objects[path]

    @classmethod
    @memoized
    def getmtime(self, path, default=0.0):
        try:
            return getmtime(path)
        except OSError:
            return default


class assets(object):

    store = defaultdict(io.StringIO)
    md5sums = set([])

    assets_dir = 'assets'
    filename = 'extra'

    @classmethod
    def init(self, assets_dir=None, filename=None):

        if assets_dir:
            self.assets_dir = assets_dir

        if filename:
            self.filename = filename

        self.store['text/css'] = io.StringIO()

    @classmethod
    def add(self, assets):

        for key, value in assets.items():

            md5 = hashlib.md5(value).hexdigest()
            if md5 in self.md5sums:
                continue

            self.store[key].write(value + u'\n\n')
            self.md5sums.add(md5)

    @classmethod
    def injected(self):

        for key in sorted(self.store.keys()):
            self.store[key].seek(0)
            path = 'extra.' + key.split('/')[-1]

            cls = type('Asset', (object, ), {'url': path,
                                             'type': key, 'source': self.store[key],
                                             'path': join(self.assets_dir, path)})
            yield cls()

