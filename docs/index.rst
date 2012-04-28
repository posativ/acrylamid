Welcome to Acrylamid's Documentation!
=====================================

Acrylamid is yet another static blog compiler written in python that aims to
be lightweight, fast and producing high quality output. It is licensed under
BSD Style, 2 clauses.

.. toctree::
   :maxdepth: 1

   installation
   tutorial
   conf.py
   commands
   filters
   views
   templating
   extending
   howtos
   about

Features
--------

Acrylamid is a mixture of `nanoc <http://nanoc.stoneship.org/>`_, `Pyblosxom
<http://pyblosxom.bluesock.org/>`_ and `Pelican <http://pelican.notmyidea.org/>`_. It
features mainly:

- blog articles, static pages, tags RSS/Atom feeds and an article overview
- theming support (using jinja2_) and support for jinja2 directly in postings
- Markdown_, reStructuredText_, textile_ and pandoc_
- MathML, modern web-typography and hyphenation using `&shy;`
- RSS/Atom import, deployment and a handy CLI
- it's very flexible/configurable and fast

.. _jinja2: http://jinja.pocoo.org/
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _textile: https://en.wikipedia.org/wiki/Textile_%28markup_language%29
.. _pandoc: http://johnmacfarlane.net/pandoc/
.. _AsciiMathML: http://www1.chapman.edu/~jipsen/mathml/asciimath.html

Quickstart
----------

::

    easy_install -U acrylamid

It has actually only one dependency, ``jinja2`` but for convenience it also
installs ``markdown`` and ``translitcodec``. In addition it has support for
PyYAML, reStructuredText, syntax highlighting using pygments, asciimathml
to render MathML and finally smartypants for nicer typography.

::

    easy_install -U docutils pygments asciimathml smartypants

Get acrylamid, edit *conf.py* and *layouts/* and compile with:

::

    $> acrylamid init myblog
        create  myblog/conf.py
        ...
    $> cd myblog/
    $> acrylamid compile && acrylamid view
          warn  using mtime from <fileentry f'content/sample entry.txt'>
        create  '/articles/index.html', written to output/articles/index.html
        create  'Die Verwandlung', written to output/2011/die-verwandlung/index.html
        create  '/atom/index.html', written to output/atom/index.html
        create  '/rss/index.html', written to output/rss/index.html
        create  '/', written to output/index.html
       * Running on http://127.0.0.1:8000/

Real World Example?
*******************

I have released all sources from my personal blog:
`/posativ/blog.posativ.org/ <https://github.com/posativ/blog.posativ.org/>`_. Take a
look at my *conf.py* for some inspiration.


Filters
-------

You can apply various filter to a single entry, to a specific view or globally
and Acrylamid resolves it automatically (some filters conflict with others so
you can for example apply *Markdown* as global filter but render some entries
with reStructuredText). Currently supported by acrylamid, see
`docs/filters.rst <http://acrylamid.readthedocs.org/en/latest/filters.html>`_
for detailed information:

- **Markdown**: rendering Markdown (+asciimathml,pygments,built-in extensions)
- **reST**: reStructuredText (+pygments)
- **pandoc**: Pandoc (+Markdown,textitle,rst,...)
- **textile**: using Textile as markup language
- **HTML**: don't render with filters mentioned above (it's a conflicting filter)

- **typography**: https://code.google.com/p/typogrify/ (and custom modifications)
- **hyphenation**: hyphenate words (len > 10) based on language
- **summarize**: summarizes posts to 200 words

- **head_offset**: decrease headings by offset
- **jinja2**: write jinja2 in your entries (you can also execute system calls therewith)
- **acronyms**: automatically replace acronyms and abbreviations to help unexperienced users


Commands
--------

See :doc:`commands` for a detailed overview.

::

    %> acrylamid --help
    Usage: acrylamid <subcommand> [options] [args]

    Options:
      -q, --quiet    less verbose
      -v, --verbose  more verbose
      -h, --help     show this help message and exit
      --version      print version details

    Commands:
      init           initializes base structure in DIR
      create  (new)  creates a new entry
      compile (co)   compile blog
      view           fire up built-in webserver
      autocompile    automatic compilation and serving (short aco)
      clean   (rm)   remove abandoned files
      import         import content from URL
      deploy         run a given TASK

    All subcommands except `init` require a conf.py file.
