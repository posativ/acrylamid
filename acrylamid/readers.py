# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from __future__ import unicode_literals

import os
import io
import re
import sys
import abc
import locale
import traceback

from os.path import join, getmtime
from fnmatch import fnmatch
from datetime import datetime, tzinfo, timedelta

from acrylamid import log
from acrylamid.errors import AcrylamidException

from acrylamid.utils import cached_property, NestedProperties, istext
from acrylamid.core import cache
from acrylamid.filters import FilterTree
from acrylamid.helpers import safeslug, expand, md5, rchop

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

    It returns a tuple containing the list of entries sorted by date reverse (newest
    comes first) and other pages (unsorted).

    :param conf: configuration with CONTENT_DIR and CONTENT_IGNORE set"""

    # list of Entry-objects reverse sorted by date.
    entrylist, pages = [], []

    # collect and skip over malformed entries
    for path in filelist(conf['content_dir'], conf.get('content_ignore', [])):
        if path.endswith(('.txt', '.rst', '.md')) or istext(path):
            try:
                entry = Entry(path, conf)
                if entry.type == 'entry':
                    entrylist.append(entry)
                else:
                    pages.append(entry)
            except (ValueError, AcrylamidException) as e:
                raise AcrylamidException('%s: %s' % (path, e.args[0]))

    # sort by date, reverse
    return (sorted(entrylist, key=lambda k: k.date, reverse=True), pages)


def ignored(cwd, path, patterns, directory):
    """Test wether a path is excluded by the user. The ignore syntax is
    similar to Git: a path with a leading slash means absolute position
    (relative to output root), path with trailing slash marks a directory
    and everything else is just relative fnmatch.

    :param cwd: current directory (root from :py:func:`os.walk`)
    :param path: current path
    :param patterns: a list of patterns
    :param directory: destination directory
    """

    for pattern in patterns:
        if pattern.startswith('/'):
            if fnmatch(join(cwd, path), join(directory, pattern[1:])):
                return True
        elif fnmatch(path, pattern):
            return True
    else:
        return False


def filelist(directory, patterns=[]):
    """Gathers all files in directory but excludes file by patterns. Note, that
    this generator won't raise any (IOError, OSError)."""

    for root, dirs, files in os.walk(directory):
        for path in files:
            if not ignored(root, path, patterns, directory):
                yield os.path.join(root, path)

        # don't visit excluded dirs
        for dir in dirs[:]:
            if ignored(root, dir+'/', patterns, directory):
                dirs.remove(dir)


class Date(datetime):
    """A :class:`datetime.datetime` object that returns unicode on ``strftime``."""

    def strftime(self, fmt):
        if sys.version_info < (3, 0):
            return u"" + datetime.strftime(self, fmt).decode(locale.getlocale()[1] or 'utf-8')
        return datetime.strftime(self, fmt)


class Timezone(tzinfo):
    """A dummy tzinfo object that gives :class:`datetime.datetime` more
    UTC awareness."""

    def __init__(self, offset=0):
        self.offset = timedelta(hours=offset)

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return timedelta()


class Reader(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, conf, meta):

        self.props = NestedProperties((k, v) for k, v in conf.iteritems()
            if k in ['author', 'lang', 'encoding', 'email',
                     'date_format', 'entry_permalink', 'page_permalink'])

        self.props.update(meta)
        self.type = meta.get('type', 'entry')

        # redirect singular -> plural
        for key, to in {'tag': 'tags', 'filter': 'filters'}.iteritems():
            if key in self.props:
                self.props.redirect(key, to)

        self.filters = self.props.get('filters', [])

    @abc.abstractproperty
    def md5(self):
        return

    @abc.abstractproperty
    def source(self):
        return

    @abc.abstractproperty
    def has_changed(self):
        return

    @abc.abstractproperty
    def lastmodified(self):
        return

    def getfilters(self):
        return self._filters
    def setfilters(self, filters):
        if isinstance(filters, basestring):
            filters = [filters]
        self._filters = FilterTree(filters)
    filters = property(getfilters, setfilters)

    def gettype(self):
        """="Type of this entry. Can be either ``'entry'`` or ``'page'``"""
        return self._type
    def settype(self, value):
        if value not in ('entry', 'page'):
            raise ValueError("item type must be 'entry' or 'page'")
        self._type = value
    type = property(gettype, settype, doc=gettype.__doc__)

    def hasproperty(self, prop):
        """Test whether BaseEntry has prop in `self.props`."""
        return prop in self.props

    @property
    def date(self):
        return datetime.now()

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


class FileReader(Reader):

    def __init__(self, path, conf):

        self.filename = path
        self.tzinfo = conf.get('tzinfo', None)

        native = conf.get('metastyle', '').lower() == 'native'
        with io.open(path, 'r', encoding=conf['encoding'], errors='replace') as fp:

            if native and path.endswith(('.md', '.mkdown')):
                i, meta = markdownstyle(fp)
            elif native and path.endswith(('.rst', '.rest')):
                i, meta = reststyle(fp)
            else:
                i, meta = yamlstyle(fp)

        meta['title'] = unicode(meta['title'])  # YAML can convert 42 to an int

        self.offset = i
        Reader.__init__(self, conf, meta)

    def __repr__(self):
        return "<FileReader f'%s'>" % self.filename

    @property
    def extension(self):
        """Filename's extension without leading dot"""
        return os.path.splitext(self.filename)[1][1:]

    @property
    def lastmodified(self):
        return getmtime(self.filename)

    @property
    def source(self):
        """Returns the actual, unmodified content."""
        with io.open(self.filename, 'r', encoding=self.props['encoding'],
        errors='replace') as f:
            return ''.join(f.readlines()[self.offset:]).strip()

    @cached_property
    def md5(self):
        return md5(self.filename, self.title, self.date)

    @property
    def date(self):
        "Fallback to last modification timestamp if date is unset."
        return Date.fromtimestamp(getmtime(self.filename)).replace(tzinfo=self.tzinfo)


class MetadataMixin(object):

    @property
    def slug(self):
        """ascii safe entry title"""
        slug = self.props.get('slug', None)
        if not slug:
            slug = safeslug(self.title)
        return slug

    @cached_property
    def permalink(self):
        """Actual permanent link, depends on entry's property and ``permalink_format``.
        If you set permalink in the YAML header, we use this as permalink otherwise
        the URL without trailing *index.html.*"""

        try:
            return self.props['permalink']
        except KeyError:
            return expand(rchop(self.props['%s_permalink' % self.type], 'index.html'), self)

    @cached_property
    def date(self):
        """Parse date value and return :class:`datetime.datetime` object.
        You can set a ``DATE_FORMAT`` in your :doc:`conf.py` otherwise
        Acrylamid tries several format strings and throws an exception if
        no pattern works."""

        # alternate formats from pelican.utils, thank you!
        # https://github.com/ametaireau/pelican/blob/master/pelican/utils.py
        formats = ['%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M',
                   '%Y-%m-%d', '%Y/%m/%d',
                   '%d-%m-%Y', '%Y-%d-%m',  # Weird ones
                   '%d/%m/%Y', '%d.%m.%Y',
                   '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S']

        if 'date' not in self.props:
            if self.type == 'entry':
                log.warn("using mtime from %r" % self.filename)
            return super(MetadataMixin, self).date  # Date.fromtimestamp(self.mtime)

        string = re.sub(' +', ' ', self.props['date'])
        formats.insert(0, self.props['date_format'])

        for date_format in formats:
            try:
                return Date.strptime(string, date_format).replace(tzinfo=self.tzinfo)
            except ValueError:
                pass
        else:
            raise AcrylamidException("%r is not a valid date" % string)

    @property
    def year(self):
        return self.date.year

    @property
    def imonth(self):
        return self.date.month

    @property
    def month(self):
        return '%02d' % self.imonth

    @property
    def iday(self):
        return self.date.day

    @property
    def day(self):
        return '%02d' % self.iday

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
    def description(self):
        """first 50 characters from the source"""
        try:
            return self.props['description']
        except KeyError:
            return self.source[:50].strip() + u'...'


class ContentMixin(object):
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
                rv = cache.get(path, key, mtime=self.lastmodified)
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
            return self.lastmodified > cache.getmtime(path)

    @has_changed.setter
    def has_changed(self, value):
        self._has_changed = value


class Entry(ContentMixin, MetadataMixin, FileReader):
    pass


def unsafe(string):
    """Try to remove YAML string escape characters safely from `string`.

    ---
    title: "AttributeError: queryMethodId" when creating an object
    ---

    should retain the quotations around AttributeError."""

    if len(string) < 2:
        return string

    for char in "'", '"':
        if string == 2*char:
            return ''
        try:
            if string.startswith(char) and string.endswith(char):
                return string[1:-1]
        except IndexError:
            continue
    else:
        return string


def distinguish(value):
    """Convert :param value: to None, Int, Bool, a List or String.
    """
    if not isinstance(value, (unicode, str)):
        return value

    if not isinstance(value, unicode):
        value = unicode(value)

    if value == '':
        return None
    elif value.isdigit():
        return int(value)
    elif value.lower() in ['true', 'false']:
        return True if value.capitalize() == 'True' else False
    elif value[0] == '[' and value[-1] == ']':
        return list([x.strip() for x in value[1:-1].split(',') if x.strip()])
    else:
        return unsafe(value)


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
                raise AcrylamidException('%s:%i ValueError: %s\n%s' %
                    (fileobj.name, j, line.strip('\n'),
                    ("Either your YAML is malformed or our naïve parser is to dumb \n"
                     "to read it. Revalidate your YAML or install PyYAML parser with \n"
                     "> easy_install -U pyyaml")))
            props[key] = distinguish(value)

    if 'title' not in props:
        raise AcrylamidException('No title given in %r' % fileobj.name)

    return i, props
