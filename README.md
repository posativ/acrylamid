Welcome to Acrylamid
====================

[![Build Status](https://travis-ci.org/farleykr/acrylamid.svg?branch=master)](https://travis-ci.org/farleykr/acrylamid)

This project is no longer maintained, use at your own risk. Or fork it.

*Notice:*

* don't try the master branch unless you are very sure about the not
  yet documented changes.
* PyPi releases (0.7.x) do not work with Python 3.3+ due dependency
  pinning. The upcoming 0.8 release will drop support for 3.2, but
  fully supports 3.3 and higher.
* yes, the name will change (still searching for a good name) and a
  transition from "static blog generator" to "static site generator"
  is already on my todo list.

Acrylamid is a mixture of [nanoc](http://nanoc.stoneship.org), [Pyblosxom](http://pyblosxom.github.io), and [Pelican](http://blog.getpelican.com)
licensed under BSD Style, 2 clauses. It is actively developed at
https://github.com/posativ/acrylamid/.

Why?
----

- it is really *fast* due incremental builds
- support for [Jinja2](http://jinja.pocoo.org/) and [Mako](http://www.makotemplates.org) templates
- many Markdown_ extensions and custom reStructuredText_ directives
- [MathML](http://www1.chapman.edu/~jipsen/mathml/asciimath.html) enhanced typography and hyphenation using soft-hyphens

Oh, and it can also generate a static blog with articles, static pages, tags,
RSS/Atom feeds (also per tag), article listing and a sitemap.

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

- [Markdown](http://daringfireball.net/projects/markdown/) and additional extensions (support for MathML_, deletion/insertion,
  sub- and supscript, syntax highlighting …)
- [reStructuredText](http://docutils.sourceforge.net/rst.html) with directives for syntax highlighting and youtube video
  embedding
- [textile](https://en.wikipedia.org/wiki/Textile_%28markup_language%29), [discount](http://www.pell.portland.or.us/~orc/Code/discount/), all dialects supported by [pandoc](http://johnmacfarlane.net/pandoc/) and plain HTML

You miss one? Extend Acrylamid in [less than 30 LoC](https://posativ.org/git/acrylamid/blob/master/acrylamid/filters/pytextile.py)_!

other filters

- support for Jinja2 and Mako directly in postings (before they get processed)
- [typography](https://code.google.com/p/typogrify/) (and [smartypants](http://daringfireball.net/projects/smartypants/))
- TeX hyphenation
- summarize ability
- [acronym detection](http://pyblosxom.github.io/Documentation/1.5/plugins/acronyms.html)  that automatically replace acronyms and abbreviations
- [liquid plugins](http://octopress.org/docs/plugins/) ported from [Octopress](http://octopress.org/)


blogging features

- you like the [YAML front matter](https://github.com/mojombo/jekyll/wiki/YAML-Front-Matter) from [Jekyll](http://jekyllrb.com/) or [nanoc](http://nanoc.stoneship.org/)? First choice in Acrylamid!
- coming from Pelican_? Acrylamid has also support for metadata in the native
  format of Markdown, reStructuredText and even Pandoc.
- support for translations (oh, and did I mention the language dependend
  hyphenation feature?).
- a few HTML5 themes, see [Theming](http://posativ.org/acrylamid/theming.html)
- internal webserver with automatic compiling when something has changed.
- assets management, including [LESS](http://lesscss.org/) and [SASS](http://sass-lang.com/) conversion.
- uni-directional PingBack support.
- static site search.

Quickstart

    easy_install -U acrylamid

This installs Acrylamid with Jinja2_ as templating engine. For Mako use:
    
    easy_install -U acrylamid[mako]
    
This installs two additional but not required dependencies: `Markdown` and `translitcodec`. To get a list of all supported modules, head over to [additional supported modules](http://posativ.org/acrylamid/installation.html#additional-supported-modules).

If you rather use non-ascii characters, you're better off with:

    easy_install -U acrylamid python-magic unidecode

Initialize the base structure, edit *conf.py* and *layouts/* and compile with:

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

- [Practicing web development](http://www.vlent.nl/) – Mark van Lent
  [source <https://github.com/markvl/www.vlent.nl>]

- [mecker. mecker. mecker. ](http://blog.posativ.org) – Martin Zimmermann
  [source https://github.com/posativ/blog.posativ.org/]

- [Groovematic](http://groovematic.com/) – Isman Firmansyah
  [`source https://github.com/iromli/groovematic]

- [Christoph Polcin](http://www.christoph-polcin.com/) – Christoph Polcin
  [source http://git.christoph-polcin.com/blog/, theme http://git.christoph-polcin.com/acrylamid-theme-bipolar/]

- [Knitatoms](http://knitatoms.net) – Tom Atkins
  [source https://github.com/knitatoms/knitatoms.net]

- [blubee.me](http://blubee.me) – Owen Hogarth
  [source https://github.com/teamblubee/http-blubee.me]

Commands
--------

See [commands](https://posativ.org/acrylamid/commands.html) for a detailed
overview.

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

Join ``#acrylamid`` on [Freenode](http://freenode.net/)! If you found a bug, please report it on
[GitHub Issues](https://github.com/posativ/acrylamid/issues?state=open). The project has also a mailing list [Archive_], just send
an email to [acrylamid@librelist.com](http://librelist.com/browser/acrylamid/) and you have subscribed.
