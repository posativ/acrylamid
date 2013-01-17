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

        '/:year/:slug/': {'views': ['entry', 'draft']},

        '/tag/:name/': {'filters': 'summarize', 'view':'tag',
                        'pagination': '/tag/:name/:num'},

        '/atom/': {'filters': ['h2', 'nohyphenate'], 'view': 'atom'},
        '/rss/': {'filters': ['h2', 'nohyphenate'], 'view': 'rss'},

        '/articles/': {'view': 'articles'},
    }

    ENGINE =  'acrylamid.templates.jinja2.Environment'
    PERMALINK_FORMAT = '/:year/:slug/index.html'
    DATE_FORMAT = '%d.%m.%Y, %H:%M'

Each key-value pair (except views [#]_) is available during :doc:`templating`.

See the respective documentation for your templating engine for more details on
how to use the templating languages:
`jinja2 Template Designer Documentation <http://jinja.pocoo.org/docs/templates/>`_,
`Mako Documentation <http://docs.makotemplates.org/en/latest/index.html>`_.

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
`FILTERS` (|filter|)                                Global list of filters.
`VIEWS` (see example conf.py)                       Dictionary of views set in conf.py.
`WWW_ROOT` (``'http://localhost:8000/'``)           Your actual website link where you host this blog to
                                                    build absolute urls (required for Disqus and feeds).
                                                    You can also set a sub URI like ``example.org/blog``.
`OUTPUT_DIR` (``output/``)                          Directory where the output goes to.
`CONTENT_DIR` (``content/``)                        Directory where you posts are located. No assets will
                                                    be copied from this directory!
`CONTENT_EXTENSION` (``.txt``)                      Filename extension used for creating new entries.
`CONTENT_IGNORE` (|ignored|)                        A list of filename/directory-patterns [#]_ which
                                                    Acrylamid should ignore.
`THEME` (``layouts/``)                              Directory where you place your jinja2 templates.
`THEME_IGNORE` (|ignored|)                          Same as ``CONTENT_IGNORE`` but for ``THEME``.
`STATIC` (*not set*)                                A directory or list of directories which contain
                                                    objects Acrylamid should copy to destination dir.
`STATIC_IGNORE` (|ignored|)                         Same as ``CONTENT_IGNORE`` but for ``STATIC``.
`STATIC_FILTER` (``['HTML', 'XML']``)               See :doc:`assets` for details.
`FILTERS_DIR` (*not set*)                           If you want add your own filters, create a directory,
                                                    put your filters into and add this directory to conf.
`VIEWS_DIR` (*not set*)                             Like above but for custom views.
================================================    =====================================================

.. |ignored| replace::

    ``['.git*', '.hg*', '.svn']``

.. |filter| replace::

    ``["markdown+codehilite(css_class=highlight)", "hyphenate"]``

.. [#] The syntax for ignore patterns is very similar to ``git-ignore``: a
   path with a leading slash means absolute position (to /path/to/output/),
   path with trailing slash marks a directory and everything else is just
   relative fnmatch.

   - ``".hidden"`` matches every file named *.hidden*, ``"/.hidden"`` matches
     a file in the base directory named the same.
   - ``".git/*"`` excludes *HEAD*, *config* and *description* but not the
     directories  *hooks/* and *info/*.
   - ``".git/"`` ignores a *.git* folder anywhere in the output directory,
     ``"/.git/"`` only *output/.git*.

Templating Engine
-----------------

=======================================================    =====================================================
Variable name (default value)                              Description
=======================================================    =====================================================
`ENGINE` (``'acrylamid.templates.jinja2.Environment'``)    The full (importable) name of the Environment class
                                                           (see `acrylamid.templates.AbstractEnvironment`) for
                                                           your templating engine (currently, acrylamid supports
                                                           `jinja2 <http://jinja.pocoo.org/>`_ and
                                                           `Mako <http://www.makotemplates.org/>`_).
=======================================================    =====================================================

URL Settings
------------

When it comes to URLs, Acrylamid follows two simple rules: always add a
*index.html* to an URL with a trailing slash. Second: substitution variables
begin with a double dash and and the attribute name:

- ``/2012/hello-world/`` gets a ``index.html`` as filename for nice URLs
- ``/atom/index.html`` gets not touched anywhere and uses ``index.html``
  as filename.
- ``/page/:num/`` gets expanded to ``/page/2/index.html`` for ``num = 2``,
  see :doc:`views` for details.
- ``/:slug.html`` becomes ``/hello-world.html`` for a given slug.

Use :doc:`views` and :doc:`templating` as reference guide for all possible
variable name substitutions in a current view.

================================================    =====================================================
Variable name (default value)                       Description
================================================    =====================================================
`ENTRY_PERMALINK` (*not set*)                       A substitution string where all entries were saved
                                                    to. By default you don’t need to set this parameter
                                                    because it takes the route where the view is `entry`.
                                                    If your url routes for the entry view are ambiguous,
                                                    you might need to set this parameter.
`PAGE_PERMALINK` (*not set*)                        Same for ENTRY_PERMALINK but for static pages.
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
`METASTYLE` (*not set*)                             With ``native`` you can Acrylamid parse Markdown's or
                                                    or reST's native meta data section if the filename
                                                    ends with ``.rst`` or ``.md`` and ``.mkdown``
                                                    respectively.
`DISQUS_SHORTNAME` (*not set*)                      Enables `Disqus <https://disqus.com/>`_ integration
                                                    with your site identifier [#]_.
`DEFAULT_ORPHANS` (``0``)                           The minimum number of articles allowed on the last
                                                    page. Use this when you don’t want to have a last
                                                    page with very few articles.
`SUMMARIZE_MODE` (``1``)                            Mode *0* this injects the link to the end of the
                                                    current tag, *1* after some black-listed tags and
                                                    *2* after all tags as standalone link.
`SUMMARIZE_LINK` (|link|)                           String template for the continue reading link
                                                    generated by ``summarize`` filter.
                                                    Default uses an ellipsis (three typographical dots,
                                                    …), a link with the css class ``continue`` and the
                                                    text ``continue`` and a single dot afterwards.
                                                    This string must contain ``%s`` where this link
                                                    location will be inserted.
`INTRO_LINK` (|link|)                               String template for the continue reading link
                                                    generated by ``intro`` filter.
                                                    Default uses an ellipsis (three typographical dots,
                                                    …), a link with the css class ``continue`` and the
                                                    text ``continue`` and a single dot afterwards.
                                                    This string must contain ``%s`` where this link
                                                    location will be inserted. If set to empty string,
                                                    no link is produced.
================================================    =====================================================

.. [#] Note, disqus only knows a given URL. If you change the title of an entry
   and you don't setup recirect codes or leave the original url by setting
   ``permalink: /2011/a-title/``, you'll lose your disqus comments for this thread.

.. |link| replace::

       ``'<span>&#8230;<a href="%s" class="continue">continue</a>.</span>'``


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

.. code-block:: html+jinja

    <ul>
    {% for tag in env.tag_cloud %}
        <li class="tag-{{ tag.step }}"><a href="/tag/{{ tag.name | safeslug }}/">{{ tag.name }}</a></li>
    {% endfor %}
    </ul>


You should then also define a CSS style with the appropriate classes (tag-0 to
tag-N, where N matches TAG_CLOUD_STEPS -1).
