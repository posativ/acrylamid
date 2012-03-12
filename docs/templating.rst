Templating
==========

Within ``layout/base.html``, ``layout/main.html`` and ``layout/entry.html``
the conf, env and entry dictionary have directly accessible attributes.
Instead of writing ``entry.permalink`` you just need to write ``permalink``.

Variables
---------

Internally all configuration variables are written in small caps, therefore
this listing may differ from `doc: conf.py`.

conf
****

Global configuration, ``conf.py``.

:sitename:
    The name of your blog. It's displayed in the <title>-block.

:author:
    Blog's primary author. To set individual authors per entry, see entry.author.

:email:
    Your email address -- used in Atom/RSS feeds and as contact ability at the bottom in the default layout.

:lang:
    Default language, defaults to ``de_DE`` and is important for the hyphenation patterns XXX: and also in ``meta http-equiv="content-language"``.

:date_format:
    This python date-format string is used in ``layout/entry.html`` to render the date nicely. Defaults to ``%d.%m.%Y, %H:%M``, see `Python's strftime directives <http://strftime.org/>`_ for detailed explanation of these variables.

:encoding:
    Default encoding of your text files, defaults to utf-8 and can only globally set.

:permalink_format:
    A substitution string as described here (XXX), defaults to ``/:year/:slug/``.

:output_ignore:
    A list of filename/directory-patterns which acrylamid should ignore.

:filters:
    Global list of filters.

:views:
    Dictionary of set views.


env
***

Environment which contains some useful informations like version info.

:protocol:
    Internet protocol determined from ``sitename``, should be http or https.

:netloc:
    Domain name like *domain.example.tld*, derieved from ``sitename``

:path:
    Path (sub-uri) from ``sitename``, used for relative links.

:views:
    A list of executed views, only used to explicitely activate certain features like Disqus-integration or tagging in templates.

:VERSION:
    Acrylamid's version

:VERSION_SPLIT:
    Acrylamid's version split, a three-items tupel, e.g. ``('0', '3', '0')``.

entry
*****

:permalink:
    actual permanent link

:date:
    entry's :class:`datetime.datetime` object

:year:
    entry's year as string

:month:
    entry's month as string

:day:
    entry's day as string

:filters:
    a per-post applied filters as list

:tags:
    per-post list of applied tags

:title:
    entry's title

:author:
    entry's author as set in entry or from conf.py if unset

:lang:
    entry's language, derieved from conf.py if unset

:content:
    returns rendered content

:description:
    first 50 characters from the source

:slug:
    safe entry title

:draft:
    if set to True, the entry will not appear in articles, index, feed and tag view

:extension:
    filename's extension