Configuration
=============

Acrylamid's configuration is read from ``conf.py`` inside your current working
dir. If a given value is not set it will be derived from *acrylamid.defaults*.

A basic configuration looks like this (This file is directly executed as
python script and therefore must be valid python code!):

.. code-block:: python

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
    }

    PERMALINK_FORMAT = '/:year/:slug/index.html'
    DATE_FORMAT = '%d.%m.%Y, %H:%M'

Each key-value pair (except views [#]_) is available during :doc:`templating`.
Acrylamid uses `jinja2 <http://jinja.pocoo.org/docs/>`_, see their `Template
Designer Documentation <http://jinja.pocoo.org/docs/templates/>`_ for details.

All the settings identifiers must be set in caps, otherwise they will not be
processed. This file is processed within a namespace that contains default
values for almost every parameter. This allows something like ``OUTPUT_IGNORE +=
['foo']`` and makes it more DRY (except ``VIEWS``).

.. [#] views is a dictionary mapping of view name to view instance and is not
   available in ``conf`` but ``env``, so you can test for a given view with
   ``if 'entry' in env.views``.

Here is a list of settings for acrylamid, regarding the different features.

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
`OUTPUT_IGNORE` (|ignored|)                         A list of filename/directory-patterns which
                                                    Acrylamid should ignore.
`FILTERS` (|filter|)                                Global list of filters.
`VIEWS` (see example conf.py)                       Dictionary of views set in conf.py.
`WWW_ROOT` (``'http://localhost:8000'``)            Your actual website link where you host this blog.
                                                    It's used to build absolute urls (required for disqus
                                                    and feeds).
`CONTENT_DIR`(``content/``)                         Directoy where you write your posts to.
`LAYOUT_DIR` (``layouts/``)                         Directoy where you place your jinja2 templates.
`OUTPUT_DIR` (``output/``)                          Directoy where the output goes to.
`FILTERS_DIR` (*not set*)                           If you want add your own filters, create a directory,
                                                    put your filters into and add this directory to conf.
`VIEWS_DIR` (*not set*)                             Like above but for custom views.
================================================    =====================================================

.. |ignored| replace::

    ``['/style.css', '/images/*', '.git/']``

.. |filter| replace::

    ``["markdown+codehilite(css_class=highlight)", "hyphenate"]``


URL Settings
------------

When it comes to URLs, Acrylamid follows two simple rules: always add a
*index.html* to an URL with trailing slash. Secondly: substitution variables
begin with a double dash and then the wished property:

- ``/2012/hello-world/`` gets a ``index.html`` as filename for nice URLs
- ``/atom/index.html`` gets not touched anywhere and uses ``index.html``
  as filename.
- ``/page/:num/`` gets expanded to ``/page/2/index.html`` if ``num = 2``.

Use :doc:`views` and :doc:`templating` as reference guide for all possible
variable name substitutions in a current view.

================================================    =====================================================
Variable name (default value)                       Description
================================================    =====================================================
`PERMALINK_FORMAT` (``'/:year/:slug/'``)            A (substitution) string where we save this URL
================================================    =====================================================

Date format and locale
----------------------

A few filters and views (namely hyphenation and syndication feeds) depend on a
valid locale and language. By default we use the system's locale but in some
cases you would rather use a different. Thus, you can set ``LANG`` to your
favourite language (if available) and it will be also used as default language
for hyphenation.


================================================    =====================================================
Variable name (default value)                       Description
================================================    =====================================================
`LANG`  (``''`` [#]_)                               Default language [#]_ to use -- is important for
                                                    hyphenation patterns. Is available as two-character
                                                    locale in templating.
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
.. [#] see `ISO_639 <https://en.wikipedia.org/wiki/ISO_639>`_, if not set or the
   given locale is not available,  the system's will be used. If you don't like
   this behaviour, use ``'C'`` instead which results in an english locale. On
   linux and you may not have generated all locales, try *en-us* instead of *en*
   or use the *exact* locale like "en_US.UTF-8".

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
                                                    *2* after all tags as standalone link.
`SUMMARIZE_ELLIPSIS` (``&#8230;``)                  Ellipsis (defaults to three typographical dots, …)
`SUMMARIZE_IDENTIFIER` (``weiterlesen``)            The text inside the continue reading link.
`SUMMARIZE_CLASS` (``continue``)                    CSS-class used in ``<a>``-Tag.
================================================    =====================================================

.. [#] Note, disqus only knows a given URL. If you change the title of an entry
   and you don't setup recirect codes or leave the original url by setting
   ``permalink: /2011/a-title/``, you'll lose your disqus comments for this thread.


Tag cloud
---------

If you want to generate a tag cloud with all your tags, you can do so using the
following settings.

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


You should then also define a CSS style with the appropriate classes (tag-0 to
tag-N, where N matches TAG_CLOUD_STEPS -1).
