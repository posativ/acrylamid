# -*- encoding: utf-8 -*-
# This is your config file.  Please write in a valid python syntax!
# See http://posativ.org//conf.py.html

TITLE = ('shadow', 'play')

SITENAME = 'A blog subtitle'
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

    '/:slug/': {'view': 'page'},  # static pages
    '/articles/': {'view': 'articles'},
    '/sitemap.xml': {'view': 'sitemap'},

}

THEME = 'shadowplay'
ENGINE = 'acrylamid.templates.jinja2.Environment'

# Tuples are (name, link)
BLOGROLL = [
    ('Acrylamid', 'http://posativ.org/acrylamid/'),
    ('Yet another blogroll', 'http://example.com/')
]
