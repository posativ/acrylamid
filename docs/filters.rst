Filters
=======

All transformations your content is done via filters. You an either set them
implicit in *conf.yaml* and/or overriding them in your individual blog posts.
A filter can convert a Markdown-written text into HTML, render MathML from
AsciiMathML or just increase HTML-headers by 1 or 2. You can specify a filter
by setting the key `filters` to a list of your wished filters or simply omit
the key, if you've already defined a global filter:

::

    ---
    title: Samply Entry
    filters: [reST, hyphenate]
    ---

If you pass conflicting filters like ``reST, Markdown`` the first one gets
applied and every conflicing ignored. This is useful, when you define a global
filter *Markdown* but also write single entries in e.g. *reStructuredText*.
Most inbuilt filters have aliases so you don't have to remember/write the
exact name. As an example, *rst*, *reST* and *restructuredtext* are aliases
for *reStructuredText*.

Some filters may take additional arguments to activate builtin filters like
Markdown's code-hilighting. Here's a list of all Markdon `built-in extensions
<http://freewisdom.org/projects/python-markdown/Available_Extensions>`_) and
in addition, acrylamid features a `asciimathml extension
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

Markdown
--------

:Requires:
    markdown or (python-markdown) -- already a dependency
	of acrylamid and implicitly installed

:Aliases:
    md, mkdown, markdown

:Conflicts:
    plain, reStructuredText

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
package. Simply ``pip install asciimathml`` and you are done. *Note*, place
your formula into single dollar signs like ``$a+b^2$`` intead of two!

reStructuredText
----------------

:Requires:
	pygments, docutils (or python-docutils)

:Aliases:
    rst, rest, reST, restructuredtext

:Conflicts:
    plain, Markdown

reStructuredText enables you to write in reStructuredText syntax instead of
HTML. reStructuredText is more powerful and reliable than Markdown but is also
slower and more difficult to write (but also easier than HTML).

XXX: cheat sheet

HTML
----

:Requires:
	built-in

:Conflicts:
	reStructuredText, Markdown

:Aliases:
	pass, plain, html, xhtml

No transformation will applied. Useful if your text is already written in
HTML.

head_offset
-----------

:Requires:
	built-in

:Aliases:
    h1, h2, h3, h4, h5

Increase HTML-headings (<h1>...</h1>) by h(x).

summarize
---------

:Requires:
	built-in

:Aliases:
	sum

:Arguments:
	Maximum words in summarize (an Integer)

:Defaults:
	200

Summarizes content to make listings of text previews (used for the default
tag/page view).

Hyphenate
---------

:Requires:
	language patterns (comes pre-installed with `de`, `en` and `fr` patterns)

:Aliases:
    hyphenate, hyph

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

Custom Filters
**************

Acrylamid can easily be extended with self-written filters inside your blog
directory (``filters/`` per default)
