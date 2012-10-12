# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# Utilities that do not depend on any further Acrylamid object

from __future__ import unicode_literals

import sys
import os
import io
import re
import functools


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


class classproperty(property):
    # via http://stackoverflow.com/a/1383402
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class memoized(object):
    """Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated)."""

    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.__doc__ = func.__doc__

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


def find(fname, directory):
    """Find `fname` in `directory`, if not found try the parent folder until
    we find `fname` (as full path) or raise an :class:`IOError`."""

    directory = directory.rstrip('/')

    while directory:
        try:
            return os.path.join(directory, filter(lambda p: p == fname,
                os.listdir(directory))[0])
        except (OSError, IndexError):
            directory = directory.rsplit('/', 1)[0]
    else:
        raise IOError


def execfile(path, ns={}):
    """A python3 compatible way to use conf.py's with encoding declaration
    -- based roughly on http://stackoverflow.com/q/436198/5643233#5643233."""

    encre = re.compile(r"^#.*coding[:=]\s*([-\w.]+)")

    with io.open(path, 'r') as fp:
        try:
            enc = encre.search(fp.readline()).group(1)
        except AttributeError:
            enc = "utf-8"
        with io.open(path, 'r', encoding=enc) as fp:
            contents = '\n'.join(fp.readlines()[1:])
        if not contents.endswith("\n"):
            # http://bugs.python.org/issue10204
            contents += "\n"
        exec contents in ns


def batch(iterable, count):
    """batch a list to N items per slice"""
    result = []
    for item in iterable:
        if len(result) == count:
            yield result
            result = []
        result.append(item)
    if result:
        yield result


class NestedProperties(dict):

    def __init__(self, *args, **kwargs):

        self.redirects = dict()
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        try:
            key, other = key.split('.', 1)
            self.setdefault(key, NestedProperties())[other] = value
        except ValueError:
            dict.__setitem__(self, key, value)

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            return self[self.redirects[attr]]

    def __contains__(self, key):

        if key in self.redirects:
            key = self.redirects[key]
        return dict.__contains__(self, key)

    def update(self, dikt, **kw):
        if hasattr(dikt, 'keys'):
            for k in dikt:
                self[k] = dikt[k]
        for k in kw:
            self[k] = kw[k]

    def redirect(self, old, new):

        self[new] = self[old]
        del self[old]
        self.redirects[old] = new


def import_object(name):
    if '.' not in name:
        return __import__(name)

    parts = name.split('.')
    obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)
    return getattr(obj, parts[-1])


# A function that takes an integer in the 8-bit range and returns a
# single-character byte object in py3 / a single-character string in py2.
int2byte = (lambda x: bytes((x,))) if sys.version_info > (3, 0) else chr

def istext(path, blocksize=512, chars=(
    b''.join(int2byte(i) for i in range(32, 127)) + b'\n\r\t\f\b')):
    """Uses heuristics to guess whether the given file is text or binary,
    by reading a single block of bytes from the file. If more than 30% of
    the chars in the block are non-text, or there are NUL ('\x00') bytes in
    the block, assume this is a binary file.

    -- via http://eli.thegreenplace.net/2011/10/19/perls-guess-if-file-is-text-or-binary-implemented-in-python/"""

    with open(path, 'rb') as fp:
        block = fp.read(blocksize)
    if b'\x00' in block:
        # Files with null bytes are binary
        return False
    elif not block:
        # An empty file is considered a valid text file
        return True

    # Use translate's 'deletechars' argument to efficiently remove all
    # occurrences of chars from the block
    nontext = block.translate(None, chars)
    return float(len(nontext)) / len(block) <= 0.30


class Struct(dict):
    """A dictionary that provides attribute-style access."""

    __getitem__ = dict.__getitem__

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)
