# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import io
from os.path import join, dirname

from acrylamid import log

copy = lambda path: io.open(join(dirname(__file__), path), 'rb')

conf = {
    'sitename': 'A descriptive blog title',
    'author': 'Anonymous',
    'email': 'info@example.com',

    'date_format': '%d.%m.%Y, %H:%M',
    'encoding': 'utf-8',
    'permalink_format': '/:year/:slug/',

    # pagination
    'default_orphans': 0,

    # tag cloud
    'tag_cloud_max_items': 100,
    'tag_cloud_steps': 4,
    'tag_cloud_start_index': 0,
    'tag_cloud_shuffle': False,

    # filter & view configuration
    'filters_dir': [],
    'views_dir': [],

    'filters': ['markdown+codehilite(css_class=highlight)', 'hyphenate'],
    'views': {
    },

    # user dirs
    'output_dir': 'output/',
    'output_ignore': ['.git*', '.hg*', '.svn'],

    'content_dir': 'content/',
    'content_ignore': ['.git*', '.hg*', '.svn'],

    'theme': 'layouts/',
    'theme_ignore': ['.git*', '.hg*', '.svn'],

    'static': None,
    'static_ignore': ['.git*', '.hg*', '.svn'],
    'static_filter': ['Template', 'XML'],

    'engine': 'acrylamid.templates.jinja2.Environment',
}


def normalize(conf):

    if isinstance(conf['static'], list):
        conf['static'] = conf['static'][0]
        log.warn("multiple static directories has been deprecated, " + \
                 "Acrylamid continues with '%s'.", conf['static'])

    for key in 'content_dir', 'theme', 'static', 'output_dir':
        if conf[key] is not None and not conf[key].endswith('/'):
            conf[key] += '/'

    for key in 'views_dir', 'filters_dir':
        if isinstance(conf[key], basestring):
            conf[key] = [conf[key], ]

    return conf
