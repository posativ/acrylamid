# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

conf = {
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

    'filters': ['markdown+codehilite(css_class=highlight)', 'hyphenate'],
    'views': {
    },

    'engine': 'acrylamid.templates.jinja2.Environment'
}
