# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.
#
# This provide some basic functionality of Acrylamid: caching and re-validating.

import os
import io
import zlib
import types
import tempfile

from os.path import join, exists, getmtime, getsize, dirname, basename

from acrylamid import log, defaults
from acrylamid.errors import AcrylamidException

from acrylamid.utils import (
    classproperty, cached_property, Struct, hash, HashableList, find, execfile,
    lchop, force_unicode as u
)

try:
    import cPickle as pickle
except ImportError:
    import pickle  # NOQA

__all__ = ['Memory', 'cache', 'Environment', 'Configuration']


class Memory(dict):
    """A callable dictionary object described at
    :func:`acrylamid.helpers.memoize`."""

    def __call__(self, key, value=None):
        if value is None:
            return self.get(key)

        rv = self.get(key)
        self[key] = value
        return rv != value


class cache(object):
    """A cache that stores all intermediates of an entry zlib-compressed on
    file system. Inspired from ``werkzeug.contrib.cache``, but heavily modified
    to fit our needs.

    Terminology: A cache object is a pickled dictionary into a single file. An
    intermediate (object) is a key/value pair that we store into a cache object.
    An intermediate is the content of an entry that is the same for a chain of
    filters used in different views.

    :class:`cache` is designed as global singleton and should not be constructed.

    .. attribute:: cache_dir

       Location where all cache objects are being stored, defaults to `.cache/`.

    The :class:`cache` does no longer maintain used/unused intermediates and cache
    objects due performance reasons (and an edge case described in #67)."""

    _fs_transaction_suffix = '.__ac_cache'
    cache_dir = '.cache/'
    mode = 0600

    memoize = Memory()

    @classmethod
    def _list_dir(self):
        """return a list of valid cache filenames

        jinja2 suffixes cached templates with .cache
        for mako, we prefix cached templates with cache_
        """
        return [fn for fn in os.listdir(self.cache_dir) if not
            (fn.endswith('.cache') or fn.startswith('cache_') or fn == '__pycache__')]

    @classmethod
    def init(self, cache_dir=None):
        """Initialize cache object by creating the cache_dir if non-existent,
        read all available cache objects and restore memoized key/values.

        :param cache_dir: the directory where cache files are stored.
        :param mode: the file mode wanted for the cache files, default 0600
        """
        if cache_dir:
            self.cache_dir = cache_dir

        if not exists(self.cache_dir):
            try:
                os.mkdir(self.cache_dir, 0700)
            except OSError:
                raise AcrylamidException("could not create directory '%s'" % self.cache_dir)

        # load memorized items
        try:
            with io.open(join(self.cache_dir, 'info'), 'rb') as fp:
                self.memoize.update(pickle.load(fp))
        except (IOError, pickle.PickleError):
            self.emptyrun = True
        else:
            self.emptyrun = False

    @classmethod
    def shutdown(self):
        """Write memoized key-value pairs to disk."""
        try:
            with io.open(join(self.cache_dir, 'info'), 'wb') as fp:
                pickle.dump(self.memoize, fp, pickle.HIGHEST_PROTOCOL)
        except (IOError, pickle.PickleError) as e:
            log.warn('%s: %s' % (e.__class__.__name__, e))

    @classmethod
    def remove(self, path):
        """Remove a cache object completely from disk and `objects`."""
        try:
            os.remove(join(self.cache_dir, path))
        except OSError as e:
            log.debug('OSError: %s' % e)

    @classmethod
    def clear(self, directory=None):
        """Wipe current cache objects and reset all stored informations.

        :param directory: directory to clean (defaults to `.cache/`"""

        if directory is not None:
            self.cache_dir = directory

        self.memoize = Memory()
        if not exists(self.cache_dir):
            return

        self.remove('info')
        for path in self._list_dir():
            self.remove(path)

    @classmethod
    def get(self, path, key, default=None):
        """Restore value from obj[key] if mtime has not changed or return
        default.

        :param path: path of this cache object
        :param key: key of this value
        :param default: default return value
        """
        try:
            with io.open(join(self.cache_dir, path), 'rb') as fp:
                return zlib.decompress(pickle.load(fp)[key]).decode('utf-8')
        except KeyError:
            pass
        except (IOError, pickle.PickleError, zlib.error):
            self.remove(join(self.cache_dir, path))

        return default

    @classmethod
    def set(self, path, key, value):
        """Save a key, value pair into a blob using pickle and moderate zlib
        compression (level 6). We simply save a dictionary containing all
        different intermediates (from every view) of an entry.

        :param path: path of this cache object
        :param key: dictionary key where we store the value
        :param value: a string we compress with zlib and afterwards save
        """
        path = join(self.cache_dir, path)

        if exists(path):
            try:
                with io.open(path, 'rb') as fp:
                    rv = pickle.load(fp)
            except (pickle.PickleError, IOError):
                self.remove(path)
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

        return value

    @classmethod
    def getmtime(self, path, default=0.0):
        """Get last modification timestamp from cache object but store it over
        the whole compilation process so we have the same value for different
        views.

        :param path: valid cache object
        :param default: default value if an :class:`OSError` occurs
        """
        try:
            return getmtime(join(self.cache_dir, path))
        except OSError:
            return default

    @classproperty
    @classmethod
    def size(self):
        """return size of all cacheobjects in bytes"""
        try:
            res = getsize(join(self.cache_dir, 'info'))
        except OSError:
            res = 0
        for (path, dirs, files) in os.walk(self.cache_dir):
            for file in files:
                filename = os.path.join(path, file)
                res += getsize(filename)
        return res


def load(path):
    """Load default configuration, prepare namespace and update configuration
    with `conf.py`'s uppercase values and normalizes ambiguous values.
    """
    conf = Configuration(defaults.conf)
    ns = dict([(k.upper(), v) for k, v in defaults.conf.iteritems()])

    os.chdir(dirname(find(basename(path), u(dirname(path) or os.getcwd()))))
    execfile(path, ns)
    conf.update(dict([(k.lower(), ns[k]) for k in ns if k.upper() == k]))

    # append trailing slash to *_dir and place certain values into an array
    return defaults.normalize(conf)


class Environment(Struct):
    """Use *only* for the environment container.  This class hides un-hashable
    keys from :class:`Struct` hash function.

    .. attribute:: modified

        Return whether the Environment has changed between two runs. This
        attribute must only be accessed after all modifications to the environment!
    """
    blacklist = set(['engine', 'translationsfor', 'options', 'archives'])

    @classmethod
    def new(self, env):
        return Environment({'author': env.author, 'url': env.url,
            'options': env.options, 'globals': Struct()})

    def keys(self):
        return sorted(list(set(super(Environment, self).keys()) - self.blacklist))

    def values(self):
        for key in self.keys():
            yield self[key]

    @cached_property
    def modified(self):
        return hash(self) != cache.memoize(self.__class__.__name__)


class Configuration(Environment):
    """Similar to :class:`Environment` but allows hashing of a literarily
    defined dictionary (that's the conf.py)."""

    blacklist = set(['if', 'hooks'])

    def fetch(self, ns):
        return Configuration((lchop(k, ns), v)
            for k, v in self.iteritems() if k.startswith(ns))

    def values(self):
        for key in self.keys():
            if isinstance(self[key], types.FunctionType):
                continue

            if isinstance(self[key], list):
                yield HashableList(self[key])
            elif isinstance(self[key], dict):
                yield Configuration(self[key])
            elif isinstance(self[key], types.NoneType):
                yield -1
            else:
                yield self[key]
