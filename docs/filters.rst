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
********

:Requires:
    markdown or (python-markdown) -- already a dependency
	of acrylamid and implicitly installed

:Aliases:
    md, mkdown, markdown

:Conflicts:
    plain, reStructuredText

:Arguments:
	asciimathml (mathml, math), ...

Markdown uses `the official implementation by John Gruber
<http://www.freewisdom.org/projects/python-markdown/>`_ and all it's
`available extensions
<http://www.freewisdom.org/projects/python-markdown/Available_Extensions>`_.
*Note*, `pygments <http://pygments.org>`_ is required for `codehilite
<http://www.freewisdom.org/projects/python-markdown/CodeHilite>`_.

Acrylamid includes a specia `AsciiMathML
<https://github.com/favalex/python-asciimathml>`_ extension. The aliases are:
*asciimathml*, *mathml* and *math* and requires the ``python-asciimathml``
package. Simply ``pip install asciimathml`` and you are done. *Note*, place
your formula into single dollar signs like ``$a+b^2$`` intead of two!

reStructuredText
****************

*needs pygments to be installed*!

:Requires:
	pygments, docutils (or python-docutils)

:Aliases:
    rst, rest, reST, restructuredtext

:Conflicts:
    plain, Markdown
    
Install ``reStructuredText`` via ``pip install docutils``. Currently only a
hard-coded `pygments <http://pygments.org>`_ extension.

plain
*****

No transformation applied. Useful if your text is already HTML and you don't
trust Markdown's "don't touch html"-policy.

head_offset
***********

:Aliases:
    h1, h2, h3, h4, h5

Increase HTML-headings (<h1>...</h1>) by h(x).

Hyphenate
*********

:Aliases:
    hyphenate, hyph

Hyphenate HTML based on entry's/blog's lang. Only en, de and fr dictionary are
provided by Acrylamid. Example usage:

::

    filters: [hyphenate, ]
    lang: en

If you need an additional language, `download
<http://tug.org/svn/texhyphen/trunk/hyph-utf8/tex/generic/hyph-utf8/patterns/txt/>`_
both, ``hyph-*.chr.txt`` and ``hyph-*.pat.txt``, to
*\`sys.prefix\`/lib/python/site-packages/acrylamid/filters/hyph/*.

typography
**********

:Requires:
	smartypants

:Aliases:
    typography, typo, smartypants

:Arguments:
    all, typo, typogrify, amp, widont, smartypants, caps, initial_quotes,
    number_suffix

Brings some typography to your content. This includes no widows, correct
quotes and special css-classes for words written as CAPS (sophisticated
recognition) and & (ampersand). See `original project
<https://code.google.com/p/typogrify/>`_.

By default *amp*, *widont*, *smartypants*, *caps* are applied. *all*, *typo*
and *typogrify* applying "widont, smartypants, caps, amp, initial_quotes". All
filters are applied in the order as they are written down.
