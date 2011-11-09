#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see lilith.py

import sys, os, re
import yaml
from datetime import datetime
from os.path import join, exists, getmtime, dirname
from time import gmtime
import logging

log = logging.getLogger('lilith.utils')
_slug_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

try:
    import translitcodec
except ImportError:
    import unicodedata
    from string import maketrans
    from unicodedata import normalize
    translitcodec = None
    log.debug("no 'translitcodec' found, using NFKD algorithm")


class FileEntry:
    """This class gets it's data and metadata from the file specified
    by the filename argument"""
    
    # TODO: remap internally
    __map__ = {'tag': 'tags', 'filter': 'filters'}
    __keys__ = ['permalink', 'filters', 'author', 'draft', 'tags', 'date', 'title', 'content']
    
    title = content = ''
    draft = False
    permalink = None
    tags = filters = []
    
    def __init__(self, filename, new=True):
        """Arguments:
        request -- the Request object
        filename -- the complete filename including path
        datadir --  the data dir"""
        
        self.date = datetime.fromtimestamp(os.path.getmtime(filename))
        self.filename = filename
        self.parse()
        
    def __repr__(self):
        return "<fileentry f'%s'>" % (self.filename)
        
    @property
    def extension(self):
        return os.path.splitext(self.filename)[1][1:]
        
    @property
    def source(self):
        with file(self.filename, 'r') as f:
            return unicode(''.join(f.readlines()[self._i:]).strip())
            
    @property
    def slug(self):
        """Generates an ASCII-only slug.  Borrowed from
        http://flask.pocoo.org/snippets/5/"""

        result = []
        for word in _slug_re.split(self.title.lower()):
            if translitcodec:
                word = word.encode('translit/long')
            else:
                word = normalize('NFKD', word).encode('ascii', 'ignore')
            if word and not word[0] in '-:':
                result.append(word)
        return unicode('-'.join(result))
        
    @property
    def permalink(self):
        # TODO: fix hard-coded slug
        return expand('/:year/:slug/', self)
        
    def get(self, key, default=None):
        return self.__dict__.get(key, default)
        
    def parse(self):
        """parsing yaml header and remember when content begins."""
        
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
        for key, value in yaml.load(''.join(meta)).iteritems():
            if not hasattr(self, key):
                self.__dict__[key] = value
            elif key in self.__keys__:
                if isinstance(value, basestring):
                    self.__dict__[key] = unicode(value)
                else:
                    self.__dict__[key] = value
                    
    def keys(self):
        return filter(lambda k: hasattr(self, k), self.__keys__)
        
    def __getitem__(self, key):
        if key in self.__map__:
            return self.__dict__[self.__map__[key]]
        elif key in self.__keys__:
            return getattr(self, key)
        else:
            raise KeyError("%s has no such attribute '%s'" % (self, key))
            


class ColorFormatter(logging.Formatter):
    """Implements basic colored output using ANSI escape codes."""

    # -- and BOLD
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
                    'update': self.YELLOW, 'change': self.YELLOW}
                    
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
    """Creates entry in filesystem. Overwrite only if content
    differs.

    Arguments:
    content -- rendered html
    entry -- FileEntry object
    path -- path to write
    force -- force overwrite, even nothing has changed (defaults to `False`)
    """

    if exists(dirname(path)) and exists(path):
        with file(path) as f:
            old = f.read()
        if content == old and not force:
            log.info("skip  '%s' is up to date" % entry['title'])
        else:
            f = open(path, 'w')
            f.write(content)
            f.close()
            log.info("changed  content of '%s'" % entry['title'])
    else:
        try:
            os.makedirs(dirname(path))
        except OSError:
            # dir already exists (mostly)
            pass
        f = open(path, 'w')
        f.write(content)
        f.close()
        log.info("create  '%s', written to %s" % (entry['title'], path))

    
def expand(url, entry):
    m = {':year': str(entry.date.year), ':month': str(entry.date.month),
         ':day': str(entry.date.day), ':slug': entry.slug}
    
    for val in m:
        url = url.replace(val, m[val])
    return url


def joinurl(*args):
    """joins multiple urls to one single domain without loosing root (first element)"""
    
    r = []
    for i, mem in enumerate(args):
        mem = mem.rstrip('/') if i==0 else mem.strip('/')
        r.append(mem)
    
    return join(*r)
