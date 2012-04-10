Views
=====

A view in Acrylamid is the representation of your content like single full-text,
tag listing or articles overview. Acrylamid ships with most features typical
for a dynamic blog except an static search (still a todo). Here is an overview
of what views do for you:

- short but unique identifier based on time and title, like
  */2012/haensel-und-gretel/* (yes, including unicode transition)
- compatible with restricted web hosting services by using a folder as
  identifier with an *index.html* inside.
- portable (= relative) urls, except you use Disqus
- incremental update (only edited articles/templates)

All views have some properties in common such as path, filters and
conditionals, you set in :doc:`conf.py`. The path is your the where you
assigned a new dictionary containing options for this view. Let's use an
example:

.. code-block:: python

    VIEWS = {
        "/path/": {"view": "special", "if": lambda e: e.lang == 'klingon',
                   arg:""}
    }

To make the next section more easier to read, we define "/path/" as route,
"view: special" as type of view and "if: lambda x: x" as condition.

Built-in Views
**************

Articles
--------

- `Articles Example <http://blog.posativ.org/articles/>`_

Creates a single page overview of all articles in the form of (year) date and
title. This view uses *articles.html* as jinja2 template to function.

The default configuration outputs this to */articles/* and is (currently)
hardcoded into *base.html*.

Entry
-----

- `Entry Example <http://blog.posativ.org/2012/nginx/>`_

The entry view renders an post to a unique location and should be used as
permalink URL. The url is user configurable using the ``PERMALINK_FORMAT``
variable and defaults to */:year/:slug/(index.html)*.

This view takes no other arguments and uses *main.html* and *entry.html* as
template.

Index
-----

Creates nicely paged listing of your posts. First page renders to ``route``
(defaults to */*) with a recent list of your (e.g. summarized) articles. Other
pages enumerate to the variable ``pagination`` (*/page/:num/* per default).

The Index view uses *main.html* and *entry.html* as template and yields
``items_per_page`` items per page (default: 10).

Tag
---

Same behaviour like Index except ``route`` that defaults to */tag/:name/* and
``pagination`` that defaults to */tag/:name/:num/* where :name is the current
tag identifier.

Feed
----



Custom Views
************

You can easily extend Acrylamid by writing custom views directly in your blog
directory.
