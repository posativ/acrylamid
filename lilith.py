#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# TODO:
# - callback after rendering, but before write to file (e.g. tidy)
# - use file ext for markup, if #parser not specifed

VERSION = "0.1-dev"
VERSION_SPLIT = tuple(VERSION.split('-')[0].split('.'))

import sys
reload(sys); sys.setdefaultencoding('utf-8')

import os
import re
import locale
import time
from datetime import datetime

import yaml
import extensions
import tools
from tools import FileEntry

from shpaml import convert_text
from jinja2 import Template

class Lilith:
    """Main class for Lilith functionality.  It handles initialization,
    defines default behavior, and also pushes the request through all
    steps until the output is rendered and we're complete."""
    
    def __init__(self, config, environ, data=None):
        """Sets configuration and environment and creates the Request
        object
        
        config -- dict containing the configuration variables
        environ -- dict containing the environment variables
        """
        
        config['lilith_name'] = "lilith"
        config['lilith_version'] = VERSION
        
        self._config = config
        self._data = data
        self.request = Request(config, environ, data)
        
    def initialize(self):
        """The initialize step further initializes the Request by
        setting additional information in the ``data`` dict,
        registering plugins, and entryparsers.
        """
        data = self._data
        config = self._config

        # initialize the locale, if wanted (will silently fail if locale
        # is not available)
        if config.get('lang', None):
            try:
                locale.setlocale(locale.LC_ALL, config['lang'])
            except locale.Error:
                # invalid locale
                pass

        config['www_root'] = config.get('www_root', '')

        # take off the trailing slash for base_url
        if config['www_root'].endswith("/"):
            config['www_root'] = config['www_root'][:-1]

        # import and initialize plugins
        extensions.initialize(config.get("ext_dir", ['ext', ]),
                              exclude=config.get("ext_ignore", []))

        # entryparser callback is run here first to allow other
        # plugins register what file extensions can be used
    
    def run(self):
        """This is the main loop for lilith.  This method will run
        the handle callback to allow registered handlers to handle
        the request. If nothing handles the request, then we use the
        ``_lilith_handler``.
        """
        
        self.initialize()
        
        # run the start callback
        request = tools.run_callback('start', self.request)
        
        # run the default handler
        request = tools.run_callback("handle",
                        request,
                        mapping=lambda x,y:x,
                        defaultfunc=_lilith_handler)
                
        # do end callback
        print request
        request = tools.run_callback('end', request)

            
class Request(object):
    """This class holds the lilith request.  It holds configuration
    information, OS environment, and data that we calculate and
    transform over the course of execution."""
    
    def __init__(self, config, environ, data):
        """Sets configuration and environment.
        
        Arguments:
        config: dict containing configuration variables
        environ: dict containing environment variables
        adata: dict containing data variables"""
        
        self._data = data
        self._config = config
        self._environ = environ

def _lilith_handler(request):
    """This is the default lilith handler.
        - cb_filelist
        - cb_filestat
        - cb_sortlist
        - cb_entryparser
            - cb_preformat
            - cb_format
            - cb_postformat
        - cb_prepare
    """
    
    config = request._config
    data = request._data
                       
    # call the filelist callback to generate a list of entries
    request =  tools.run_callback(
            "filelist",
            request,
            defaultfunc=_filelist)
        
    # chance to modify specific meta data e.g. datetime
    request = tools.run_callback(
            'filestat', 
            request,
            defaultfunc=_filestat)
    
    # use datetime to sort chronological
    request = tools.run_callback(
            'sortlist', 
            request,
            defaultfunc=_sortlist)
            
    for i,entry in enumerate(request._data['entry_list']):
        request._data['entry_list'][i] = tools.run_callback(
                'entryparser',
                {'entry': entry, 'config': request._config},
                defaultfunc=_entryparser)
    
    # last modifications
    request = _prepare(request)
            
    from copy import deepcopy # performance? :S
    
    tools.run_callback('item', deepcopy(request),
                    mapping=lambda x,y: y,
                    defaultfunc=_item)
    
    tools.run_callback('page', deepcopy(request),
                    mapping=lambda x,y: y,
                    defaultfunc=_page)
    
    return request

def _filelist(request):
    """This is the default handler for getting entries.  It takes the
    request object in and figures out which entries bases on the default
    behavior that we want to show and generates a list of EntryBase
    subclass objects which it returns.
    
    Arguments:
    args -- dict containing the incoming Request object
    
    Returns the content we want to render"""
    
    data = request._data
    config = request._config
    
    filelist = []
    for root, dirs, files in os.walk(config.get('entries_dir', 'content')):
        filelist += [ os.path.join(root, file) for file in files
                         if root not in ['content/drafts', ] ]
    
    entry_list = [FileEntry(request, e, config['entries_dir']) for e in filelist]
    data['entry_list'] = entry_list
    
    return request
    
def _filestat(request):
    """Sets an alternative timestamp specified in yaml header."""
    
    config = request._config
    
    entry_list = request._data['entry_list']
    for i in range(len(entry_list)):
        if entry_list[i].has_key('date'):
            timestamp = time.strptime(entry_list[i]['date'],
                                config.get('strptime', '%d.%m.%Y, %H:%M'))
            timestamp = time.mktime(timestamp)
            entry_list[i].date = datetime.utcfromtimestamp(timestamp)
        else:
            entry_list[i]['date'] = entry_list[i]._date
    return request
    
def _sortlist(request):
    """sort list by date"""

    entry_list = request._data['entry_list']
    entry_list.sort(key=lambda k: k.date, reverse=True)
    return request

def _format(args):
    """Apply markup using Post.parser."""
    entry = args['entry']
    config = args['config']
    
    parser = entry.get('parser', config.get('parser', 'plain'))
    
    if parser.lower() in ['markdown', 'mkdown', 'md']:
        from markdown import markdown
        return markdown(entry['body'],
                        extensions=['codehilite(css_class=highlight)'])
    
    elif parser.lower() in ['restructuredtest', 'rst', 'rest']:                
        from docutils import nodes
        from docutils.parsers.rst import directives, Directive
        from docutils.core import publish_parts
        
        # Set to True if you want inline CSS styles instead of classes
        INLINESTYLES = False
        
        from pygments.formatters import HtmlFormatter
        
        # The default formatter
        DEFAULT = HtmlFormatter(noclasses=INLINESTYLES)
        
        
        from docutils import nodes
        from docutils.parsers.rst import directives, Directive
        
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name, TextLexer
        
        class Pygments(Directive):
            """ Source code syntax hightlighting.
            """
            required_arguments = 1
            optional_arguments = 0
            final_argument_whitespace = True
            option_spec = dict([(key, directives.flag) for key in {}])
            has_content = True
    
            def run(self):
                self.assert_has_content()
                try:
                    lexer = get_lexer_by_name(self.arguments[0])
                except ValueError:
                    # no lexer found - use the text one instead of an exception
                    lexer = TextLexer()
                # take an arbitrary option if more than one is given
                formatter = self.options and VARIANTS[self.options.keys()[0]] or DEFAULT
                parsed = highlight(u'\n'.join(self.content), lexer, formatter)
                return [nodes.raw('', parsed, format='html')]
        
        directives.register_directive('sourcecode', Pygments)
        initial_header_level = 1
        transform_doctitle = 0
        settings = {
            'initial_header_level': initial_header_level,
            'doctitle_xform': transform_doctitle
            }
        parts = publish_parts(
            entry['body'], writer_name='html', settings_overrides=settings)
        return parts['body'].encode('utf-8')
        
    else:
        return entry['body']
    
def _entryparser(args):
    """Applies:
        - cb_preformat
        - cb_format
        - cb_postformat"""
    
    entry = args['entry']
    config = args['config']
    
    entry['body'] = tools.run_callback(
            'preformat',
            {'entry': entry, 'config': config},
            defaultfunc=lambda x: ''.join(x['entry']['story']))

    entry['body'] = tools.run_callback(
            'format',
            {'entry': entry, 'config': config},
            mapping=lambda x,y: y,
            defaultfunc=_format)
    
    entry['body'] = tools.run_callback(
            'postformat',
            {'entry': entry, 'config': config},
            mapping=lambda x,y: y,
            defaultfunc=lambda x: x['entry']['body'])
    
    return entry

def _prepare(request):
    """Sets a few required keys in FileEntry.
    
    required:
    safe_title -- used as directory name
    url -- permalink
    id -- atom conform id: http://diveintomark.org/archives/2004/05/28/howto-atom-id
    """
    
    config = request._config
    data = request._data
    for i, entry in enumerate(data['entry_list']):
        safe_title = re.sub('[\W]+', '-', entry['title'], re.U).lower().strip('-')
        url = config.get('www_root', '') + '/' \
              + str(entry.date.year) + '/' + safe_title + '/'
        id = 'tag:' + config.get('www_root', '').replace('http://', '').strip('/') \
             + ',' + entry.date.strftime('%Y-%m-%d') + ':' \
             + '/' + str(entry.date.year) +  '/' + safe_title
        data['entry_list'][i]['safe_title'] = safe_title
        data['entry_list'][i]['url'] = url
        data['entry_list'][i]['id'] = id
        
    return request
    
def _item(request):
    """Creates single full-length entry.  Looks like
    http://yourblog.org/year/title/(index.html).
    
    required:
    entry.html -- layout of Post's entry
    main.html -- layout of the website
    """
    config = request._config
    data = request._data
    data['type'] = 'item'
    
    layout = config.get('layout_dir', 'layouts')
    tt_entry = Template(open(os.path.join(layout, 'entry.html')).read())
    tt_main = Template(open(os.path.join(layout, 'main.html')).read())

    # last preparations
    request = tools.run_callback(
                'prepare',
                request)
    
    dict = request._config
    entry_list = []
    
    for entry in data['entry_list']:
        entrydict = dict.copy()
        entrydict.update({'Post': entry})
        dict.update({'entry_list':tt_entry.render(entrydict) })
        html = tt_main.render( dict )
        
        directory = os.path.join(config.get('output_dir', 'out'),
                         str(entry.date.year),
                         entry.safe_title)
        path = os.path.join(directory, 'index.html')
        tools.mk_file(html, entry, path)
        
    return request

def _page(request):
    """Creates nicely paged listing of your posts.  First “Page” is the
    index.hml used to have this nice url: http://yourblog.com/ with a recent
    list of your (e.g. summarized) Posts. Other pages are enumerated to /page/n+1
    
    required:
    items_per_page -- posts displayed per page (defaults to 6)
    entry.html -- layout of Post's entry
    main.html -- layout of the website
    """
    config = request._config
    data = request._data
    data['type'] = 'page'
    ipp = config.get('items_per_page', 6)
    
    # last preparations
    request = tools.run_callback(
                'prepare',
                request)
    
    layout = config.get('layout_dir', 'layouts')
    tt_entry = Template(open(os.path.join(layout, 'entry.html')).read())
    tt_main = Template(open(os.path.join(layout, 'main.html')).read())
    
    dict = request._config
    entry_list = []
    for entry in data['entry_list']:
        entrydict = dict.copy()
        entrydict.update({'Post': entry})
        entry_list.append(tt_entry.render(entrydict))
                
    for i, mem in enumerate([entry_list[x*ipp:(x+1)*ipp] for x in range(len(entry_list)/ipp+1)]):
        
        dict.update( {'entry_list': '\n'.join(mem), 'page': i+1,
                      'num_entries': len(entry_list)} )
        html = tt_main.render( dict )
        directory = os.path.join(config.get('output_dir', 'out'),
                         '' if i == 0 else 'page/%s' % (i+1))
        path = os.path.join(directory, 'index.html')
        tools.mk_file(html, {'title': 'page/%s' % (i+1)}, path)
        
    return request

if __name__ == '__main__':
    
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-c", "--config-file", dest="conf", metavar="FILE",
                      help="an alternative conf to use", default="lilith.conf")
    #parser.add_option("-o", "--overwrite", dest="force",
    #                  help="force overwrite", default=False)
    parser.add_option("-l", "--layout_dir", dest="layout", metavar="DIR",
                      help="force overwrite", default=False)
    
    (options, args) = parser.parse_args()
    
    conf = yaml.load(open(options.conf).read())
    if options.layout:
        conf['layout_dir'] = options.layout
    assert tools.check_conf(conf)
    l = Lilith(config=conf, environ={}, data={})
    l.run()
