Templating
==========

The default theme is very minimalistic and may don't fit to everyone's
expectations. But like every blog compiler, you can edit the complete layout to
your likings.

Unlike others Acrylamid knows when you edited a template file, hence when you do
a session on templates and just the your changes without any interaction, launch
Acrylamid in auto-compile mode (``acrylamid autocompile``) and even when you
have hundrets of postings you will see your result almost immediately appear.

Variables
---------

Internally all configuration variables are written in small caps, therefore
this listing differs from :doc:`conf.py`.

conf
****

Global configuration, :doc:`conf.py`.

env
***

Environment which contains some useful informations like version info, current
protocol and count of entries.

:protocol:
    Internet protocol determined from ``sitename``, should be http or https.

:netloc:
    Domain name like *domain.example.tld*, derieved from ``sitename``

:path:
    Path (sub-uri) from ``sitename``, used for relative links.

:views:
    A list of executed views, only used to explicitely activate certain features like Disqus-integration or tagging in templates.

:type:
    Current view type to distuingish between single entry, tag or page view. Can be one of this list: ['entry', 'tag', 'index'].

:entrylist:
    A list of all processed FileEntry-objects.

:globals.entrylist:
    All entries processed by Acrylamid.

:num_entries:
    Count of all entries, only available in page/articles/index-view.

:prev:
    Number of the previous pagination index if available, e.g. ``'3'`` or ``None``.

:curr:
    Number of the current pagination index, e.g. ``2``.

:next:
    Number of the next pagination index if available, e.g. ``1`` or ``None``

:VERSION:
    Acrylamid's version

:VERSION_SPLIT:
    Acrylamid's version split, a three-items tupel, e.g. ``('0', '3', '0')``.

entry
*****

:type:
    either ``"entry"`` or ``"page"``

:permalink:
    actual permanent link

:date:
    entry's :class:`datetime.datetime` object

:year:
    entry's year (Integer)

:month:
    entry's month (Integer)

:zmonth:
    zero padded month number of the entry, e.g. "05" for May and "11"
    for November (String)

:day:
    entry's day (Integer)

:zday:
    zero padded day number of the entry, e.g. "04", "17" (String)

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
