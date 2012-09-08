# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# This provide some basic functionality of Acrylamid: caching and re-validating.

import os
import io
import zlib
import tempfile

from collections import defaultdict
from os.path import join, exists, getmtime

from acrylamid import log
from acrylamid.errors import AcrylamidException

from acrylamid.utils import memoized, classproperty

try:
    import cPickle as pickle
except ImportError:
    import pickle  # NOQA

__all__ = ['Memory', 'cache']


class Memory(dict):
    """A callable dictionary object described at
    :func:`acrylamid.helpers.memoize`."""

    __call__ = lambda self, k, v=None: self.__setitem__(k, v) if v else self.get(k, None)


def track(func):
    """Decorator to track accessed cache objects that return something != None.

    :param func: function to decorate
    """
    def dec(cls, path, key, *args, **kw):

        rv = func(cls, path, key, *args, **kw)

        if rv is not None:
            cls.tracked[path].add(key)

        return rv
    return dec


class cache(object):
    """A cache that stores all intermediates of an entry zlib-compressed on
    file system. Inspired from ``werkzeug.contrib.cache``, but heavily modified
    to fit our needs.

    This cache is a bit more advanced and can track used cache objects to
    remove them afterwards, it reduces I/O so we can call `has_key` very
    often. After a run, we can automatically remove dead objects from cache.

    Terminology: A cache object is a pickled dictionary into a single file in
    cache. An intermediate (object) is a key/value pair that we store into a
    cache object. An intermediate is the content of an entry that is the same
    for an amount of filters.

    cache is designed as global singleton and should not be constructed.

    .. attribute:: cache_dir

       Location where all cache objects are being stored, defaults to *.cache/*

    .. attribute:: tracked

       A bunch of cache objects with all tracked (used) intermediate objects

    .. attribute:: objects

       Internal cache for less I/O on cache objects containing all cache objects
       and keys belong to them. On :func:`init` we parse all existent cache
       objects and update them when it's necessary (we delete or update an
       cache object).

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
        """return a list of valid cache filenames

        jinja2 suffixes cached templates with .cache
        for mako, we prefix cached templates with cache_
        """
        return [join(self.cache_dir, fn) for fn in os.listdir(self.cache_dir)
                if not (fn.endswith('.cache') or fn.startswith('cache_'))]

    @classmethod
    def init(self, cache_dir=None, mode=0600):
        """Initialize cache object by creating the cache_dir if non-existent,
        read all available cache objects and restore memoized key/values.

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
                raise AcrylamidException("could not create directory '%s'" %
                                         self.cache_dir)

        # get all cache objects
        for path in self._list_dir():
            try:
                with io.open(path, 'rb') as fp:
                    self.objects[path] = set(pickle.load(fp).keys())
            except pickle.PickleError:
                os.remove(path)
            except (AttributeError, EOFError):
                # this may happen after a refactor
                log.info('notice  stale cache objects')
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
        """Remove abandoned cache files that are not accessed during compilation
        process. This does not affect jinja2 templates or *.cache/info*. This
        also removes abandoned intermediates from a cache file (they may
        accumulate over time)."""

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
        """Remove a cache object completely from disk, objects and tracked
        files."""
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
        cache.remove(join(self.cache_dir, 'info'))
        cache.memoize = Memory()

    @classmethod
    @track
    def get(self, path, key, default=None, mtime=0.0):
        """Restore value from obj[key] if mtime has not changed or return
        default.

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
                return zlib.decompress(pickle.load(fp)[key]).decode('utf-8')
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
                    rv[key] = zlib.compress(value.encode('utf-8'), 6)
                    pickle.dump(rv, fp, pickle.HIGHEST_PROTOCOL)
            except (IOError, pickle.PickleError) as e:
                log.warn('%s: %s' % (e.__class__.__name__, e))
        else:
            try:
                fd, tmp = tempfile.mkstemp(suffix=self._fs_transaction_suffix,
                                           dir=self.cache_dir)
                with io.open(fd, 'wb') as fp:
                    pickle.dump({key: zlib.compress(value.encode('utf-8'), 6)}, fp,
                                pickle.HIGHEST_PROTOCOL)
                os.rename(tmp, path)
                os.chmod(path, self.mode)
            except (IOError, OSError, pickle.PickleError, zlib.error) as e:
                log.warn('%s: %s' % (e.__class__.__name__, e))

        self.objects[path].add(key)
        return value

    @classmethod
    @track
    def has_key(self, path, key):
        """Check wether cache file has key and track them as used (that means
        not abandoned)."""
        return key in self.objects[path]

    @classmethod
    @memoized
    def getmtime(self, path, default=0.0):
        """Get last modification timestamp from cache object but store it over
        the whole compilation process so we have the same value for different
        views.

        :param path: valid cache object
        :param default: default value if an :class:`OSError` occurs
        """
        try:
            return getmtime(path)
        except OSError:
            return default

    @classproperty
    @classmethod
    def size(self):
        res = 0
        for (path, dirs, files) in os.walk(self.cache_dir):
            for file in files:
                filename = os.path.join(path, file)
                res += os.path.getsize(filename)
        return res
