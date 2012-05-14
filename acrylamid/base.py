# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# This module currently contains the FileEntry, Entry and abstract BaseEntry class

import os
import io
import re
import sys
import abc
import traceback

from os.path import join, getmtime
from datetime import datetime

from acrylamid import log
from acrylamid.errors import AcrylamidException

from acrylamid.utils import cached_property, read
from acrylamid.core import cache
from acrylamid.filters import FilterTree
from acrylamid.helpers import safeslug, expand, md5


class BaseEntry(object):
    """An abstract version of what an Entry class should implement."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def source(self):
        return

    @abc.abstractproperty
    def content(self):
        return

    @abc.abstractproperty
    def date(self):
        return

    @abc.abstractproperty
    def md5(self):
        return

    @abc.abstractproperty
    def has_changed(self):
        return

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
    def draft(self):
        """If set to True, the entry will not appear in articles, index, feed and tag view."""
        return True if self.props.get('draft', False) else False

    @property
    def slug(self):
        """ascii safe entry title"""
        return safeslug(self.title)

    @cached_property
    def permalink(self):
        """Actual permanent link, depends on entry's property and ``permalink_format``.
        If you set permalink in the YAML header, we use this as permalink otherwise
        the URL without trailing *index.html.*"""

        try:
            return self.props['permalink']
        except KeyError:
            return expand(self.props['permalink_format'].rstrip('index.html'), self)

    @property
    def description(self):
        """first 50 characters from the source"""
        try:
            return self.props['description']
        except KeyError:
            return self.source[:50].strip() + '...'

    def __iter__(self):
        for key in self.props:
            yield key

        for key in (attr for attr in dir(self) if not attr.startswith('_')):
            yield key

    def __contains__(self, other):
        return other in self.props or other in self.__dict__

    def __getattr__(self, attr):
        try:
            return self.props[attr]
        except KeyError:
            raise AttributeError

    __getitem__ = lambda self, attr: getattr(self, attr)


class FileEntry(BaseEntry):

    def __init__(self, filename, conf):

        self.filename = filename
        self.mtime = os.path.getmtime(filename)
        self.props = dict((k, v) for k, v in conf.iteritems()
                        if k in ['author', 'lang', 'encoding', 'date_format',
                                 'permalink_format', 'email'])

        try:
            i, props = read(filename, self.props['encoding'],
                            remap={'tag': 'tags', 'filter': 'filters', 'static': 'draft'})
        except ValueError as e:
            raise AcrylamidException(str(e))

        self.offset = i
        self.props.update(props)

        fx = self.props.get('filters', [])
        if isinstance(fx, basestring):
            fx = [fx]

        self.filters = FilterTree(fx)

    def __repr__(self):
        return "<FileEntry f'%s'>" % self.filename

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
    def extension(self):
        """Filename's extension without leading dot"""
        return os.path.splitext(self.filename)[1][1:]

    @property
    def source(self):
        """Returns the actual, unmodified content."""
        with io.open(self.filename, 'r', encoding=self.props['encoding'],
        errors='replace') as f:
            return u''.join(f.readlines()[self.offset:]).strip()

    @cached_property
    def md5(self):
        return md5(self.filename, self.title, self.date)

    @property
    def content(self):

        # previous value
        res = self.source
        # growing dependencies of the filter chain
        deps = []

        for fxs in self.filters.iter(context=self.context):
            # extend dependencies
            deps.extend(fxs)

            try:
                for f in fxs:
                    res = f.transform(res, self, *f.args)
            except (IndexError, AttributeError):
                # jinja2 will ignore these Exceptions, better to catch them before
                traceback.print_exc(file=sys.stdout)

        return res

    @property
    def has_changed(self):
        return True

    @has_changed.setter
    def has_changed(self, value):
        self._has_changed = value


class Entry(FileEntry):
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

    @property
    def content(self):
        """Returns the processed content.  This one of the core functions of
        acrylamid: it compiles incrementally the filter chain using a tree
        representation and saves final output or intermediates to cache, so
        we can rapidly re-compile the whole content.

        The cache is rather dumb: Acrylamid can not determine wether it differs
        only in a single character. Thus, to minimize the overhead the cache
        object is zlib-compressed."""

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
