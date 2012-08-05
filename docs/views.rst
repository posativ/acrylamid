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

.. autoclass:: acrylamid.views.articles.Articles()

.. autoclass:: acrylamid.views.entry.Entry()

.. autoclass:: acrylamid.views.index.Index()

.. autoclass:: acrylamid.views.page.Page()

.. autoclass:: acrylamid.views.tag.Tag()

.. autoclass:: acrylamid.views.sitemap.Sitemap()


.. note:: TODO: Feeds!



Custom Views
************

You can easily extend Acrylamid by writing custom views directly in your blog
directory.
