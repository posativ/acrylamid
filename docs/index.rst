.. acrylamid documentation master file, created by
   sphinx-quickstart on Thu Jan  5 20:59:59 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to acrylamid's documentation!
=====================================

acrylamid is yet another lightweight static blogging software written in
python and designed to get a high quality output. Its licensed under BSD
Style, 2 clauses.

.. toctree::
   :maxdepth: 2

   installation
   .. tutorial
   .. usage
   conf.yaml
   filters
   .. views
   .. deployment
   howtos
   static_search
   about

Features
********

- blog articles, pages and rss/atom feeds
- theming support (using jinja2_)
- Markdown_ and reStructuredText_ as markup languages
- MathML generation using AsciiMathML_
- hyphenation using `&shy;`
- modern web-typography

.. _jinja2: http://jinja.pocoo.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _AsciiMathML: http://www1.chapman.edu/~jipsen/mathml/asciimath.html

Quickstart
**********

::

    easy_install -U acrylamid

You'll need ``python``, ``jinja2`` and either ``markdown`` (default) or
``docutils``. ``pygments`` and ``asciimathml`` for colored code listings
respectively MathML. Typography requires ``smartypants``. To get a
full-featured installation do:

::

    pip install docutils pygments asciimathml smartypants

Get acrylamid and edit *conf.yaml* and *layouts/*. Run acrylamid with:

::

    $> acrylamid init myblog
        create  myblog/content/
        ...
    $> cd myblog/
    $> acrylamid gen
          warn  using mtime from <fileentry f'content/sample entry.txt'>
        create  '/articles/index.html', written to output/articles/index.html
        create  'Die Verwandlung', written to output/2011/die-verwandlung/index.html
        create  '/atom/index.html', written to output/atom/index.html
        create  '/rss/index.html', written to output/rss/index.html
        create  '/', written to output/index.html

Using acrylamid
***************

- `conf.yaml </posativ/acrylamid/blob/master/docs/conf.yaml.rst>`_
- `filters </posativ/acrylamid/blob/master/docs/filters.rst>`_


Filters
**********

See `docs/filters.rst </posativ/acrylamid/blob/master/docs/filters.rst>`_ for
detailed information. Currently supported by acrylamid:

- **markdown**: rendering Markdown (+asciimathml,pygments)
- **rest**: reStructuredText (+pygments)
- **typography**: https://code.google.com/p/typogrify/ (and custom modifications)
- **summarize**: summarizes posts to 200 words
- **hyphenation**: hyphenate words (len > 10) based on language
- **head_offset**: decrease headings by offset
- **pass-through**: don't render with Markdown or reStructuredText

Views
*****

- **articles**: articles overview
- **entry**: renders single entry to given slug
- **index**: creates pagination / and /page/:num
- **feeds**: valid atom/rss feed
- **tags**: sort by tag with pagination (/:tag and /:tag/:num)


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

