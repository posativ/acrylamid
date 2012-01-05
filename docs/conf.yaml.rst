conf.yaml
=========

Acrylamid's configuration is read from `conf.yaml` inside your blog-folder. It
is a YAML-like syntax (key: value) and don't requires every key to be set. If
a given key is not set it will be derived from *acrylamid.defaults*.

A basic configuration looks like this:

::

    blog_title: A descriptive blog title

    author: anonymous
    website: http://example.org/
    email: info@example.org

    www_root: http://example.org/
    lang: de_DE
    strptime: %d.%m.%Y, %H:%M

    disqus_shortname: yourname

    views.filters: ['markdown+codehilite(css_class=highlight)', 'hyphenate']

    views.index.filters: ['summarize', 'h1']
    views.entry.filters: ['h1']
    views.feeds.filters: ['h2']

Each key-value pair is available during templating. Acrylamid uses `jinja2
<http://jinja.pocoo.org/docs/>`_, see their `Template Designer Documentation
<http://jinja.pocoo.org/docs/templates/>`_ for details.

A ``views.`` or ``filters.`` statement has special meaning to acrylamid's
internal program flow. You can set global filters and overwrite or exclude
filters for each view individually.

key-value statements
********************

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
