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
import locale
import traceback

from os.path import join, getmtime
from datetime import datetime

from acrylamid import log
from acrylamid.errors import AcrylamidException

from acrylamid.utils import cached_property, NestedProperties, filelist, istext
from acrylamid.core import cache
from acrylamid.filters import FilterTree
from acrylamid.helpers import safeslug, expand, md5

try:
    import yaml
except ImportError:
    yaml = None  # NOQA


def load(conf):
    """Load and parse textfiles from content directory and optionally filter by an
    ignore pattern. Filenames ending with a known binary extension such as audio,
    video or images are ignored. If not blacklisted open the file end check if it
    :func:`utils.istext`.

    This function is *not* exception-tolerant. If Acrylamid could not handle a file
    it will raise an exception.

    It returns a list of entries sorted by date reverse (newest comes first).

    :param conf: configuration with CONTENT_DIR and CONTENT_IGNORE set"""

    # list of Entry-objects reverse sorted by date.
    entrylist = []

    # collect and skip over malformed entries
    for path in filelist(conf['content_dir'], conf.get('content_ignore', [])):
        if path.endswith(('.txt', '.rst', '.md')) or istext(path):
            try:
                entrylist.append(Entry(path, conf))
            except (ValueError, AcrylamidException) as e:
                raise AcrylamidException('%s: %s' % (path, e.args[0]))

    # sort by date, reverse
    return sorted(entrylist, key=lambda k: k.date, reverse=True)


class Date(datetime):
    """A :class:`datetime.datetime` object that returns unicode on ``strftime``."""

    def strftime(self, fmt):
        if sys.version_info < (3, 0):
            return u"" + datetime.strftime(self, fmt).decode(locale.getlocale()[1])
        return datetime.strftime(self, fmt)


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
    def zmonth(self):
        return '%02d' % self.month

    @property
    def day(self):
        return self.date.day

    @property
    def zday(self):
        return '%02d' % self.day

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
            return self.source[:50].strip() + u'...'

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
            raise AttributeError(attr)

    __getitem__ = lambda self, attr: getattr(self, attr)


class FileEntry(BaseEntry):

    def __init__(self, path, conf):

        self.filename = path
        self.mtime = os.path.getmtime(path)
        self.props = NestedProperties((k, v) for k, v in conf.iteritems()
            if k in ['author', 'lang', 'encoding', 'date_format', 'permalink_format', 'email'])

        native = conf.get('metastyle', '').lower() == 'native'

        with io.open(path, 'r', encoding=conf['encoding'], errors='replace') as fp:

            if native and path.endswith(('.md', '.mkdown')):
                i, meta = markdownstyle(fp)
            elif native and path.endswith(('.rst', '.rest')):
                i, meta = reststyle(fp)
            else:
                i, meta = yamlstyle(fp)

        # remap singular -> plural
        for key, to in {'tag': 'tags', 'filter': 'filters', 'static': 'draft'}.iteritems():
            if key in meta:
                meta[to] = meta[key]
                del meta[key]

        self.offset = i
        self.props.update(meta)

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
                   '%d-%m-%Y', '%Y-%d-%m',  # Weird ones
                   '%d/%m/%Y', '%d.%m.%Y',
                   '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S']

        if 'date' not in self.props:
            log.warn("using mtime from %r" % self.filename)
            return Date.fromtimestamp(self.mtime)

        string = re.sub(' +', ' ', self.props['date'])
        formats.insert(0, self.props['date_format'])

        for date_format in formats:
            try:
                return Date.strptime(string, date_format)
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


def distinguish(value):
    """Convert :param value: to None, Int, Bool, a List or String.
    """

    if not isinstance(value, unicode):
        return value

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


def markdownstyle(fileobj):
    """Parse Markdown Metadata without converting the source code. Mostly copy&paste
    from the 'meta' extension but slighty modified to fit to Acrylamid: we try to parse
    a value into a python value (via :func:`distinguish`)."""

    # -- from markdown.extensions.meta
    meta_re = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9._-]+):\s*(?P<value>.*)')
    meta_more_re = re.compile(r'^[ ]{4,}(?P<value>.*)')

    i = 0
    meta, key = {}, None

    while True:
        line = fileobj.readline(); i += 1

        if line.strip() == '':
            break  # blank line - done

        m1 = meta_re.match(line)
        if m1:
            key = m1.group('key').lower().strip()
            value = distinguish(m1.group('value').strip())
            try:
                meta[key].append(value)
            except KeyError:
                meta[key] = [value]
        else:
            m2 = meta_more_re.match(line)
            if m2 and key:
                # Add another line to existing key
                meta[key].append(m2.group('value').strip())
            else:
                break  # no meta data - done

    if not meta:
        raise AcrylamidException("no meta information in %r found" % fileobj.name)

    for key, values in meta.iteritems():
        if key not in ('tag', 'tags') and len(values) == 1:
            meta[key] = values[0]

    return i, meta


def reststyle(fileobj):
    """Parse metadata from reStructuredText document when the first two lines are
    valid reStructuredText headlines followed by metadata fields.

    -- http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#field-lists"""

    import docutils
    from docutils.core import publish_doctree

    title = fileobj.readline().strip('\n')
    dash = fileobj.readline().strip('\n')

    if not title or not dash:
        raise AcrylamidException('No title given in %r' % fileobj.name)

    if len(dash) != len(title) or dash.count(dash[0]) != len(dash):
        raise AcrylamidException('title line does not match second line %r' % fileobj.name)

    i = 2
    meta = []

    while True:
        line = fileobj.readline(); i += 1

        if not line.strip() and i == 3:
            continue
        elif not line.strip():
            break  # blank line - done
        else:
            meta.append(line)

    document = publish_doctree(''.join(meta))
    meta = dict(title=title)

    for docinfo in document.traverse(docutils.nodes.docinfo):
        for element in docinfo.children:
            if element.tagname == 'field':  # custom fields
                name_elem, body_elem = element.children
                name = name_elem.astext()
                value = body_elem.astext()
            else:  # standard fields (e.g. filters)
                name = element.tagname
                value = element.astext()
            name = name.lower()

            if '\n\n' in value:
                value = value.split('\n\n')  # Y U NO DETECT UR LISTS?
            elif '\n' in value:
                value = value.replace('\n', ' ')  # linebreaks in wrapped sentences

            meta[name] = distinguish(value.split('\n\n') if '\n\n' in value else value)

    return i, meta


def yamlstyle(fileobj):
    """Open and read content using the specified encoding and return position
    where the actual content begins and all collected properties.

    If ``pyyaml`` is available we use this parser but we provide a dumb
    fallback parser that can handle simple assigments in YAML.

    :param fileobj: fileobj with correct encoding
    """

    head = []
    i = 0

    while True:
        line = fileobj.readline(); i += 1
        if i == 1 and not line.startswith('---'):
            raise AcrylamidException("no meta information in %r found" % fileobj.name)
        elif i > 1 and not line.startswith('---'):
            head.append(line)
        elif i > 1 and line.startswith('---') or not line:
            break

    if yaml:
        try:
            return i, yaml.load(''.join(head))
        except yaml.YAMLError as e:
            raise AcrylamidException('YAMLError: %s' % str(e))
    else:
        props = {}
        for j, line in enumerate(head):
            if line[0] == '#' or not line.strip():
                continue
            try:
                key, value = [x.strip() for x in line.split(':', 1)]
            except ValueError:
                raise ValueError('%s:%i ValueError: %s\n%s' %
                    (fileobj.name, j, line.strip('\n'),
                    ("Either your YAML is malformed or our naïve parser is to dumb \n"
                     "to read it. Revalidate your YAML or install PyYAML parser with \n"
                     "> easy_install -U pyyaml")))
            props[key] = distinguish(value)

    if 'title' not in props:
        raise AcrylamidException('No title given in %r' % fileobj.name)

    return i, props


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
