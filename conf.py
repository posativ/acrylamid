# -*- encoding: utf-8 -*-
# This is your configuration file.  Please write valid python!
# See http://posativ.org/acrylamid/conf.py.html

ENCODING = u'UTF-8'
SITENAME = u'blubee.me the place blubee calls home on the www'
METADESC = u'blubee enjoys doing a lot of stuff, this is where he\'ll ' \
           u'blog about them. From software development, music, art, chinese and much more of course.'
WWW_ROOT = u'http://blubee.me/'
AUTHOR   = u'blubee'
EMAIL    = u'hello@Blubee.me'

FILTERS = [u'markdown+codehilite(pygments_style=default, noclasses=True, css_class=highlight,linenums=True)'
           u'+MathML+delins+sane_lists+footnotes+extra', u'typography', u'smartypants', u'h1', u'jinja2', u'html']

VIEWS = {
    u'/': {u'view': u'page', u'if': lambda e: u'blubee home' in e.title.lower()},

    u'/journal/': {u'filters': u'summarize+62', u'view': u'index', u'pagination': u'/page/:num/',
                   u'items_per_page': 10},

    u'/:slug/': {u'views': [u'entry', u'page'], u'template': u'front-end/post.html'},

    u'/tag/:name/': {u'filters': u'summarize+62', u'view': u'tag', u'pagination': u'/tag/:name/:num/'},

    u'/category/:name/': {u'filters': u'summarize+62', u'view': u'category', u'pagination': u'/category/:name/:num/'},

    u'/atom/': {u'filters': [u'h2', u'nohyphenate'], u'view': u'atom'},
    u'/rss/': {u'filters': [u'h2', u'nohyphenate'], u'view': u'rss'},

    u'/sitemap.xml': {u'view': u'sitemap'},

    u'/video-sitemap.xml': {u'view': u'videoSitemap'},
}
DISQUS_KEY = '---MyDisqusKey---'
DISQUS_SHORTNAME = 'bbme'
VIEWS_DIR += ['views/']
CONTENT_EXTENSION = u'.md'
CONTENT_IGNORE = ['.git*', '.hg*', '.svn', '.D*', '_*']
OUTPUT_IGNORE = ['.git*', '.hg*', '.svn', '.D*', '_*']
THEME_IGNORE = ['.git*', '.hg*', '.svn', '.D*', '_*']
STATIC_IGNORE = ['.git*', '.hg*', '.svn', '.D*', '_*']
THEME = u'theme'
ENGINE = u'acrylamid.templates.jinja2.Environment'
DATE_FORMAT = u'%d.%m.%Y, %H:%M'
SUMMARIZE_LINK = u'<a href=%s class=\'continue\'>continue reading</a>'
DEFAULT_ORPHANS = 0

DEPLOYMENT = {
    'blubee': 'rsync -rtuvz --delete $OUTPUT_DIR root@http://blubee.me:/var/www/blubee',
}