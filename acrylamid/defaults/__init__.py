# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from __future__ import unicode_literals

import sys
import os
import io
import shutil
import logging

from os.path import exists, isfile, isdir, join, dirname, basename

log = logging.getLogger('acrylamid.defaults')


def same(f, o):
    """Check whether two files are the same."""

    fp = io.open(f, 'rb')
    op = io.open(o, 'rb')

    while True:
        c, k = fp.read(128), op.read(128)
        if not c or not k:
            break
        if c != k:
            break


def init(root, theme='html5', engine='jinja2', overwrite=False):
    """Subcommand: init -- creates the base structure of an Acrylamid blog
    or restores individual files."""

    def create(directory, path):
        """A shortcut for check if exists and shutil.copy to."""

        dest = join(root, directory, basename(path))
        if not isfile(dest) or overwrite == True:
            try:
                shutil.copy(path, dest)
                log.info('create  %s', dest)
            except IOError as e:
                log.fatal(e.args[0])

        else:
            log.info('skip  %s already exists', dest)

    global default

    default['output_dir'] = default['output_dir'].rstrip('/')
    default['content_dir'] = default['content_dir'].rstrip('/')
    default['layout_dir'] = default['layout_dir'].rstrip('/')

    dirs = ['%(content_dir)s/', '%(layout_dir)s/', '%(output_dir)s/', '.cache/']

    files = [p % {'engine': engine, 'theme': theme} for p in [
        '%(engine)s/%(theme)s/base.html', '%(engine)s/%(theme)s/main.html',
        '%(engine)s/%(theme)s/entry.html', '%(engine)s/%(theme)s/articles.html',
        '%(engine)s/rss.xml', '%(engine)s/atom.xml',
        'misc/%(theme)s/style.css', 'misc/sample-entry.txt']]
    files = [join(dirname(__file__), path) for path in files]

    # restore a given file from defaults
    # XXX restore folders, too
    if filter(lambda p: basename(p) == basename(root), files):

        for path in files:
            if basename(path) == basename(root):
                break
        if isfile(root):
            if same(path) == same(root):
                log.info('skip  %s is identical', root)
                sys.exit(0)
            if overwrite or raw_input('re-initialize %r? [yn]: ' % root) == 'y':
                shutil.copy(path, root)
                log.info('re-initialized %s' % root)
        else:
            shutil.copy(path, root)
            log.info('create %s' % root)
        sys.exit(0)

    config = confstring + '''
TT = 'acrylamid.templates.%s.Environment'
''' % engine

    # re-initialize conf.py
    if root == 'conf.py':
        if overwrite or raw_input('re-initialize %r? [yn]: ' % root) == 'y':
            with io.open('conf.py', 'w') as fp:
                fp.write(config)
            log.info('re-initialized %s' % root)
        sys.exit(0)

    # YO DAWG I HERD U LIEK BLOGS SO WE PUT A BLOG IN UR BLOG -- ask user before
    if isfile('conf.py') and not overwrite:
        q = raw_input("Create blog inside a blog? [yn]: ")
        if q != 'y':
            sys.exit(1)

    if exists(root) and len(os.listdir(root)) > 0 and not overwrite:
        if raw_input("Destination directory not empty! Continue? [yn]: ") != 'y':
            sys.exit(1)

    if root != '.' and not exists(root):
        os.mkdir(root)

    for directory in dirs:
        directory = join(root, directory % default)
        if exists(directory) and not isdir(directory):
            log.critical('Unable to create %r. Please remove this file', directory)
            sys.exit(1)
        elif not exists(directory):
            os.mkdir(directory)

    with io.open(join(root, 'conf.py'), 'w') as fp:
        fp.write(config)
        log.info('create  %s', join(root, 'conf.py'))

    for path in files:
        if filter(lambda k: path.endswith(k), ('.html', '.xml')):
            create(default['layout_dir'], path)
        elif path.endswith('.txt'):
            create(default['content_dir'], path)
        else:
            create(default['output_dir'], path)

    log.info('Created your fresh new blog at %r. Enjoy!', root)


def check_conf(conf):
    """Rudimentary conf checking.  Currently every *_dir except
    `ext_dir` (it's a list of dirs) is checked whether it exists."""

    def check(value):
        if os.path.exists(value):
            if os.path.isdir(value):
                pass
            else:
                log.error("'%s' must be a directory" % value)
                sys.exit(1)
        else:
            os.mkdir(value)
            log.warning('%s created...' % value)

    # directories
    for key, value in conf.iteritems():
        if key.endswith('_dir'):
            if isinstance(value, list) or isinstance(value, tuple):
                for subkey in value:
                    check(subkey)
            else:
                check(value)

    return True


conf = default = {
    'sitename': 'A descriptive blog title',
    'author': 'Anonymous',
    'email': 'info@example.com',

    'date_format': '%d.%m.%Y, %H:%M',
    'encoding': 'utf-8',
    'permalink_format': '/:year/:slug/',
    'output_ignore': ['/style.css', '/images/*', '.git/'],

    'default_orphans': 0,

    'tag_cloud_max_items': 100,
    'tag_cloud_steps': 4,
    'tag_cloud_start_index': 0,

    'filters_dir': [],
    'views_dir': [],
    'content_dir': 'content/',
    'layout_dir': 'layouts/',
    'output_dir': 'output/',

    'filters_ignore': [],
    'filters_include': [],

    'filters': ['markdown+codehilite(css_class=highlight)', 'hyphenate'],
    'views': {
    },

    'tt': 'acrylamid.templates.jinja2.Environment',
}


confstring = """
# -*- encoding: utf-8 -*-
# This is your config file.  Please write in a valid python syntax!
# See http://acrylamid.readthedocs.org/en/latest/conf.py.html

SITENAME = 'A descriptive blog title'
WWW_ROOT = 'http://example.com/'

AUTHOR = 'Anonymous'
EMAIL = 'mail@example.com'

FILTERS = ['markdown+codehilite(css_class=highlight)', 'hyphenate', 'h1']
VIEWS = {
    '/': {'filters': 'summarize', 'view': 'index',
          'pagination': '/page/:num'},

    '/:year/:slug/': {'view': 'entry'},

    '/tag/:name/': {'filters': 'summarize', 'view':'tag',
                    'pagination': '/tag/:name/:num'},

    '/atom/': {'filters': ['h2', 'nohyphenate'], 'view': 'atom'},
    '/rss/': {'filters': ['h2', 'nohyphenate'], 'view': 'rss'},

    '/articles/': {'view': 'articles'},

    '/sitemap.xml': {'view': 'sitemap'},

    # Here are some more examples

    # # '/atom/full/' will give you a _complete_ feed of all your entries
    # '/atom/full/': {'filters': 'h2', 'view': 'atom', 'num_entries': 1000},

    # # a feed containing all entries tagges with 'python'
    # '/rss/python/': {'filters': 'h2', 'view': 'rss',
    #                  'if': lambda e: 'python' in e.tags}

    # # a full typography features entry including MathML and Footnotes
    # '/:year/:slug': {'filters': ['typography', 'Markdown+Footnotes+MathML'],
    #                  'view': 'entry'}
}

PERMALINK_FORMAT = '/:year/:slug/index.html'
DATE_FORMAT = '%d.%m.%Y, %H:%M'
""".strip()
