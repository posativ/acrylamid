# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# Utilities that do not depend on any further Acrylamid object

import os
import io
import functools

from fnmatch import fnmatch

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


class memoized(object):
   """Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   """
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


def filelist(content_dir, entries_ignore=[]):
    """Gathering all entries in content_dir except entries_ignore via fnmatch."""

    flist = []
    for root, dirs, files in os.walk(content_dir):
        for f in files:
            if f[0] == '.':
                continue
            path = os.path.join(root, f)
            fn = filter(lambda p: fnmatch(path, os.path.join(content_dir, p)), entries_ignore)
            if not fn:
                flist.append(path)
    return flist


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
            raise ValueError('YAMLError: %s' % str(e))
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
                raise ValueError('%s:%i ValueError: %s\n%s' %
                    (filename, j, line.strip('\n'),
                    ("Either your YAML is malformed or our naïve parser is to dumb \n"
                     "to read it. Revalidate your YAML or install PyYAML parser with \n"
                     "> easy_install -U pyyaml")))
            props[key] = distinguish(value)

    if 'title' not in props:
        raise ValueError('No title given in %r' % filename)

    return i, props
