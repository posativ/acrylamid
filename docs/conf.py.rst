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

Each key-value pair (except views [#]_) is available during :doc:`templating`.
Acrylamid uses `jinja2 <http://jinja.pocoo.org/docs/>`_, see their `Template
Designer Documentation <http://jinja.pocoo.org/docs/templates/>`_ for details.

All the settings identifiers must be set in caps, otherwise they will not be
processed.

Here is a list of settings for acrylamid, regarding the different features.

.. [#] views is a list of all used views, e.g. [index, entry, ...]

Basic settings
--------------

================================================    =====================================================
Variable name (default value)                       Description
================================================    =====================================================
`SITENAME` (``'A descriptive blog title'``)         The name of your blog. It's displayed in the
                                                    <title>-block.
`AUTHOR` (``'Anonymous'``)                          First author of this blog, can be overwritten in
                                                    the entry YAML-header.
`EMAIL` (``'info@example.com'``)                    Your email address -- used in Atom/RSS feeds and as
                                                    contact ability at the bottom in the default layout.
`ENCODING` (``'utf-8'``)                            Default encoding of your text files, only global.
`OUTPUT_IGNORE` (``['style.css', 'img/*']``)        A list of filename/directory-patterns which
                                                    Acrylamid should ignore.
`FILTERS` ( |filter_example|)                       Global list of filters.
`VIEWS` (see example conf.py)                       Dictionary of views set in conf.py.
`WWW_ROOT` (``'http://localhost:8000'``)            Your actual website link where you host this blog.
                                                    It's used to build absolute urls (required for disqus
                                                    and feeds)
================================================    =====================================================

.. |filter_example| replace::

    ``["markdown+codehilite(css_class=highlight)", "hyphenate"]``


URL Settings
------------



================================================    =====================================================
Variable name (default value)                       Description
================================================    =====================================================
`PERMALINK_FORMAT` (``'/:year/:slug/'``)            A substitution string as described here (XXX).
================================================    =====================================================

Date format and locale
----------------------



================================================    =====================================================
Variable name (default value)                       Description
================================================    =====================================================
`LANG`  (``''`` [#]_)                               Default language [#]_ to use -- is important for
                                                    hyphenation patterns XXX: and
                                                    ``meta http-equiv="content-language"``.
`DATE_FORMAT` (``'%d.%m.%Y, %H:%M'``)               This python date-format string is used in
                                                    ``layout/entry.html`` to render the date nicely.
                                                    See `Python's strftime directives
                                                    <http://strftime.org/>`_ for detailed explanation of
                                                    these variables.
`strptime` (``'%d.%m.%Y, %H:%M'``)                  Format to parse the ``date:`` value using
                                                    :func:`time.strptime`. The default matches
                                                    ``23.12.2012, 09:00``, see python's reference
                                                    `strftime <http://strftime.org/>`_
================================================    =====================================================

.. [#] default is the system locale.
.. [#] see `ISO_639 <https://en.wikipedia.org/wiki/ISO_639>`_, if not set the
   system's will be used. If not available, fallback to ``'C'``.

Miscellaneous
-------------

================================================    =====================================================
Variable name (default value)                       Description
================================================    =====================================================
`DISQUS_SHORTNAME` (*not set*)                      Enables `Disqus <https://disqus.com/>`_ integration
                                                    with your site identifier [#]_.
`DEFAULT_ORPHANS` (``0``)                           The minimum number of articles allowed on the last
                                                    page. Use this when you don’t want to have a last
                                                    page with very few articles.
`SUMMARIZE_MODE` (``1``)                            Mode *0* this injects the link to the end of the
                                                    current tag, *1* after some black-listed tags and
                                                    *2* after all tags as standalone tag.
`SUMMARIZE_ELLIPSIS` (``&#8230;``)                  Ellipsis (defaults to three typographical dots, …)
`SUMMARIZE_IDENTIFIER` (``weiterlesen``)            The text inside the continue reading link.
`SUMMARIZE_class` (``continue``)                    CSS-class used in ``<a>``-Tag.
================================================    =====================================================

.. [#] Note, disqus only knows a given URL. If you change the title of an entry
   and you don't setup recirect codes or leave the original url by setting
   ``permalink: /2011/a-title/``, you'll lose your disqus comments for this thread.


Tag cloud
---------

If you want to generate a tag cloud with all your tags, you can do so using the following settings.

================================================    =====================================================
Variable name (default value)                       Description
================================================    =====================================================
`TAG_CLOUD_STEPS` (``4``)                           Count of different font sizes in the tag cloud.
`TAG_CLOUD_MAX_ITEMS` (``100``)                     Maximum number of tags in the cloud.
`TAG_CLOUD_START_INDEX` (``0``)                     Start index of font sizes in the tag cloud.
`TAG_CLOUD_SHUFFLE` (``False``)                     Shuffle tag list.
================================================    =====================================================

The default theme does not support tag clouds, but it is fairly easy to add:

.. code-block:: jinja2

    <ul>
    {% for tag in tag_cloud %}
        <li class="tag-{{ tag.step }}"><a href="/tag/{{ tag.name | safeslug }}/">{{ tag.name }}</a></li>
    {% endfor %}
    </ul>


You should then also define a CSS style with the appropriate classes (tag-0 to tag-N, where N matches TAG_CLOUD_STEPS -1).
