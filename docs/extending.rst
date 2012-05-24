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

.. note:: TODO

.. code-block:: python

    from acrylamid.views import View

    class Articles(View):

        def init(self, key=value):
            pass

        def context(self, env, request):
            return env

        def generate(self, request):
            pass


Layout
------

.. note:: TODO