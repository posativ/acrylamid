# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.
#
# Utilities that do not depend on any further Acrylamid object

from __future__ import unicode_literals
from __builtin__ import hash as pyhash

import sys
import os
import io
import re
import functools
import itertools


def hash(*objs, **kw):

    xor = lambda x,y: (x & 0xffffffff)^(y & 0xffffffff)
    attr = kw.get('attr', lambda o: o)

    return reduce(xor, map(lambda o: pyhash(attr(o)), objs), 0)


def rchop(original_string, substring):
    """Return the given string after chopping of a substring from the end.

    :param original_string: the original string
    :param substring: the substring to chop from the end
    """
    if original_string.endswith(substring):
        return original_string[:-len(substring)]
    return original_string


def lchop(string, prefix):
    """Return the given string after chopping the prefix from the begin.

    :param string: the original string
    :oaram prefix: prefix to chop of
    """

    if string.startswith(prefix):
        return string[len(prefix):]
    return string


class cached_property(object):
    """A property that is only computed once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property.

    Copyright (c) 2012, Marcel Hellkamp. License: MIT."""

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        if obj is None: return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
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
            return os.path.join(directory, next(itertools.ifilter(
                lambda p: p == fname, os.listdir(directory))))
        except (OSError, StopIteration):
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


def groupby(iterable, keyfunc=lambda x: x):
    """:func:`itertools.groupby` wrapper for :func:`neighborhood`."""
    for k, g in itertools.groupby(iterable, keyfunc):
        yield k, list(g)


def neighborhood(iterable, prev=None):
    """yield previous and next values while iterating"""
    iterator = iter(iterable)
    item = next(iterator)
    for new in iterator:
        yield (prev, item, new)
        prev, item = item, new
    yield (prev, item, None)


class Metadata(dict):
    """A nested :class:`dict` used for post metadata."""

    def __init__(self, dikt={}):
        super(Metadata, self).__init__(self)
        self.update(dict(dikt))


    def __setitem__(self, key, value):
        try:
            key, other = key.split('.', 1)
            self.setdefault(key, Metadata())[other] = value
        except ValueError:
            super(Metadata, self).__setitem__(key, value)

    def __getattr__(self, attr):
        return self[attr]

    def update(self, dikt):
        for key, value in dikt.iteritems():
            self[key] = value

    def redirect(self, old, new):

        self[new] = self[old]
        del self[old]


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

    def __hash__(self):
        return hash(*itertools.chain(self.keys(), self.values()))


class HashableList(list):

    def __hash__(self):
        return hash(*self)
