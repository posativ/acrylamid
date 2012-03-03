Configuration
=============

Acrylamid's configuration is read from ``conf.py`` inside your current working
dir. If a given value is not set it will be derived from *acrylamid.defaults*.

A basic configuration looks like this (This file is directly executed as
python script and therefore must be valid python code!):

::

    # -*- encoding: utf-8 -*-
    # This is your config file.  Please write in a valid python syntax!
    # See http://acrylamid.readthedocs.org/en/latest/conf.py.html

    SITENAME = "A descriptive blog title"
    WWW_ROOT = "http://example.com/"

    AUTHOR = "Anonymous"
    EMAIL = "info@example.org"

    FILTERS = ["markdown+codehilite(css_class=highlight)", "hyphenate"]
    VIEWS = {
        "/": {"filters": ["summarize", "h1"],
              "pagination": "/page/:num",
              "view": "index"},
        "/:year/:slug/": {"filters": ["h1"], "view": "entry"},
        "/atom/": {"filters": ["h2"], "view": "atom"},
        "/rss/": {"filters": ["h2"], "view": "rss"},
        "/articles/": {"view": "articles"},
        #"/atom/full": {"filters": ["h2"], "view": "atom", "num_entries": 1000},
        "/tag/:name/": {"filters": ["h1", "summarize"], "view":"tag",
                       "pagination": "/tag/:name/:num"},
        }

    PERMALINK_FORMAT = "/:year/:slug/index.html"
    DATE_FORMAT = "%d.%m.%Y, %H:%M"

Each key-value pair (except views[1]_) is available during :doc:`templating`.
Acrylamid uses `jinja2 <http://jinja.pocoo.org/docs/>`_, see their `Template
Designer Documentation <http://jinja.pocoo.org/docs/templates/>`_ for details.

All the settings identifiers must be set in caps, otherwise they will not be
processed.

Here is a list of settings for acrylamid, regarding the different features.

.. [1] ``views`` is a list of all used views, e.g. [index, entry, ...]

==============

================================================    =====================================================
Setting name (default value)                        what does it do?
================================================    =====================================================
`SITENAME` (``''``)                                 base URL of your website. This is also the way
                                                    to tell acrylamid to use a sub-uri (all relative,
                                                    though)
`AUTHOR`                                            default author (put your name)
`CLEAN_URL` (``False``)                             If set to `True`, the URLs will not be suffixed by
                                                    `.html`, so you will have to setup URL rewriting on 
                                                    your web server.
`DATE_FORMATS` (``{}``)                             If you do manage multiple languages, you can
                                                    set the date formatting here.
`DEFAULT_CATEGORY` (``'misc'``)                     The default category to fallback on.
`DEFAULT_DATE_FORMAT` (``'%a %d %B %Y'``)           The default date format you want to use.
`DISPLAY_PAGES_ON_MENU` (``True``)                  Display or not the pages on the menu of the
                                                    template. Templates can follow or not this
                                                    settings.
`FALLBACK_ON_FS_DATE` (``True``)                    If True, pelican will use the file system
                                                    dates infos (mtime) if it can't get
                                                    informations from the metadata
`JINJA_EXTENSIONS` (``[]``)                         A list of any Jinja2 extensions you want to use.
`DELETE_OUTPUT_DIRECTORY` (``False``)               Delete the output directory and just
                                                    the generated files.
`LOCALE` (''[1]_)                                   Change the locale. A list of locales can be provided 
                                                    here or a single string representing one locale.
                                                    When providing a list, all the locales will be tried 
                                                    until one works.
`MARKUP` (``('rst', 'md')``)                        A list of available markup languages you want
                                                    to use. For the moment, only available values
                                                    are `rst` and `md`.
`MD_EXTENSIONS` (``('codehilite','extra')``)        A list of the extensions that the markdown processor
                                                    will use. Refer to the extensions chapter in the
                                                    Python-Markdown documentation for a complete list of
                                                    supported extensions.
`OUTPUT_PATH` (``'output/'``)                       Where to output the generated files.
`PATH` (``None``)                                   path to look at for input files.
`PDF_GENERATOR` (``False``)                         Set to True if you want to have PDF versions
                                                    of your documents. You will need to install
                                                    `rst2pdf`.
`RELATIVE_URLS` (``True``)                          Defines if pelican should use relative urls or
                                                    not.
`SITENAME` (``'A Pelican Blog'``)                   Your site name
`SITEURL`                                           
`STATIC_PATHS` (``['images']``)                     The static paths you want to have accessible
                                                    on the output path "static". By default,
                                                    pelican will copy the 'images' folder to the
                                                    output folder.
`TIMEZONE`                                          The timezone used in the date information, to
                                                    generate atom and rss feeds. See the "timezone"
                                                    section below for more info.
================================================    =====================================================

This is a complete list of all configuration keys available in acrylamid.

blog_title
    The blog's title
author
    the author's name. Can be overwritten in a given entry's YAML header and
    is then available in this ``entry.html`` template.
website
    defaults to www_root but may changed to link to a different website in
    feeds.
www_root
    the root-url where you host this blog. It's used to build absolute urls
    (required for disqus and feeds)
lang
    your language code, see
    `ISO_639 <https://en.wikipedia.org/wiki/ISO_639>`_, if not set the
    system's will be used. If not available, fallback to ``'C'``.
strptime
    the parsing format of your ``date:`` key-value pair. Defaults to
    ``%d.%m.%Y, %H:%M`` and matches 23.12.2012, 09:00, see
    python's reference `strftime <http://strftime.org/>`_
disqus_shortname
    username for `Disqus <http://disqus.com/>`_ integration. Note, disqus only
    knows a given URL. If you change a entry-title and you don't setup
    recirect codes or leave the original url by setting ``permalink:
    /2011/a-title/``, you'll lose your disqus comments for this thread.

control-flow statements
***********************

A key beginning with ``views.`` or ``filters.`` (including the dot) is removed
from YAML parsing and directly injected into the given namespace. Therefore
you can add global filters, per-view filters, disable views and/or customize
settings for views or filters.

views.filters
    a pythonic list of globally applied filters. See
    `filters.rst </posativ/acrylamid/blob/master/docs/filters.rst>`_
    for syntax specifications.
views.$myview.filters
    a list of per-view applied filters. You may also disable global filters by
    *no*-prefixing filters e.g. ``nosummarize``.
views.$myview.property
    change given property from view
