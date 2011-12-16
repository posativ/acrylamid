#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import sys, os, re, logging
import codecs
import tempfile
from datetime import datetime
from os.path import join, exists, dirname, getmtime
from hashlib import md5

import traceback
from jinja2 import FileSystemLoader

try:
    import cPickle as pickle
except ImportError:
    import pickle

log = logging.getLogger('acrylamid.utils')
_slug_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

try:
    import translitcodec
except ImportError:
    from unicodedata import normalize
    translitcodec = None
    log.debug("no 'translitcodec' found, using NFKD algorithm")


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


class FileEntry:
    """This class gets it's data and metadata from the file specified
    by the filename argument"""
    
    __map__ = {'tag': 'tags', 'filter': 'filters'}
    __keys__ = ['permalink', 'filters', 'author', 'draft', 'tags', 'date', 'title', 'content', 'lang', 'description']
    
    title = content = ''
    draft = False
    permalink = lang = None
    tags = filters = lazy_eval = []
    
    def __init__(self, filename, encoding='utf-8'):
        """parsing FileEntry's YAML header.
        
        :param filename: path to open, plain text preferred
        :param encoding: reading content using this specific encoding codec."""
        
        self.mtime = os.path.getmtime(filename)
        self.date = datetime.fromtimestamp(self.mtime)
        self.filename = filename
        self.encoding = encoding
        self.parse()
        
    def __repr__(self):
        return "<fileentry f'%s'>" % self.filename
    
    @property
    def hash(self):
        if len(self.lazy_eval) == 0:
            return ''
        
        to_hash = []
        for t in self.lazy_eval:
            to_hash.append('%s:%.2f:%s' % (t[0], t[1].__priority__, t[2]))
        return '-'.join(to_hash) + self.filename
        
    @property
    def extension(self):
        return os.path.splitext(self.filename)[1][1:]
        
    @property
    def source(self):
        with codecs.open(self.filename, 'r', encoding=self.encoding) as f:
            return ''.join(f.readlines()[self._i:]).strip()
    
    @property
    def content(self):
       try:
            rv = cache.get(self.hash, mtime=self.mtime)
            if not rv:
                res = self.source
                for i, f, args in self.lazy_eval:
                    f.__dict__['__matched__'] = i
                    res = f(res, self, *args)
                rv = cache.set(self.hash, res)
            return rv
       except (IndexError, AttributeError):
           # jinja2 will ignore these Exceptions, better to catch them before
           traceback.print_exc(file=sys.stdout)
            
    @property
    def slug(self):
        return safeslug(self.title)
        
    @property
    def permalink(self):
        # TODO: fix hard-coded slug
        return expand('/:year/:slug/', self)

    @property
    def description(self):
        # TODO: this is really poor
        return self.source[:50].strip()+'...'
    
    @cached_property
    def has_changed(self):
        if not exists(cache._get_filename(self.hash)):
            self.content
        if getmtime(self.filename) > cache.get_mtime(self.hash):
            return True
        else:
            return False
        
    def get(self, key, default=None):
        return self.__dict__.get(key, default)
        
    def parse(self):
        """parsing yaml header and remember where content begins. Only append
        key,value if whitelisted in __keys__ and __map__ ."""
        
        meta = []; i = 0
        with file(self.filename, 'r') as f:
            while True:
                line = f.readline()
                i += 1
                if i == 1 and not line.strip():
                    break
                elif i == 1 and line.startswith('---'):
                    pass
                elif i > 1 and not line.startswith('---'):
                    meta.append(line)
                else:
                    break
                
        self._i = i
        for key, value in yamllike(''.join(meta)).iteritems():
            if key not in self.__keys__+self.__map__.keys():
                continue
            if isinstance(value, basestring):
                self.__dict__[key] = unicode(value.strip('"'))
            else:
                self.__dict__[key] = value

    def keys(self):
        return filter(lambda k: hasattr(self, k), self.__keys__)
        
    def __getitem__(self, key):
        """surjective dict. Return mapped key (tag -> tags) or raise KeyError."""
        if key in self.__map__:
            return self.__dict__[self.__map__[key]]
        elif key in self.__keys__:
            return getattr(self, key)
        else:
            raise KeyError("%s has no such attribute '%s'" % (self, key))


class ColorFormatter(logging.Formatter):
    """Implements basic colored output using ANSI escape codes."""

    # $color + BOLD
    BLACK = '\033[1;30m%s\033[0m'
    RED = '\033[1;31m%s\033[0m'
    GREEN = '\033[1;32m%s\033[0m'
    YELLOW = '\033[1;33m%s\033[0m'
    GREY = '\033[1;37m%s\033[0m'
    RED_UNDERLINE = '\033[4;31m%s\033[0m'

    def __init__(self, fmt='[%(levelname)s] %(name)s: %(message)s', debug=False):
        logging.Formatter.__init__(self, fmt)
        self.debug = debug

    def format(self, record):

        keywords = {'skip': self.BLACK, 'create': self.GREEN, 'identical': self.BLACK,
                    'update': self.YELLOW, 'changed': self.YELLOW}
                    
        if record.levelno == logging.INFO:
            for item in keywords:
                if record.msg.startswith(item):
                    record.msg = record.msg.replace(item, ' '*2 + \
                                    keywords[item] % item.rjust(8))
        elif record.levelno >= logging.WARN:
            record.levelname = record.levelname.replace('WARNING', 'WARN')
            record.msg = ''.join([' '*2, self.RED % record.levelname.lower().rjust(8),
                                  '  ', record.msg])

        return logging.Formatter.format(self, record)


class ExtendedFileSystemLoader(FileSystemLoader):

    def load(self, environment, name, globals=None):
        """patched `load` to add a has_changed property"""
        code = None
        if globals is None:
            globals = {}

        source, filename, uptodate = self.get_source(environment, name)

        bcc = environment.bytecode_cache
        if bcc is not None:
            bucket = bcc.get_bucket(environment, name, filename, source)
            p = bcc._get_cache_filename(bucket)
            has_changed = getmtime(filename) > getmtime(p) if exists(p) else False
            print filename, has_changed
            code = bucket.code

        if code is None:
            code = environment.compile(source, name, filename)

        if bcc is not None and bucket.code is None:
            bucket.code = code
            bcc.set_bucket(bucket)

        tt = environment.template_class.from_code(environment, code, globals, uptodate)
        tt.has_changed = has_changed
        return tt


def check_conf(conf):
    """Rudimentary conf checking.  Currently every *_dir except
    `ext_dir` (it's a list of dirs) is checked wether it exists."""

    # directories

    for key, value in conf.iteritems():
        if key.endswith('_dir') and not key in ['ext_dir', ]:
            if os.path.exists(value):
                if os.path.isdir(value):
                    pass
                else:
                    log.error("'%s' must be a directory" % value)
                    sys.exit(1)
            else:
                os.mkdir(value)
                log.warning('%s created...' % value)

    return True
    
def yamllike(conf):
    """pyyaml replacement (not really yet, but works for me). Parsing
    first-layer YAML (okay: key,value assignments) into a python dict.
    yamllike is filter. and view. aware, that means all assignments starting
    with this string will exec into the given __init__ environment."""
    
    conf = [line.strip() for line in conf.split('\n')
                if not line.startswith('#') and line.strip()]
    
    config = {}
    config['views.'] = []
    config['filters.'] = []
    for line in conf:
        try:
            key, value = [x.strip() for x in line.split(':', 1)]
        except ValueError:
            # do something
            log.warn('conf.yaml -> ValueError: %s' % line)
            continue
        
        if key.startswith('filters.'):
            config['filters.'].append(key.replace('filters.', '')+' = '+value+'\n')
        elif key.startswith('views.'):
            config['views.'].append(key.replace('views.', '')+' = '+value+'\n')
        else:
            if value == '':
                config[key] = None
            elif value.isdigit():
                config[key] = int(value)
            elif value.lower() in ['true', 'false']:
                 config[key] = True if value.capitalize() == 'True' else False
            elif value[0] == '[' and value[-1] == ']':
                config[key] = list([unicode(x.strip()) for x in value[1:-1].split(',') if x.strip()])
            else:
                config[key] = value
    
    return config


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


def mkfile(content, entry, path, force=False):
    """Creates entry in filesystem. Overwrite only if content differs.

    :param content: rendered html/xml to write
    :param entry: FileEntry object
    :param path: path to write to
    :param force: force overwrite, even nothing has changed (defaults to `False`)"""

    if exists(dirname(path)) and exists(path):
        with file(path) as f:
            old = f.read()
        if content == old and not force:
            event.skip(entry['title'])
        else:
            f = open(path, 'w')
            f.write(content)
            f.close()
            event.changed(entry['title'])
    else:
        try:
            os.makedirs(dirname(path))
        except OSError:
            # dir already exists (mostly)
            pass
        f = open(path, 'w')
        f.write(content)
        f.close()
        event.create(entry['title'], path)

    
def expand(url, entry):
    """expanding '/:year/:slug/' scheme into e.g. '/2011/awesome-title/"""
    m = {':year': str(entry.date.year), ':month': str(entry.date.month),
         ':day': str(entry.date.day), ':slug': entry.slug}
    
    for val in m:
        url = url.replace(val, m[val])
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
    for word in _slug_re.split(slug.lower()):
        if translitcodec:
            word = word.encode('translit/long')
        else:
            word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word and not word[0] in '-:':
            result.append(word)
    return unicode('-'.join(result))


class cache(object):
    """A cache that stores the entries on the file system.  Borrowed from
    werkzeug.contrib.cache, see their AUTHORS and LICENSE for additional
    copyright information.
    
    cache is designed as singleton and should not constructed using __init__ .
    >>> cache.init('.mycache/')
    >>> cache.get(key, default=None, mtime=0.0)
    >>> cache.set(key, value)

    :param cache_dir: the directory where cache files are stored.
    :param mode: the file mode wanted for the cache files, default 0600
    """
    
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
        return [os.path.join(self._path, fn) for fn in os.listdir(self._path)
                if not fn.endswith(self._fs_transaction_suffix)]
    
    @classmethod
    def init(self, cache_dir=None, mode=0600):
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


class event:
    
    @classmethod
    def __init__(self):
        pass
    
    @classmethod
    def create(self, what, path):
        log.info("create  '%s', written to %s", what, path)
    
    @classmethod
    def changed(self, what):
        log.info("changed  content of '%s'", what)
    
    @classmethod
    def skip(self, what):
        log.info("skip  '%s' is up to date", what)
