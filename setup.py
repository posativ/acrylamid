#!/usr/bin/env python
from distutils.core import setup

"""Welcome to Acrylamid's Documentation!
=====================================

Acrylamid is yet another lightweight static blogging software written in
python and designed to get a high quality output. Its licensed under BSD
Style, 2 clauses.

Features
--------

Acrylamid is a mixture of `nanoc <http://nanoc.stoneship.org/>`_, `Pyblosxom
<http://pyblosxom.bluesock.org/>`_ and `Pelican <http://pelican.notmyidea.org/>`_. It
features mainly:

- blog articles, simple pages, tags RSS/Atom feeds and an article overview
- theming support (using jinja2_) and support for jinja2 directly in postings
- Markdown_, reStructuredText_ and pandoc_
- MathML, modern web-typography and hyphenation using `&shy;`
- RSS/Atom import, deployment and a very handy CLI
- it's very flexible and fast

.. _jinja2: http://jinja.pocoo.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _pandoc: http://johnmacfarlane.net/pandoc/
.. _AsciiMathML: http://www1.chapman.edu/~jipsen/mathml/asciimath.html

Quickstart
----------

::

    easy_install -U acrylamid

You'll need ``python``, ``jinja2`` and either ``markdown`` (default) or
``docutils``. ``pygments`` and ``asciimathml`` for colored code listings
respectively MathML. Typography requires ``smartypants``. To get a
full-featured installation do:

::

    pip install docutils pygments asciimathml smartypants

Get acrylamid, edit *conf.py* and *layouts/* and run acrylamid with:

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
`posativ/blog.posativ.org <https://github.com/posativ/blog.posativ.org>`_. Take a
look at my *conf.py* for some inspiration.


Filters
-------

See `docs/filters.rst <http://acrylamid.readthedocs.org/en/latest/filters.html>`_ for
detailed information. Currently supported by acrylamid:

- **Markdown**: rendering Markdown (+asciimathml,pygments,built-in extensions)
- **reST**: reStructuredText (+pygments)
- **pandoc**: Pandoc (+Markdown,textitle,rst,...)
- **HTML**: don't render with Markdown, reStructuredText or Pandoc (it's a conflicting filter)

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
"""

setup(
    name='acrylamid',
    version='0.3.0',
    author='posativ',
    author_email='info@posativ.org',
    packages=['acrylamid', 'acrylamid.filters', 'acrylamid.views', 'acrylamid.lib'],
    scripts=['bin/acrylamid'],
    package_data={'acrylamid.filters': ['hyph/*.txt']},
    url='http://pypi.python.org/pypi/acrylamid/',
    license='BSD style',
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
)
