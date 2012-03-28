Extending Acrylamid
===================

Acrylamid is designed to easily integrate custom code and you can customize
almost everything: transformation to the content, custom HTML layout or a
new view of your posts. Acrylamid itself is using this API to implement
different text parsers like Markdown or reStructuredText, hyphenation and
the complete rendering of articles, single posts and paged listings.

The following document shows the full API of Acrylamid.

Filters
-------

Filters are used to transform your input and used to perform Markdown-conversion
of your posts. Per default custom filters are stored in ``filters/`` directory
inside your blog. On startup, Acrylamid will parse this plugin, report
accidential syntax errors, initialize it and call it if required.

.. code-block:: python

    from acrylamid.filters import Filter

    class MyFilter(Filter):

        match = ['keyword', 'another']
        # conflicts = ['Markdown']

        def init(self, conf, env):
            pass

        def transform(self, content, request, *args):
            return content


Views
-----

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