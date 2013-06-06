Views
=====

Now, you know about transforming your content, you'll learn how to aggregate
your content. Acrylamid ships a few views but you are not limited to them. You
can easily write your own view without forking the project (more on this topic
later). Currently, Acrylamid ships the following:

  - article overview, an aggregation of all posts grouped by year and month.
  - entry view, a single full-text post.
  - index view, pagination of your content.
  - tag view, per tag pagination.
  - feed view, offering RSS and Atom aggregation (also per tag).
  - static site search, self-explanatory.

All views have some properties in common such as path, filters and conditionals,
you've to set in your :doc:`conf.py`.  The idea of views is similar to routes in
Django or Flask. You can set your URL setup to whatever you like, Acrylamid is
not fixed to a single directory structure. For convenience, Acrylamid appends an
``index.html`` to a URL if it does end with a slash (as shown in the defaults).

All views share some options such as view type, conditionals or route in common,
but can also offer individual parameters, you'll find explained in the built-in
views section.

path : string
  The route/path of the view(s). Note that you can't add the same route a second
  time, but you can add multiple views to a path.

view : string
  Name of your wished view. Exact case does not matter that much.

views : list of strings
  A list of views as described above.

filters : string or list of strings
  A list of filters or a single filter name to apply to the view.

if : lambda/function
  A condition to filter your content before they are passed to the view.

Here's an example of how to use views:

.. code-block:: python

    VIEWS = {
        "/path/": {"view": "translation", "if": lambda e: e.lang == 'klingon'}
    }

To see, what variables are available during templating, consult :doc:`templating`.


Built-in Views
**************

.. autoclass:: acrylamid.views.archive.Archive()

.. autoclass:: acrylamid.views.articles.Articles()

.. autoclass:: acrylamid.views.entry.Entry()

.. autoclass:: acrylamid.views.feeds.Feed()

.. autoclass:: acrylamid.views.index.Index()

.. autoclass:: acrylamid.views.entry.Page()

.. autoclass:: acrylamid.views.tag.Tag()

.. autoclass:: acrylamid.views.category.Category()

.. autoclass:: acrylamid.views.entry.Translation()

.. autoclass:: acrylamid.views.sitemap.Sitemap()


Custom Views
************

You can easily extend Acrylamid by writing custom views directly in your blog
directory. Just add ``VIEWS_DIR += ['views/']`` to your :doc:`conf.py` and write
your own view.
