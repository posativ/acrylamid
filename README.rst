Welcome to Acrylamid
====================

*Notice:*

* don't try the master branch unless you are very sure about the not
  yet documented changes.
* PyPi releases (0.7.x) do not work with Python 3.3+ due dependency
  pinning. The upcoming 0.8 release will drop support for 3.2, but
  fully supports 3.3 and higher.
* yes, the name will change (still searching for a good name) and a
  transition from "static blog generator" to "static site generator"
  is already on my todo list.

Acrylamid is a mixture of `nanoc <http://nanoc.stoneship.org>`_, `Pyblosxom
<http://pyblosxom.github.io>`_ and `Pelican <http://blog.getpelican.com>`_
licensed under BSD Style, 2 clauses. It is actively developed at
https://github.com/posativ/acrylamid/.

|Build Status|_

.. _Build Status: http://travis-ci.org/posativ/acrylamid
.. |Build Status| image:: https://secure.travis-ci.org/posativ/acrylamid.png?branch=master


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

Why the name “Acrylamid”?
-------------------------

I'm studying bioinformatics and I was experimenting with Acrylamide at this
time. I'm really bad at naming. If you have a better name, please tell me!
Two requirements: reasonably speakable and tab-completion after 3 characters.

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
- `liquid plugins`_ ported from `Octopress <http://octopress.org/>`_

.. _typography: https://code.google.com/p/typogrify/
.. _smartypants: http://daringfireball.net/projects/smartypants/
.. _acronym detection: http://pyblosxom.github.com/1.5/plugins/acronyms.html
.. _liquid plugins: http://octopress.org/docs/plugins/

blogging features
~~~~~~~~~~~~~~~~~

- you like the `YAML front matter`_ from Jekyll_ or nanoc_? First choice in Acrylamid!
- coming from Pelican_? Acrylamid has also support for metadata in the native
  format of Markdown, reStructuredText and even Pandoc.
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

- No comments. You have to use Disqus_, Isso_ or `this approach`_.

.. _Disqus: http://disqus.com/
.. _Isso: https://github.com/posativ/isso
.. _this approach: http://hezmatt.org/~mpalmer/blog/2011/07/19/static-comments-in-jekyll.html
.. _Sphinx: http://sphinx.pocoo.org/latest/

Quickstart
----------

::

    easy_install -U acrylamid

This installs Acrylamid with Jinja2_ as templating engine. For Mako_ use
``easy_install -U acrylamid[mako]``. This installs two additional but not
required dependencies: ``Markdown`` and ``translitcodec``. To get a list of
all supported modules, head over to `additional supported modules`_.

If you rather use non-ascii characters, you're better off with:

::

    easy_install -U acrylamid python-magic unidecode

.. _additional supported modules: http://posativ.org/acrylamid/installation.html#additional-supported-modules

Initialize the base structure, edit *conf.py* and *layouts/* and compile with:

::

    $ acrylamid init myblog  # --mako, defaults to --jinja2
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

- `Practicing web development <http://www.vlent.nl/>`_ – Mark van Lent
  [`source <https://github.com/markvl/www.vlent.nl>`__]
- `mecker. mecker. mecker. <http://blog.posativ.org/>`_ – Martin Zimmermann
  [`source <https://github.com/posativ/blog.posativ.org/>`__]
- `Groovematic <http://groovematic.com/>`_ –  Isman Firmansyah
  [`source <https://github.com/iromli/groovematic>`__]
- `Christoph Polcin <http://www.christoph-polcin.com/>`_ – Christoph Polcin
  [`source <http://git.christoph-polcin.com/blog/>`__, `theme <http://git.christoph-polcin.com/acrylamid-theme-bipolar/>`__]
- `Knitatoms <http://knitatoms.net>`_ – Tom Atkins
  [`source <https://github.com/knitatoms/knitatoms.net>`__]

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
`GitHub Issues`_. The project has also a mailing list [Archive_], just send
an email to ``acrylamid@librelist.com`` and you have subscribed .

.. _Freenode: http://freenode.net/
.. _Github Issues: https://github.com/posativ/acrylamid/issues?state=open
.. _Archive: http://librelist.com/browser/acrylamid/

How to contribute
-----------------

Communication.  Beside that, I am open for most enhancements, just
two requirements:

* resepect PEP-8 (max line length may vary, but use 80 as your soft limit
  and 100 as your hard limit; 105 for ugly ``if`` linebreaks though).
* I prefer clear code (early return instead of nested else etc.) and concise
  variable (and configuration) names. Also: ``@[cached_]property`` is way
  better than `get_thing(self)`.

Be aware, that the current master has been quite diverged from the PyPi
release (legacy/0.7 branch). If you are going to fix a bug, branch off
the legacy branch. On the other hand, if you want to contribute features,
branch off the master branch, but expect things to be changed/broken/removed.

The master branch features a 2.6/2.7/3.3 unified code base, please have a look
at the ``acrylamid.compat`` module (e.g. `map`, `filter` etc).
