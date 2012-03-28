Filters
=======

All transformations your content is done via filters. You an either set them
implicit in *conf.yaml* and/or overriding them in your individual blog posts.  A
filter can convert a Markdown-written text into HTML, render MathML from
AsciiMathML or just increase HTML-headers by one or two. You can specify a filter
by setting the key `filters` to a list of your wished filters, a string with only
one filter, or simply omit the key, if you've already defined a global filter:

::

    ---
    title: Samply Entry
    filters: [reST, hyphenate]
    ---

If you pass conflicting filters like ``reST, Markdown`` the first one gets
applied and every conflicing ignored. This is useful, when you define a global
filter *Markdown* but also write single entries in e.g. *reStructuredText*.  Most
inbuilt filters have aliases so you don't have to remember/write the exact name.
As an example, *rst*, *reST* and *restructuredtext* are aliases for
*reStructuredText*.

Some filters may take additional arguments to activate builtin filters like
Markdown's code-hilighting. Here's a list of all Markdon `built-in extensions
<http://freewisdom.org/projects/python-markdown/Available_Extensions>`_) and in
addition, acrylamid features a `asciimathml extension
<https://github.com/favalex/python-asciimathml>`_. The syntax is:

::

    filters: [markdown+mathml, ...]
    # or
    filters: [markdown+mathml+codehilite(css_class=highlight), ...]

You can also disable filters applied globally by prefixing them with *no*:

::

    filters: nosummary

A short word to filter evaluation. Internally, it is iterating over all
items in entry_filters+config_filters. If a filter conflicts with an
existing filter, it will overgone.

Built-in Filters
****************

Markdown
--------

:Requires:
    markdown or (python-markdown) -- already as a dependency implicitly installed

:Aliases:
    md, mkdown, markdown

:Conflicts:
    HTML, reStructuredText, Pandoc

:Arguments:
	asciimathml (mathml, math), ...

Lets write you using Markdown which simplifies HTML generation and is a lot
easier to write. The Markdown filter uses `the official implementation by John
Gruber <http://freewisdom.org/projects/python-markdown/>`_ and all it's
`available extensions
<http://www.freewisdom.org/projects/python-markdown/Available_Extensions>`_.
*Note*, `pygments <http://pygments.org>`_ is required for `codehilite
<http://freewisdom.org/projects/python-markdown/CodeHilite>`_.

XXX: cheat sheet

Acrylamid features an `AsciiMathML
<https://github.com/favalex/python-asciimathml>`_ extension. The aliases are:
*asciimathml*, *mathml* and *math* and requires the ``python-asciimathml``
package. Simply ``pip install asciimathml`` and you are done. *Note*, put
your formula into single dollar signs like ``$a+b^2$`` intead of two!

reStructuredText
----------------

:Requires:
	pygments, docutils (or python-docutils)

:Aliases:
    rst, rest, reST, restructuredtext

:Conflicts:
    HTML, Markdown, Pandoc

reStructuredText enables you to write in reStructuredText syntax instead of
HTML. reStructuredText is more powerful and reliable than Markdown but is also
slower and more difficult to write (but also easier than HTML).

XXX: cheat sheet

pandoc
------

:Requires:
    `Pandoc – a universal document converter <http://johnmacfarlane.net/pandoc/>`_ in PATH

:Conflicts:
    reStructuredText, HTML, Markdown

:Aliases:
    Pandoc, pandoc

:Arguments:
    First argument is the FORMAT like Markdown, textitle and so on. All arguments after that are applied as additional long-opts to pandoc.

This is filter is a universal converter for various markup language such as
Markdown, reStructuredText, Textile and LaTeX (including special extensions by
pandoc) to HTML. A typical call would look like ``filters:
[pandoc+Markdown+mathml+...]``. You can find a complete list of pandocs improved
(and bugixed) Markdown in the `Pandoc User's Guide
<http://johnmacfarlane.net/pandoc/README.html#pandocs-markdown>`_.

HTML
----

:Requires:
	<built-in>

:Conflicts:
	reStructuredText, Markdown, Pandoc

:Aliases:
	pass, plain, html, xhtml

No transformation will applied. Useful if your text is already written in
HTML.

h, head_offset
--------------

:Requires:
	<built-in>

:Aliases:
    h1, h2, h3, h4, h5

Increase HTML-headings (<h1>...</h1>) by h(x).

summarize
---------

:Requires:
	<built-in>

:Aliases:
	sum

:Arguments:
	Maximum words in summarize (an Integer)

:Defaults:
	summarize+200

Summarizes content to make listings of text previews (used for the default
tag/page view).

hyphenate
---------

:Requires:
	language patterns (comes pre-installed with `de`, `en` and `fr` patterns)

:Aliases:
    hyphenate, hyph

:Arguments:
    Minimum length before this filter hyphenates the word (smallest possible value is four).

:Defaults:
    hyphenate+10

Hyphenates words greater than 10 characters using Frank Liang's algorithm.
Hyphenation pattern depends on the language and should therefore
Only en, de and fr dictionary are provided by Acrylamid. Example usage:

::

    filters: [Markdown, hyphenate, ]
    lang: en

If you need an additional language, `download
<http://tug.org/svn/texhyphen/trunk/hyph-utf8/tex/generic/hyph-utf8/patterns/txt/>`_
both, ``hyph-*.chr.txt`` and ``hyph-*.pat.txt``, to
*\`sys.prefix\`/lib/python/site-packages/acrylamid/filters/hyph/*.

typography
----------

:Requires:
	`smartypants <https://code.google.com/p/typogrify/>`_

:Aliases:
    typography, typo, smartypants

:Arguments:
    all, typo, typogrify, amp, widont, smartypants, caps, initial_quotes,
    number_suffix

:Defaults:
	typography+amp+widont+smartypants+caps

Enables typographical transformation to your written content. This includes no
widows, typographical quotes and special css-classes for words written in CAPS
and & (ampersand) to render an italic styled ampersand. See the `original
project <https://code.google.com/p/typogrify/>`_ for more information.

By default *amp*, *widont*, *smartypants*, *caps* are applied. *all*, *typo*
and *typogrify* applying "widont, smartypants, caps, amp, initial_quotes". All
filters are applied in the order as they are written down.

acronyms
--------

:Requires:
    `<built-in>`

:Aliases:
    Acronyms, Acronym, acronyms, acronym

:Arguments:
    zero to N strings

:Defaults:
    no arguments

This filter is a direct port of `Pyblosxom's acrynoms plugin
<http://pyblosxom.bluesock.org/1.5/plugins/acronyms.html>`_, that marks acronyms
and abbreviations in your text based on either a built-in acronyms list or a
user-specified. To use a custom list just add the FILE to your conf.py like
this:

.. code-block:: python

    ACRONYMS_FILE = '/path/to/my/acronyms.txt'


The built-in list of acronyms differs from Pyblosxom's (see
`filters/acronyms.py <https://github.com/posativ/acrylamid/blob/master/acrylam
id/filters/acronyms.py>`_ on GitHub). See the `original description
<http://pyblosxom.bluesock.org/1.5/plugins/acronyms.html#building-the-
acronyms-file>`_ of how to make an acronyms file!

jinja2
------

:Requires:
    <built-in>

:Aliases:
    Jinja2, jinja2

In addition to HTML templating you can also use `Jinja2
<http://jinja.pocoo.org/docs/>`_ in your postings, which may be useful when
implementing a image gallery or other repeative tasks.

Within jinja you have a custom ``system``-filter which allows you to call
something like ``ls`` directly in your content (use it with care, when you
rebuilt this content, the output might differ).

::

    ---
    title: "Jinja2's system filter"
    filters: jinja2
    ---

    my ip address: {{ 'curl -s http://ifconfig.me/ip' | system }}.

Environment variables are the same as in :doc:`templating`.


Custom Filters
**************

Acrylamid can easily be extended with self-written filters inside your blog
directory (``filters/`` per default). Do write your own filter, take a look
at the code of `already existing filters
<https://github.com/posativ/acrylamid/acrylamid/filters>`_ shipped with
acrylamid and also visiting `doc: Extending Acrylamid`.
