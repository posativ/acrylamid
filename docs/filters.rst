Filters
=======

All transformations of your content is done via filters. You an either set them
implicit in *conf.yaml* and/or overriding them in your individual blog entries.
A filter can convert a Markdown-written text into HTML, render MathML from
AsciiMathML, apply typographical enhancements or simply increase HTML-headers by
one or two.

To apply filters implicit, you set *FILTERS* to a list (or a single string) of
filters. Next to global filters we have implicit per-view filters that inherit
from global FILTERS. Implicit means *parent* applied if you don't override them
with conflicting filters or explicitly disable them by adding "no" to the filter
name.

Acrylamid defines a filter as a simple object containing one or more identifiers
[#]_ and also has a list of filters that would conflict with this filter. For
example you write your text using :abbr:`reST (reStructuredText)` but sometimes
you prefer Markdown's less-verbose syntax. Then you can set a (per-view or
global) filter to render all text with reST but set in chosen articles
"``filter: Markdown``" and the Markdown-filter will automatically remove
conflicting ones.

The order of choosing filters is *entry* -- *view* -- *global*, but that's *not*
the actual evaluation order when we apply these filters [#]_.

Some filters may take additional arguments to activate builtin filters like
Markdown's code-hilighting. Not every filter supports additional arguments,
please refer to the next section for details.

**Examples:**

A normal usage of explicit filters in an article:

::

    ---
    title: We write reStructuredText
    filters: [reST, hyphenate]
    ---

    With reStructuredText I can write :math:`x^2`, that's pretty cool, eh?

Filters with arguments:

::

    filters: [markdown+mathml, summarize+100]
    filters: [markdown+mathml+codehilite(css_class=highlight), ...]

Disabling a filter:

::

    filters: nosummary

The next section gives you complete details of all properties, dependencies and
extensions by Acrylamid. So continue reading!

.. [#] an identifier is the name you use to enable this specific filter, most
   filters have multiple aliases for the same filter, like "reStructuredText"
   which you can also enable with "rst" or "reST".

.. [#] the evaluation order depends on the internal priority value of each
   filter so we don't confuse our users or produce unexpected behavior.

Built-in Filters
****************

Acrylamid ships with good maintained filters but you are not restricted only to
them. Simply create a directory like *filters/* and add ``FILTERS_DIR +=
['filters/']`` to your *conf.py* and use your own filters. See
:ref:`custom-filters`.

A quick note to the following tables:

- *Requires* indicates what you have to install to use this filter
- *Alias* is a list of alternate identifiers to this filter
- *Conflicts* shows what filters don't work together (does not conflict if empty)
- *Arguments* what arguments you can apply to this filter

Markdown
--------

Lets write you using Markdown which simplifies HTML generation and is a lot
easier to write. The Markdown filter uses `the official implementation by John
Gruber <http://freewisdom.org/projects/python-markdown/>`_ and all it's
`available extensions`_. *Note* that pygments_ is required for codehilite_.

Here's an online service converting Markdown to HTML and providing a handy
cheat sheet: `Dingus <http://daringfireball.net/projects/markdown/dingus>`_.

Acrylamid features an AsciiMathML_ extension. The aliases are: *asciimathml*,
*mathml* and *math* and requires the ``python-asciimathml`` package. *Note* put
your formula into single dollar signs like ``$a+b^2$``!

.. _available extensions: http://www.freewisdom.org/projects/python-markdown/Available_Extensions
.. _codehilite: http://freewisdom.org/projects/python-markdown/CodeHilite
.. _pygments: http://pygments.org/
.. _AsciiMathML: https://github.com/favalex/python-asciimathml

============  ==================================================
Requires      ``markdown`` or (``python-markdown``) -- already
              as a dependency implicitly installed
Aliases       md, mkdown, markdown
Conflicts     HTML, reStructuredText, Pandoc
Arguments     asciimathml (mathml, math), <built-in extensions>
============  ==================================================


reStructuredText
----------------

reStructuredText lets you write (like the name says) in reStructuredText syntax
instead of HTML and is more powerful and reliable than Markdown but also slower
and slightly more difficult to use. See their quickref_ for syntax details.

Using a decent version of ``docutils`` (:math:`\geq 0.8`) let you also write
`inline math`_ with a subset of LaTeX math syntax, so there is no need of an
additional extension like in Markdown. In addition to all standard builtin
directives, acrylamid offers three additional one:

.. _quickref: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _inline math: http://docutils.sourceforge.net/docs/ref/rst/directives.html#math

- `Pygments <http://pygments.org/>`_ syntax highlighting via ``code-block``,
  ``sourcecode`` or   ``pygments``. Here's   an example (``linenos`` enables
  line numbering):

  .. code-block:: restructuredtext

        .. code-block:: python
          :linenos:

          #!/usr/bin/env python
          print "Hello World!

- JavaScript-enabled syntax highlighting via ``code`` and additional scripts:

  .. code-block:: restructuredtext

      .. source:: python

         #!/usr/bin/env python
         print "Hello, World!"

      .. raw:: html

          <script type="text/javascript" src="http://alexgorbatchev.com/pub/sh/current/scripts/shCore.js"></script>
          <script type="text/javascript" src="http://alexgorbatchev.com/pub/sh/current/scripts/shBrushPython.js"></script>
          <link type="text/css" rel="stylesheet" href="http://alexgorbatchev.com/pub/sh/current/styles/shCoreDefault.css"/>
          <script type="text/javascript">SyntaxHighlighter.defaults.toolbar=false; SyntaxHighlighter.all();</script>

- YouTube directive for easy embedding (`:options:` are optional).

  .. code-block:: restructuredtext

      .. youtube:: ZPJlyRv_IGI
         :start: 34
         :align: center
         :height: 1280
         :width: 720
         :ssl:

============  ==================================================
Requires      ``docutils`` (or ``python-docutils``), optional
              ``pygments`` for syntax highlighting
Aliases       rst, rest, reST, restructuredtext
Conflicts     HTML, Markdown, Pandoc
============  ==================================================


textile
-------

A *textile* filter if like the textile_ markup language. Note, that the `python
implementation`_ of Textile has been not actively maintained for more than a
year. Textile is the only text processor so far that adds some typographical
enhancements automatically (but not every applied via :ref:`typography`).

.. _textile: https://en.wikipedia.org/wiki/Textile_%28markup_language%29
.. _python implementation: https://github.com/sebix/python-textile

============  ==================================================
Requires      ``textile``
Aliases       Textile, textile, pytextile, PyTextile
Conflicts     HTML, Markdown, Pandoc, reStructuredText
============  ==================================================


pandoc
------

This is filter is a universal converter for various markup language such as
Markdown, reStructuredText, Textile and LaTeX (including special extensions by
pandoc) to HTML. A typical call would look like ``filters:
[pandoc+Markdown+mathml+...]``. You can find a complete list of pandocs
improved (and bugfixed) Markdown implementation in the `Pandoc User's Guide
<http://johnmacfarlane.net/pandoc/README.html#pandocs-markdown>`_.

============  ==================================================
Requires      `Pandoc – a universal document converter
              <http://johnmacfarlane.net/pandoc/>`_ in PATH
Aliases       Pandoc, pandoc
Conflicts     reStructuredText, HTML, Markdown
Arguments     First argument is the FORMAT like Markdown,
              textile and so on. All arguments after that are
              applied as additional long-opts to pandoc.
============  ==================================================


HTML
----

No transformation applied. Useful if your text is already written in HTML.

============  ==================================================
Requires      <built-in>
Aliases       pass, plain, html, xhtml, HTML
Conflicts     reStructuredText, Markdown, Pandoc
============  ==================================================


h, head_offset
--------------

This filter increases HTML headings tag by N whereas N is the suffix of
this filter, e.g. ``h2`` increases headers by two.

============  ==================================================
Requires      <built-in>
Aliases       h1, h2, h3, h4, h5
============  ==================================================


summarize
---------

Summarizes content to make listings of text previews (used in tag/page by default).
You can customize the ellipsis, CSS-class, link-text and the behaviour how the link
appears in your :doc:`conf.py`.
You can override single or all configurations made in :doc:`conf.py` with
``summarize.maxwords: 10`` and so on in the entry header.

============  ==================================================
Requires      <built-in>
Aliases       sum
Arguments     Maximum words in summarize (an Integer), defaults
              to ``summarize+200``.
============  ==================================================


hyphenate
---------

Hyphenates words greater than 10 characters using Frank Liang's algorithm.
Hyphenation pattern depends on the current language of an article (defaulting
to system's locale). Only en, de and fr dictionaries are provided by
Acrylamid. Example usage:

::

    filters: [Markdown, hyphenate, ]
    lang: en

If you need an additional language, `download
<http://tug.org/svn/texhyphen/trunk/hyph-utf8/tex/generic/hyph-utf8/patterns/txt/>`_
both, ``hyph-*.chr.txt`` and ``hyph-*.pat.txt``, to
*\`sys.prefix\`/lib/python/site-packages/acrylamid/filters/hyph/*.

============  ==================================================
Requires      language patterns (ships with `de`,  `en` and
              `fr` patterns)
Aliases       hyphenate, hyph
Arguments     Minimum length before this filter hyphenates the
              word (smallest possible value is four), defaults
              to ``hyphenate+10``.
============  ==================================================

.. _typography:

typography
----------

Enables typographical transformation to your written content. This includes no
widows, typographical quotes and special css-classes for words written in CAPS
and & (ampersand) to render an italic styled ampersand. See the `original
project <https://code.google.com/p/typogrify/>`_ for more information.

By default *amp*, *widont*, *smartypants*, *caps* are applied. *all*, *typo*
and *typogrify* applying "widont, smartypants, caps, amp, initial_quotes". All
filters are applied in the order as they are written down.

============  ==================================================
Requires      `smartypants <https://code.google.com/p/typogrify/>`_
Aliases       typography, typo, smartypants
Arguments     all, typo, typogrify, amp, widont, smartypants,
              caps, initial_quotes, number_suffix. Defaults to
              ``typography+amp+widont+smartypants+caps``.
============  ==================================================


acronyms
--------

This filter is a direct port of `Pyblosxom's acrynoms plugin
<http://pyblosxom.bluesock.org/1.5/plugins/acronyms.html>`_, that marks acronyms
and abbreviations in your text based on either a built-in acronyms list or a
user-specified. To use a custom list just add the FILE to your conf.py like
this:

::

    ACRONYMS_FILE = '/path/to/my/acronyms.txt'

The built-in list of acronyms differs from Pyblosxom's (see
`filters/acronyms.py <https://github.com/posativ/acrylamid/blob/master/acrylam
id/filters/acronyms.py>`_ on GitHub). See the `original description
<http://pyblosxom.bluesock.org/1.5/plugins/acronyms.html#building-the-
acronyms-file>`_ of how to make an acronyms file!

============  ==================================================
Requires      <built-in>
Aliases       Acronym(s), abbr (both case insensitive)
Arguments     zero to N keys to use from acronyms file, no
              arguments by default (= all acronyms are used)
============  ==================================================


jinja2
------

In addition to HTML+jinja2 templating you can also use `Jinja2
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

    Take a look at my code:

    .. code-block:: python

        {{ "cat ~/work/project/code.py" | system | indent(4) }}

Environment variables are the same as in :doc:`templating`.

============  ==================================================
Requires      <built-in>
Aliases       Jinja2, jinja2
============  ==================================================

.. _custom-filters:

Custom Filters
**************

To write your own filter, take a look at the code of `already existing filters
<https://github.com/posativ/acrylamid/acrylamid/filters>`_ shipped with
acrylamid and also visit :doc:`extending`.
