Welcome to Acrylamid
====================

Acrylamid is a mixture of `nanoc <http://nanoc.stoneship.org/>`_, `Pyblosxom
<http://pyblosxom.bluesock.org/>`_ and `Pelican <http://blog.getpelican.com/>`_
licensed under BSD Style, 2 clauses. It is actively developed and maintained
at https://github.com/posativ/acrylamid/.

|Build Status|_

.. _Build Status: http://travis-ci.org/posativ/acrylamid
.. |Build Status| image:: https://secure.travis-ci.org/posativ/acrylamid.png?branch=master


.. toctree::
   :maxdepth: 1

   installation
   usage
   advanced
   conf.py
   commands
   idea
   filters
   views
   assets
   static-search
   theming
   templating
   extending
   howtos
   about

Why?
----

- it is really *fast* due incremental builds
- support for Jinja2_ and Mako_ templates
- many Markdown_ extensions and custom reStructuredText_ directives
- MathML_, enhanced typography and hyphenation using soft-hyphens

Oh, and it can also generate a static blog with articles, static pages, tags,
RSS/Atom feeds (also per tag), article listing and a sitemap.

.. _Jinja2: http://jinja.pocoo.org/
.. _Mako: http://www.makotemplates.org/
.. _MathML: http://www1.chapman.edu/~jipsen/mathml/asciimath.html

Overview
--------

With Acrylamid you can write your weblog entries with your editor of choice in
Markdown, reStructuredText or textile. With several content filters you can
pimp your HTML (typography, math, hyphenation). Acrylamid provides a very
sophisticated CLI and integrates perfectly with any DVCes. It generates
completely static HTML you can host everywhere.

supported markup languages
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Markdown_ and additional extensions (support for MathML_, deletion/insertion,
  sub- and supscript, syntax highlighting …)
- reStructuredText_ with directives for syntax highlighting and youtube video
  embedding
- textile_, discount_, all dialects supported by pandoc_ and plain HTML

You miss one? Extend Acrylamid in `less than 30 LoC`_!

.. _Markdown: http://daringfireball.net/projects/markdown/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _textile: https://en.wikipedia.org/wiki/Textile_%28markup_language%29
.. _discount: http://www.pell.portland.or.us/~orc/Code/discount/
.. _pandoc: http://johnmacfarlane.net/pandoc/
.. _less than 30 LoC: https://posativ.org/git/acrylamid/blob/master/acrylamid/filters/pytextile.py

other filters
~~~~~~~~~~~~~

- support for Jinja2 and Mako directly in postings (before they get processed)
- typography_ (and smartypants_)
- TeX hyphenation
- summarize ability
- `acronym detection`_  that automatically replace acronyms and abbreviations

.. _typography: https://code.google.com/p/typogrify/
.. _smartypants: http://daringfireball.net/projects/smartypants/
.. _acronym detection: http://pyblosxom.github.com/1.5/plugins/acronyms.html

blogging features
~~~~~~~~~~~~~~~~~

- you like the `YAML front matter`_ from Jekyll_ or nanoc_? First choice in Acrylamid!
- coming from Pelican_? Acrylamid has also support for metadata in the native
  format of Markdown or reStructuredText.
- support for translations (oh, and did I mention the language dependend
  hyphenation feature?).
- a few HTML5 themes, see `Theming <http://posativ.org/acrylamid/theming.html>`_.
- internal webserver with automatic compiling when something has changed.
- assets management, including LESS_ and SASS_ conversion.
- uni-directional PingBack support.
- static site search.

.. _YAML front matter: https://github.com/mojombo/jekyll/wiki/YAML-Front-Matter
.. _Jekyll: http://jekyllrb.com/
.. _nanoc: http://nanoc.stoneship.org/
.. _LESS: http://lesscss.org/
.. _SASS: http://sass-lang.com/

what is missing
~~~~~~~~~~~~~~~

- No comments. You have to use Disqus_ or `this approach`_.

.. _Disqus: http://disqus.com/
.. _this approach: http://hezmatt.org/~mpalmer/blog/2011/07/19/static-comments-in-jekyll.html

Quickstart
----------

::

    easy_install -U acrylamid

This installs Acrylamid with Jinja2_ as templating engine. For Mako_ use
``easy_install -U acrylamid[mako]``. This installs two additional but not
required dependencies: ``Markdown`` and ``translitcodec``. To get a list of
all supported modules, head over to `additional supported modules`_.

.. _additional supported modules: http://posativ.org/acrylamid/installation.html#additional-supported-modules

Initialize the base structure, edit *conf.py* and *layouts/* and compile with:

.. raw:: html

    <pre>
    $ acrylamid init myblog  <span style="color: #999"># --mako, defaults to --jinja2</span>
      <span style="font-weight: bold; color: #00aa00">   create</span>  myblog/output/conf.py
        ...
    $ cd myblog/
    $ acrylamid compile && acrylamid view
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.02s] output/articles/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.31s] output/2012/die-verwandlung/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.00s] output/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.00s] output/tag/die-verwandlung/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.00s] output/tag/franz-kafka/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.01s] output/atom/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.01s] output/rss/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.00s] output/sitemap.xml
      <span style="font-weight: bold; color: #00aa00">   create</span>  output/style.css
    9 new, 0 updated, 0 skipped [0.50s]
       * Running on http://127.0.0.1:8000/
    </pre>

Real World Examples?
~~~~~~~~~~~~~~~~~~~~

- `Practicing web development <http://www.vlent.nl/>`_ – Mark van Lent
  [`source <https://github.com/markvl/www.vlent.nl>`_]
- `mecker. mecker. mecker. <http://blog.posativ.org/>`_ – posativ
  [`source <https://github.com/posativ/blog.posativ.org/>`_]

Commands
--------

See `commands <https://posativ.org/acrylamid/commands.html>`_ for a detailed
overview.

::

    $ acrylamid --help
    usage: acrylamid [-h] [-v] [-q] [-C] [--version]  ...

    positional arguments:

        init          initializes base structure in DIR
        compile       compile blog
        view          fire up built-in webserver
        autocompile   automatic compilation and serving
        new           create a new entry
        check         run W3C or validate links
        deploy        run task
        import        import content from URL or FILE
        info          short summary
        ping          notify ressources

    optional arguments:
      -h, --help      show this help message and exit
      -v, --verbose   more verbose
      -q, --quiet     less verbose
      -C, --no-color  disable color
      --version       show program's version number and exit

Need Help?
----------

Join ``#acrylamid`` on Freenode_! If you found a bug, please report it on
`GitHub Issues`_.

.. _Freenode: http://freenode.net/
.. _Github Issues: https://github.com/posativ/acrylamid/issues?state=open

API Reference
-------------

.. toctree::
   :maxdepth: 2

   api/core
   api/readers
   api/helpers
   api/lib
