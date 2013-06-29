Multi-Post
==========

.. _views-index:

Index
-----

.. _views-archive:

Archive
-------

.. _views-category:

Category
--------

A view to recursively render all posts of a category, sub category and
so on. Configuration syntax:

.. code-block:: python

    '/category/:name/': {
        'view': 'category',
        'pagination': '/category/:name/:num/'
    }

Categories are either explicitly set in the metadata section
(`category: foo/bar`) or derived from the path of the post, e.g.
`content/projects/python/foo-bar.txt` will set the category to `projects/python`.

.. code-block:: sh

    $ tree content/
    content/
    ├── projects
    │   ├── bla.txt
    │   └── python
    │       └── fuu.txt
    └── test
        └── sample-entry.txt

The directory structure above then renders the following:

.. code-block:: sh

    $ acrylamid compile
      create  [0.00s] output/category/test/index.html
      create  [0.00s] output/category/projects/index.html
      create  [0.00s] output/category/projects/python/index.html

Both, bla.txt and fuu.txt are shown on the project listing, but only the
fuu.txt post appears on the projects/python listing.

Categories in the Entry Context
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To link to the category listing, use the following Jinja2 code instead of
the tag code in the `entry.html` template:

.. code-block:: html+jinja

   {% if 'category' in env.views and entry.category %}
       <p>categorized in
           {% for link in entry.category | categorize %}
               <a href="{{ env.path + link.href }}">{{ link.title }}</a>
               {%- if loop.revindex > 2 -%}
               ,
               {%- elif loop.revindex == 2 %}
               and
               {% endif %}
           {% endfor %}
       </p>

This uses the new `categorize` filter which is available when you have the
category view enabled. It takes the category list from `entry.category` and
yields the hierarchical categories, e.g. projects/python yields projects and
projects/python.

Categories in the Environment Context
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Similar to the tag cloud you are able to generate a category listing on
each page: ``env.categories`` is an iterable object that yields categories
(which are iterable as well and yield sub categories). The following Jinja2
code recursively renders all categories and sub categories in a simple list:

.. code-block:: html+jinja

    <ul class="categories">
    {% for category in env.categories recursive %}

        <li>Category: <a href="{{ category.href }}">{{ category.title }}</a>
            with {{ category.items | count }} articles.
        </li>

        {% if category %}
            <ul class="depth-{{ loop.depth }}">{{ loop(category) }}</ul>
        {% endif %}

    {% endfor %}
    </ul>


.. versionadded:: 0.8

    Support for categories was introduced.

.. _views-tag:

Tag
---
