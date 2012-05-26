Extending Acrylamid
===================

Acrylamid is designed to easily integrate custom code and you can customize
almost everything: transformation to the content, custom HTML layout or a
new view of your posts. Acrylamid itself is using this API to implement
different text parsers like Markdown or reStructuredText, hyphenation and
the complete rendering of articles, single posts and paged listings.

Filters
-------

.. autoclass:: acrylamid.filters.Filter()


Views
-----

.. autoclass:: acrylamid.views.View()


Layout
------

Acrylamid depends deeply on the popular Jinja2 template engine written in
*pure* python. To work with Acrylamid each template you get from the
environment object has a special attribute called ``has_changed`` and
indicates over the whole compilation process if this template has changed
or not. If a template inherits a template, we also check wether this has
changed and so on.

This allows us to write a simple statement wether we may skip a page or
need to re-render it.

.. todo:: make templates configurable

- Jinja2 API docs
- Jinja2 Designer Docs
