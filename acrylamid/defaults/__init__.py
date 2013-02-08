# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import io
from os.path import join, dirname

copy = lambda path: io.open(join(dirname(__file__), path), 'rb')

conf = {
    'sitename': 'A descriptive blog title',
    'author': 'Anonymous',
    'email': 'info@example.com',

    'date_format': '%d.%m.%Y, %H:%M',
    'encoding': 'utf-8',
    'permalink_format': '/:year/:slug/',

    'default_orphans': 0,

    'tag_cloud_max_items': 100,
    'tag_cloud_steps': 4,
    'tag_cloud_start_index': 0,

    'filters_dir': [],
    'views_dir': [],
    'output_dir': 'output/',
    'output_ignore': ['.git*', '.hg*', '.svn'],
    'content_dir': 'content/',
    'content_ignore': ['.git*', '.hg*', '.svn'],
    'theme': 'layouts/',
    'theme_ignore': ['.git*', '.hg*', '.svn'],
    'static': [],
    'static_ignore': ['.git*', '.hg*', '.svn'],
    'static_filter': ['HTML', 'XML'],

    'filters': ['markdown+codehilite(css_class=highlight)', 'hyphenate'],
    'views': {
    },

    'engine': 'acrylamid.templates.jinja2.Environment',
}


def normalize(conf):

    for key in 'content_dir', 'theme', 'output_dir':
        if not conf[key].endswith('/'):
            conf[key] += '/'

    for key in 'static', 'views_dir', 'filters_dir':
        if isinstance(conf[key], basestring):
            conf[key] = [conf[key], ]

    return conf
