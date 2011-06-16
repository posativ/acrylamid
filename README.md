lilith
======

lilith is yet another lightweight static blogging software. It is designed to be
easily extendable and offers a various number of built-in plugins.

lilith is licensed under the Common Development and Distribution License (CDDL).

Features
--------

- blog articles, pages and rss/atom feeds
- theming support (using [jinja2](http://jinjna.pocoo.org/))
- reStructuredText and Markdown as markup languages
- (currently only german) hyphenation using `&shy;`

Quickstart
----------

Cloning lilith using

    git clone git://github.com/posativ/lilith.git
    
and launch your favourite text editor on lilith.conf. Most items are
(hopefully) self-explaining, see [lilith.conf](#lilith.conf) for details. Edit
your preferences and starting blogging by writing plain text files into
the specified `entries_dir`. Open a terminal and run

    python lilith.py
    
which renders everything to `output_dir` (defaults to */out*). Use your favourite
file transfer software to upload the resulting static html and xml.


Using lilith
------------

lilith uses a flat file db to store the blog entries. It does not depend on a
specific filesystem structure, neither the user's structure has any effect on
the rendered output. Just specify a `entries_dir` in `lilith.conf`, lilith will
traverse this folder and processes all files in it.

An entry consists of two parts. First, a [YAML](http://en.wikipedia.org/wiki/YAML)-header
and the real content. Inside the YAML-header you must specify at least
a `title: My Title`. I recommend to use a `date: 21.12.2012, 16:47` key and
if you don't know, what markup-language you prefer or if you using different
markup languages in your blog, use e.g. `parser: rst`, too. See this
[sample entry][].

### lilith.conf

required keys:

- www_root: http://path.to/blog/
- ext_dir: [directies, holding your plugins]
- entries_dir: "directoy holding your entries"

- author: your name
- website: http://mywebsite.org/
- email: me@example.org
- blog_title: your website's title

optional keys:

- parser
- lang (de-DE, ...)
- items_per_page used for pagination, defaults to 6

How lilith works
----------------

lilith is heavily inspired by [PyBlosxom](http://pyblosxom.bluesock.org/) and
use its main idea: callbacks to be very flexible to end user.

... to be extended ...

[sample entry]: https://github.com/posativ/lilith/blob/ec41683a12f4b633d2154142e951e2d3e192f1c5/content/sample%20entry.txt