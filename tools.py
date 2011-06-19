#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import yaml
from datetime import datetime
from os.path import join, exists, getmtime, dirname
from time import gmtime

import extensions

def run_callback(chain, input,
                 mappingfunc=lambda x, y: x,
                 donefunc=lambda x: 0,
                 defaultfunc=None):
    """
    Executes a callback chain on a given piece of data.  passed in is
    a dict of name/value pairs.  Consult the documentation for the
    specific callback chain you're executing.

    Callback chains should conform to their documented behavior.  This
    function allows us to do transforms on data, handling data, and
    also callbacks.

    The difference in behavior is affected by the mappingfunc passed
    in which converts the output of a given function in the chain to
    the input for the next function.

    If this is confusing, read through the code for this function.

    Returns the transformed input dict.

    :param chain: the name of the callback chain to run

    :param input: dict with name/value pairs that gets passed as the
                  args dict to all callback functions

    :param mappingfunc: the function that maps output arguments to
                        input arguments for the next iteration.  It
                        must take two arguments: the original dict and
                        the return from the previous function.  It
                        defaults to returning the original dict.

    :param donefunc: this function tests whether we're done doing what
                     we're doing.  This function takes as input the
                     output of the most recent iteration.  If this
                     function returns True then we'll drop out of the
                     loop.  For example, if you wanted a callback to
                     stop running when one of the registered functions
                     returned a 1, then you would pass in:
                     ``donefunc=lambda x: x`` .

    :param defaultfunc: if this is set and we finish going through all
                        the functions in the chain and none of them
                        have returned something that satisfies the
                        donefunc, then we'll execute the defaultfunc
                        with the latest version of the input dict.

    :returns: varies
    """
    chain = extensions.get_callback_chain(chain)

    output = None

    for func in chain:
        # we call the function with the input dict it returns an
        # output.
        output = func(input)

        # we fun the output through our donefunc to see if we should
        # stop iterating through the loop.  if the donefunc returns
        # something true, then we're all done; otherwise we continue.
        if donefunc(output):
            break

        # we pass the input we just used and the output we just got
        # into the mappingfunc which will give us the input for the
        # next iteration.  in most cases, this consists of either
        # returning the old input or the old output--depending on
        # whether we're transforming the data through the chain or
        # not.
        input = mappingfunc(input, output)

    # if we have a defaultfunc and we haven't satisfied the donefunc
    # conditions, then we return whatever the defaultfunc returns when
    # given the current version of the input.
    if callable(defaultfunc) and not donefunc(output):
        return defaultfunc(input)

    # we didn't call the defaultfunc--so we return the most recent
    # output.
    return output

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
                    raise OSError('[ERROR] %s has to be a directory' % value)
            else:
                os.mkdir(value)
                print '[WARNING]: %s created...' % value
                
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
            print "[INFO] '%s' is up to date" % entry['title']
        else:
            f = open(path, 'w')
            f.write(content)
            f.close()
            print "[INFO] Content of '%s' has changed" % entry['title']
    else:
        try:
            os.makedirs(dirname(path))
        except OSError:
            # dir already exists (mostly)
            pass
        f = open(path, 'w')
        f.write(content)
        f.close()
        print "[INFO] '%s' written to %s" % (entry['title'], path)