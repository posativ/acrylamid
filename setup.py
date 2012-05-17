#!/usr/bin/env python
from distutils.core import setup

"""Welcome to Acrylamid
====================

Acrylamid is yet another static blog compiler written in python that aims to
be lightweight, fast and producing high quality output. It is licensed under
BSD Style, 2 clauses.

Why?
----

Why another static blog compiler, that's a valid question. So, why would you
use Acrylamid: It's fast when you start blogging and it stays fast when you
have hundreds of articles due incremental compilation. It ships with all
builtin Markdown extensions, custom ones and additional reStructuredText
directives to embed YouTube or Code. With all complexity of Acrylamid itself,
it is super easy to use.

Why not Acrylamid? It's not well tested by different people with different
requirements. It may has some serious issues I didn't noticed yet. It also
lacks some internal documentation. The default layout is indeed not the most
beautiful and Acrylamid has no asset handling yet.

Features
--------

Acrylamid is a mixture of `nanoc <http://nanoc.stoneship.org/>`_, `Pyblosxom
<http://pyblosxom.bluesock.org/>`_ and `Pelican <http://pelican.notmyidea.org/>`_. It
features mainly:

- blog articles, static pages, tags, RSS/Atom feeds and an article overview
- theming support (using jinja2_) and support for jinja2 directly in postings
- Markdown_, reStructuredText_, textile_ and pandoc_
- Markdown extensions and custom reStructuredText directives
- MathML, modern web-typography and hyphenation using soft-hyphens
- RSS/Atom/WordPress import, deployment and a handy CLI
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

Real World Examples?
********************

- sources from my personal blog:
  `/posativ/blog.posativ.org <https://github.com/posativ/blog.posativ.org/>`_.
- sebix' (contributer) sources: `/sebix/sebix.github.com-sources <https://github.com/sebix/sebix.github.com-sources>`_.


Filters
-------

You can apply various filter to a single entry, to a specific view or globally
and Acrylamid resolves it automatically (some filters conflict with others so
you can for example apply *Markdown* as global filter but render some entries
with reStructuredText). Currently supported by acrylamid, see
`docs/filters.rst <http://acrylamid.readthedocs.org/en/latest/filters.html>`_
for detailed information:

- **Markdown**: rendering Markdown (+asciimathml, pygments, built-in extensions)
- **reST**: reStructuredText (+pygments)
- **pandoc**: Pandoc (+Markdown, textitle, rst, ...)
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

See `commands <https://posativ.org/acrylamid/commands.html>`_ for a detailed overview.

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

Need Help?
----------

Join ``#acrylamid`` on Freenode_!

.. _Freenode: http://freenode.net/
"""

setup(
    name='acrylamid',
    version='0.3.3',
    author='posativ',
    author_email='info@posativ.org',
    packages=[
        'acrylamid', 'acrylamid.filters', 'acrylamid.views', 'acrylamid.lib',
        'acrylamid.defaults', 'acrylamid.tasks'],
    scripts=['bin/acrylamid'],
    package_data={
        'acrylamid.filters': ['hyph/*.txt'],
        'acrylamid.defaults': ['misc/*', 'xhtml/*', 'html5/*']},
    url='https://github.com/posativ/acrylamid/',
    license='BSD revised',
    description='yet another static blog generator',
    long_description=__doc__,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
    ],
    install_requires=[
        'Jinja2>=2.4',
        'Markdown>=2.0.1',
        'translitcodec>=0.2'
    ],
    tests_require=[
        'tox',
        'cram',
        'konira'
    ],
)
