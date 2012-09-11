Welcome to Acrylamid
====================

Acrylamid is a mixture of `nanoc <http://nanoc.stoneship.org/>`_, `Pyblosxom
<http://pyblosxom.bluesock.org/>`_ and `Pelican <http://blog.getpelican.com/>`_
licensed under BSD Style, 2 clauses.

|Build Status|_

.. _Build Status: http://travis-ci.org/posativ/acrylamid
.. |Build Status| image:: https://secure.travis-ci.org/posativ/acrylamid.png


Why?
----

Acrylamid isn't your granddad's static blog compiler. I think that just sums
it up.

- it is *fast* (incremental builds)
- support for Jinja2_ or Mako_ templates
- many Markdown_ extensions and custom reStructuredText_ directives
- MathML_, enhanced typography and hyphenation using soft-hyphens

Oh, and it can also generate a static blog with articles, static pages, tags,
RSS/Atom feeds (also per tag) and an article overview.

.. _Jinja2: http://jinja.pocoo.org/
.. _Mako: http://www.makotemplates.org/
.. _MathML: http://www1.chapman.edu/~jipsen/mathml/asciimath.html

Overview
--------

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
  hyphenation feature?)
- HTML5 valid (but there's a XHTML template, too)
- internal webserver with automatic compiling when something has changed
- assets management, including LESS_ and SASS_ conversion.
- uni-directional PingBack support.

.. _YAML front matter: https://github.com/mojombo/jekyll/wiki/YAML-Front-Matter
.. _Jekyll: http://jekyllrb.com/
.. _nanoc: http://nanoc.stoneship.org/
.. _LESS: http://lesscss.org/
.. _SASS: http://sass-lang.com/

what is missing
~~~~~~~~~~~~~~~

- No comments. You have to use Disqus_ or `this approach`_.
- No search. But it's on the roadmap, Sphinx_ too.
- A consistent™ documentation.

.. _Disqus: http://disqus.com/
.. _this approach: http://hezmatt.org/~mpalmer/blog/2011/07/19/static-comments-in-jekyll.html
.. _Sphinx: http://sphinx.pocoo.org/latest/

Quickstart
----------

The latest release on PyPi is outdated but the current master not yet finished.
But to get the latest improvements (and there have been alot) as well as new
features such as asset handling use:

::

    easy_install -U https://github.com/posativ/acrylamid/tarball/master

This installs Acrylamid with Jinja2_ as templating engine. For Mako_ use
``easy_install -U acrylamid --mako``. This installs two additional but not
required dependencies: ``Markdown`` and ``translitcodec``. To get a list of
all supported modules, head over to `additional supported modules`_.

.. _additional supported modules: http://posativ.org/acrylamid/installation.html#additional-supported-modules

Initialize the base structure, edit *conf.py* and *layouts/* and compile with:

::

    $ acrylamid init myblog
        create  myblog/conf.py
        ...
    $ cd myblog/
    $ acrylamid compile && acrylamid view
        create  [0.05s] output/articles/index.html
        create  [0.37s] output/2012/die-verwandlung/index.html
        create  [0.00s] output/index.html
        create  [0.00s] output/tag/die-verwandlung/index.html
        create  [0.00s] output/tag/franz-kafka/index.html
        create  [0.03s] output/atom/index.html
        create  [0.04s] output/rss/index.html
        create  [0.00s] output/sitemap.xml
        create  output/style.css
    9 new, 0 updated, 0 skipped [0.72s]
       * Running on http://127.0.0.1:8000/

Real World Examples?
~~~~~~~~~~~~~~~~~~~~

- sources from my `personal blog <http://blog.posativ.org/>`_:
  `/posativ/blog.posativ.org <https://github.com/posativ/blog.posativ.org/>`_.
- sebix' (contributer) `blog <http://sebix.github.com/>`_ sources:
  `/sebix/sebix.github.com-sources <https://github.com/sebix/sebix.github.com-sources>`_.

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
        clean         remove abandoned files
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

Join ``#acrylamid`` on Freenode_!

.. _Freenode: http://freenode.net/
