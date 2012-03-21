# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import sys
import os
import re
import codecs
import tempfile
import time
import subprocess
from fnmatch import fnmatch
from datetime import datetime
from os.path import join, exists, dirname, getmtime
from hashlib import md5

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


class EntryList(list):

    @cached_property
    def has_changed(self):
        return filter(lambda e: e.has_changed, self)


class FileEntry:
    """This class gets it's data and metadata from the file specified
    by the filename argument"""

    __keys__ = ['permalink', 'date', 'year', 'month', 'day', 'filters', 'tags',
                'title', 'author', 'content', 'description', 'lang', 'draft',
                'extension', 'slug']
    lazy_eval = []

    def __init__(self, filename, conf):
        """parsing FileEntry's YAML header."""

        self.filename = filename
        self.mtime = os.path.getmtime(filename)
        self.props = dict((k, v) for k, v in conf.iteritems()
                        if k in ['author', 'lang', 'encoding', 'date_format',
                                 'permalink_format'])

        i, props = read(filename, self.props['encoding'],
                        remap={'tag': 'tags', 'filter': 'filters'})
        self.offset = i
        self.props.update(props)
        self.ctime = 0.01  # time used to compile (cheating with 0.01 init value)

    def __repr__(self):
        return "<fileentry f'%s'>" % self.filename

    @cached_property
    def permalink(self):
        try:
            return self.props['permalink']
        except KeyError:
            return expand(self.props['permalink_format'], self)

    @cached_property
    def date(self):
        """return datetime.datetime obj.  Either converted from given key and fmt
        or fallback to mtime."""
        if 'date' in self.props:
            try:
                ts = time.mktime(time.strptime(self.props['date'], self.props['date_format']))
                return datetime.fromtimestamp(ts)
            except ValueError:
                pass
        log.warn("using mtime from %r" % self.filename)
        return datetime.fromtimestamp(self.mtime)

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
    def filters(self):
        fx = self.props.get('filters', [])
        if isinstance(fx, basestring):
            return [fx]
        return fx

    @property
    def tags(self):
        fx = self.props.get('tags', [])
        if isinstance(fx, basestring):
            return [fx]
        return fx

    @property
    def title(self):
        return self.props.get('title', 'No Title!')

    @property
    def author(self):
        return self.props['author']

    @property
    def draft(self):
        return True if self.props.get('draft', False) else False

    @property
    def lang(self):
        return self.props['lang']

    @property
    def hash(self):
        # XXX: __hash__
        if len(self.lazy_eval) == 0:
            return ''

        to_hash = []
        for t in sorted(self.lazy_eval):
            to_hash.append('%s:%.2f:%s' % (t[0], t[1].__priority__, t[2]))
        return '-'.join(to_hash) + self.filename

    @property
    def extension(self):
        return os.path.splitext(self.filename)[1][1:]

    @property
    def source(self):
        with codecs.open(self.filename, 'r', encoding=self.props['encoding'],
        errors='replace') as f:
            return ''.join(f.readlines()[self.offset:]).strip()

    @property
    def content(self):
        try:
            rv = cache.get(self.hash, mtime=self.mtime)
            self.ctime = 0.01
            if rv is None:
                ct = time.time()
                res = self.source
                for i, f, args in self.lazy_eval:
                    f.__dict__['__matched__'] = i
                    res = f(res, self, *args)
                self.ctime = time.time() - ct
                rv = cache.set(self.hash, res)
            return rv
        except (IndexError, AttributeError):
            # jinja2 will ignore these Exceptions, better to catch them before
            traceback.print_exc(file=sys.stdout)

    @property
    def slug(self):
        return safeslug(self.title)

    @property
    def description(self):
        # TODO: this is really poor
        return self.source[:50].strip() + '...'

    @cached_property
    def has_changed(self):
        if not exists(cache._get_filename(self.hash)):
            return True
        if getmtime(self.filename) > cache.get_mtime(self.hash):
            return True
        else:
            return False

    def keys(self):
        return list(iter(self))

    def __iter__(self):
        for k in self.__keys__:
            yield k

    def __getitem__(self, key):
        return getattr(self, key)


class ExtendedFileSystemLoader(FileSystemLoader):

    def load(self, environment, name, globals=None):
        """patched `load` to add a has_changed property providing information
        whether the template or its parents have changed."""

        def resolve(parent):
            """We check whether any dependency (extend-block) has changed and
            update the bucket -- recursively. Returns True if the template
            itself or any parent template has changed. Otherwise False."""

            source, filename, uptodate = self.get_source(environment, parent)
            bucket = bcc.get_bucket(environment, parent, filename, source)
            p = bcc._get_cache_filename(bucket)
            has_changed = getmtime(filename) > getmtime(p) if exists(p) else True

            if has_changed:
                # updating cached template if timestamp has changed
                code = environment.compile(source, parent, filename)
                bucket.code = code
                bcc.set_bucket(bucket)
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


def render(tt, *dicts, **kvalue):
    """helper function to merge multiple dicts and additional key=val params
    to a single environment dict used by jinja2 templating. Note, merging will
    first update dicts in given order, then (possible) overwrite single keys
    in kvalue."""

    env = {}
    for d in dicts:
        env.update(d)
    for key in kvalue:
        env[key] = kvalue[key]

    return tt.render(env)


def union(*args, **kwargs):
    """Takes a list of dictionaries and performs union of each.  Can take additional
    key=values as parameters which may overwrite or add a key/value-pair."""

    d = args[0]
    for dikt in args[1:]:
        d.update(dict)

    d.update(kwargs)
    return d


def mkfile(content, path, message, ctime=0.0, force=False, dryrun=False, **kwargs):
    """Creates entry in filesystem. Overwrite only if content differs.

    :param content: rendered html/xml to write
    :param path: path to write to
    :param message: message to display
    :param ctime: time needed to compile
    :param force: force overwrite, even nothing has changed (defaults to `False`)
    :param dryrun: don't write anything."""

    # XXX use hashing for comparison
    if exists(dirname(path)) and exists(path):
        with file(path) as f:
            old = f.read()
        if content == old and not force:
            event.identical(message, path=path)
        else:
            if not dryrun:
                with open(path, 'w') as f:
                    f.write(content)
            event.changed(message, path=path, ctime=ctime)
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
        event.create(message, path=path, ctime=ctime)


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


def paginate(list, ipp, func=lambda x: x):

    res = filter(func, list)
    return [res[x*ipp:(x+1)*ipp] for x in range(len(res)/ipp+1)
           if res[x*ipp:(x+1)*ipp]], True


def escapes(string):
    """Escapes string to fit to the YAML standard.  I did not read the
    specs, though."""

    if filter(lambda c: c in string, '\'\"#:'):
        if '"' in string:
            return '\'' + string + '\''
        else:
            return '\"' + string + '\"'
    return string


def system(cmd, stdin=None):
    """A simple front-end to python's horrible Popen-interface which lets you
    run a single shell command (only one, semicolon and && is not supported by
    os.execvp(). Does not catch OSError!

    :param cmd: command to run (a single string or a list of strings).
    :param stdin: optional string to pass to stdin.
    """

    try:
        if stdin:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE)
            result, err = p.communicate(stdin)
        else:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    mode = 0600

    @classmethod
    def _get_filename(self, key):
        hash = md5(key).hexdigest()
        return os.path.join(self.cache_dir, hash)

    @classmethod
    def _list_dir(self):
        """return a list of (fully qualified) cache filenames"""
        return [os.path.join(self.cache_dir, fn) for fn in os.listdir(self.cache_dir)
                if not fn.endswith(self._fs_transaction_suffix) \
                   and not fn.endswith('.cache')]

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
    def get(self, key, default=None, mtime=0.0):
        try:
            filename = self._get_filename(key)
            if mtime > getmtime(filename):
                return default
            with open(filename, 'rb') as fp:
                return pickle.load(fp)
            os.remove(filename)
        except (OSError, IOError, pickle.PickleError):
            pass
        return default

    @classmethod
    def set(self, key, value):
        filename = self._get_filename(key)
        try:
            fd, tmp = tempfile.mkstemp(suffix=self._fs_transaction_suffix,
                                       dir=self.cache_dir)
            with os.fdopen(fd, 'wb') as fp:
                pickle.dump(value, fp, pickle.HIGHEST_PROTOCOL)
            os.rename(tmp, filename)
            os.chmod(filename, self.mode)
        except (IOError, OSError):
            pass

        return value

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

        if not exists(filename):
            try:
                fd, tmp = tempfile.mkstemp(suffix=self._fs_transaction_suffix,
                                           dir=self.cache_dir)
                with os.fdopen(fd, 'wb') as fp:
                    pickle.dump({}, fp, pickle.HIGHEST_PROTOCOL)
                os.rename(tmp, filename)
                os.chmod(filename, self.mode)
            except (IOError, OSError) as e:
                raise AcrylamidException(e.message)

        if not isinstance(key, str):
            raise TypeError('key must be a string')

        if value is not None:
            with open(filename, 'rb') as fp:
                values = pickle.load(fp)
            values[key] = value
            with open(filename, 'wb') as fp:
                pickle.dump(values, fp, pickle.HIGHEST_PROTOCOL)
        else:
            with open(filename, 'rb') as fp:
                return pickle.load(fp)[key]


def track(f):
    """decorator to track files when event.create|change|skip is called."""
    def dec(cls, what, path, *args, **kwargs):
        global _tracked_files
        _tracked_files.add(path)
        return f(cls, what, path, *args, **kwargs)
    return dec


def clean(conf, everything=False, dryrun=False, **kwargs):
    """Attention: this function may eat your data!  Every create, changed
    or skip event call tracks automatically files. After generation,
    ``acrylamid clean`` will call this function and remove untracked files.

    - with OUTPUT_IGNORE you can specify a list of patterns which are ignored.
    - you can use --dry-run to see what would have been removed
    - by default acrylamid does NOT call this function
    - it removes silently every empty directory

    :param conf: user configuration
    :param every: remove all tracked files, too
    :param dryrun: don't delete, just show what would have been done
    """

    def excluded(path, excl_files):
        """test if path should be ignored"""
        if filter(lambda p: fnmatch(path, p), excl_files):
            return True
        return False

    global _tracked_files
    ignored = [join(conf['output_dir'], p) for p in conf['output_ignore']]

    for root, dirs, files in os.walk(conf['output_dir'], topdown=True):
        found = set([join(root, p) for p in files
                     if not excluded(join(root, p), ignored)])
        for i, p in enumerate(found.difference(_tracked_files)):
            if not dryrun:
                os.remove(p)
            event.removed(p)

        if everything:
            for i, p in enumerate(found):
                if not dryrun:
                    os.remove(p)
                event.removed(p)

        # don't visit excluded dirs
        for dir in dirs[:]:
            p = join(root, dir)
            if excluded(p, ignored) or excluded(p+'/', ignored):
                dirs.remove(dir)

    # remove empty directories
    for root, dirs, files in os.walk(conf['output_dir'], topdown=True):
        for p in (join(root, k) for k in dirs):
            try:
                os.rmdir(p)
            except OSError:
                pass


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
    def create(self, what, path, ctime=None):
        if ctime:
            log.info("create  [%.2fs] %s", ctime, path)
        else:
            log.info("create  %s", path)

    @classmethod
    @track
    def changed(self, what, path, ctime=None):
        if ctime:
            log.info("update  [%.2fs] %s", ctime, path)
        else:
            log.info("update  %s", path)

    @classmethod
    @track
    def skip(self, what, path):
        log.skip("skip  %s", path)

    @classmethod
    @track
    def identical(self, what, path):
        log.skip("identical  %s", path)

    @classmethod
    def removed(self, path):
        log.info("removed  %s", path)
