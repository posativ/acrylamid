acrylamid documentation
=======================

acrylamid is yet another lightweight static blogging software written in python
and designed to get a high quality output. Its licensed under BSD Style, 2 clauses.

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

    pip install acrylamid

You'll need ``python``, ``jinja2`` and either ``markdown`` (default) or
``docutils``. For nicer urls also ``translitcodec`` is required. ``pygments``
and ``asciimathml`` for colored code listings respectively MathML.
Full-featured installation do:

::

    pip install docutils translitcodec pygments asciimathml

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


::

    output/
    ├── 2011/
    │   └── a-meaningful-title/
    │       └── index.html
    ├── articles/
    │   └── index.html
    ├── atom/
    │   └── index.html
    ├── rss/
    │   └── index.html
    └── index.html

Filters
**********

- **markdown**: rendering Markdown (+asciimathml,pygments)
- **rest**: reStructuredText (+pygments)
- **typography**: https://code.google.com/p/typogrify/ (and custom modifications)
- **summarize**: summarizes posts to 200 words
- **hyphenation**: hyphenate words (len > 10) based on language
- **head_offset**: decrease headings by offset

Views
*****

- **articles**: articles overview
- **entry**: renders single entry to given slug
- **index**: creates pagination / and /page/:num
- **feeds**: valid atom/rss feed
