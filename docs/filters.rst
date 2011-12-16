Filters
=======

All transformations of the entries' content is done with filters. You an
either set them for the whole blog in *conf.yaml* and/or override them in blog
posts individually. The keyword in the YAML-header is `filters` (though, a
*filter* without s would work to). The most basic configuration would be:

::

    ---
    title: My Entry
    filters: reST
    ---

You can specify multiple filters, too:

::

    filters: reST, sumarize
    
If you pass conflicting filters like ``reST, Markdown`` the first one wins. This
is useful, when you define as overall filter *Markdown* but want to write a single
entry in *reStructuredText*. Filters can also have aliases. Therefore, *rst*,
*reST* and *reStructuredText* will call the *reStructuredText* filter.

Some filters can also take additional arguments, e.g. *Markdown* includes an
`asciimathml extension <https://github.com/favalex/python-asciimathml>`_ (and
of course all `built-in extensions <http://freewisdom.org/projects/python-markdown/Available_Extensions>`_).
The syntax for this is:

::

    filters: markdown+mathml, ...
    # or
    filters: markdown+codehilite(css_class=highlight), ...

You can also disable filters applied via *conf.yaml* by simply add *no* to
the name disables the filter for this current entry:

::

    filters: nosummary

A short word to filter evaluation. Internally, it's simply an iterating over
all elements of entry_filters+config_filters. If a filter conflicts with an
existing filter, it will overgone.

Markdown
********

aliases:
    md, mkdown, markdown
conflicts:
    plain, reStructuredText
arguments:
    asciimathml

Markdown uses `the official implementation by John Gruber <http://www.freewisdom.org/projects/python-markdown/>`_
and all it's `available extensions <http://www.freewisdom.org/projects/python-markdown/Available_Extensions>`_.
*Note*, `pygments <http://pygments.org>`_ is required for `codehilite <http://www.freewisdom.org/projects/python-markdown/CodeHilite>`_.

Acrylamid includes an `AsciiMathML <https://github.com/favalex/python-asciimathml>`_
extension. The aliases are: *asciimathml*, *mathml* and *math* and requires
``python-asciimathml`` as well. Simply ``pip install asciimathml`` and you are done.
Note, place your formula into single dollar signs like ``$a+b^2$`` intead of two!

reStructuredText
****************

*needs pygments to be installed*!

aliases:
    rst, rest, reST, restructuredtext
conflicts:
    plain, mkdown
    
Install ``reStructuredText`` via ``pip install docutils``. Currently only a
hard-coded `pygments <http://pygments.org>`_ extension.

plain
*****

No transformation applied. Useful if your text is already HTML and you don't
trust Markdown's "don't touch html"-policy.

head_offset
***********

aliases:
    h1, h2, h3, h4, h5

Increase headings by h(x).

Hyphenate
*********

aliases:
    hyphenate, hyph

Hyphenate HTML based on entry's/blog's lang. Only en, de and fr dictionary are
provided by Acrylamid. Example usage:

::

    filters: hyphenate
    lang: en

If you need an additional language, `download
<http://tug.org/svn/texhyphen/trunk/hyph-utf8/tex/generic/hyph-utf8/patterns/txt/>`_
both, ``hyph-*.chr.txt`` and ``hyph-*.pat.txt``, to
*\`sys.prefix\`/lib/python/site-packages/acrylamid/filters/hyph/*.

typography
**********

*needs smartypants*!

aliases:
    typography, typo, smartypants
arguments:
    all, typo, typogrify, amp, widont, smartypants, caps, initial_quotes,
    number_suffix

Brings some typography to your content. This includes no widows, correct
quotes and special css-classes for words written as CAPS (sophisticated
recognition) and & (ampersand). See `original project
<https://code.google.com/p/typogrify/>`_.

By default *amp*, *widont*, *smartypants*, *caps* are applied. *all*, *typo*
and *typogrify* applying "widont, smartypants, caps, amp, initial_quotes". All
filters are applied in the order as they are written down.
