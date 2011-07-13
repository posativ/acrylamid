#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import yaml
from datetime import datetime
from os.path import join, exists, getmtime, dirname
from time import gmtime
import logging

import extensions

log = logging.getLogger('lilith.tools')

def run_callback(chain, input, mapping=lambda x,y: y, defaultfunc=lambda x: x):
    """Applies defaultfunc to input and additional every function in chain.
    
    Should return neither the modifed or the unmodified output. But
    since we have a lot of cross-references here, this is currently
    NOT possible (but implemented using mapping, though).
    """
    
    if not callable(defaultfunc):
        raise TypeError('defaultfunc must be callable')

    chain = extensions.get_callback_chain(chain)

    if chain:
        for func in chain:
            log.debug('%s.%s' % (func.__module__, func.func_name))
            output = func(input)
            input = mapping(input, output)
    
    log.debug('%s.%s' % (defaultfunc.__module__, defaultfunc.func_name))
    return defaultfunc(input)

class FileEntry:
    """This class gets it's data and metadata from the file specified
    by the filename argument"""
    
    def __init__(self, request, filename, datadir=''):
        """Arguments:
        request -- the Request object
        filename -- the complete filename including path
        datadir --  the data dir
        """
        self._config = request._config
        self._filename = filename.replace(os.sep, '/')
        self._datadir = datadir
        
        self._date = datetime.utcfromtimestamp(os.path.getmtime(filename))
        self._populate()
        
    def __repr__(self):
        return "<fileentry f'%s'>" % (self._filename)
        
    def __contains__(self, key):
        return True if key in self.__dict__.keys() else False

    def __getitem__(self, key, default=None):
        if key in self:
            return self.__dict__[key]
        else:
            return default
        
    def __setitem__(self, key, value):
        """Set metadata.  No underscore in front of `key` is allowed!"""
        if key.find('_') == 0:
            raise ValueError('invalid metadata variable: %s' % key)
        self.__dict__[key] = value
        
    def keys(self):
        return self.__dict__.keys()
        
    def has_key(self, key):
        return self.__contains__(key)
    
    def iteritems(self):
        for key in self.keys():
            yield (key, self[key])
        
    get = __getitem__

    def _populate(self):
        """Populates the yaml header and splits the content.  """
        f = open(self._filename, 'r')
        lines = f.readlines()
        f.close()
        
        data = {}
    
        # if file is empty, return a blank entry data object
        if len(lines) == 0:
            data['title'] = ''
            data['story'] = []
        else:
            lines.pop(0) # first `---`
            meta = []
            for i, line in enumerate(lines):
                if line.find('---') == 0:
                    break
                meta.append(line)
            lines.pop(0) # last `---`            

            for key, value in yaml.load(''.join(meta)).iteritems():
                data[key] = value

            # optional newline after yaml header
            lines = lines[i:] if lines[i].strip() else lines[i+1:]

            # call the preformat function
            data['parser'] = data.get('parser', self._config.get('parser', 'plain'))
            data['story'] = lines
        
            for key, value in data.iteritems():
                self[key] = value

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

def mk_file(content, entry, path, force=False):
    """Creates entry in filesystem. Overwrite only if content
    differs.
    
    Arguments:
    content -- rendered html
    entry -- FileEntry object
    path -- path to write
    force -- force overwrite, even nothing has changed (defaults to `False`)
    """
    
    if exists(dirname(path)) and exists(path):
        old = open(path).read()
        if content == old and not force:
            log.debug("'%s' is up to date" % entry['title'])
        else:
            f = open(path, 'w')
            f.write(content)
            f.close()
            log.info("Content of '%s' has changed" % entry['title'])
    else:
        try:
            os.makedirs(dirname(path))
        except OSError:
            # dir already exists (mostly)
            pass
        f = open(path, 'w')
        f.write(content)
        f.close()
        log.info("'%s' written to %s" % (entry['title'], path))