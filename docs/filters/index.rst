Filters
=======

All text transformations are done with filters. You can think of a filter as a
UNIX pipe: text goes in, magic happens, text goes out. You can chain filters,
of course. In Acrylamid a filter can convert Markdown into HTML, render MathML
from AsciiMathML, apply typographical enhancements or just increase headings
by an offset.


Usage
*****

There are three ways to apply filters: global_, per view_ and per entry_.
During compilation, all filters will be chained, conflicting filters such as
:abbr:`reST (reStructuredText)` and Markdown at the same time are removed and
then ordered by internal priorities [#]_. Each entry evaluates its own filter
chain.

Acrylamid defines a filter as a simple object containing one or more
identifiers [#]_ and also has a list of filters that would conflict with this
filter. Below you can find a complete list of all built-in filters.

.. _global:

global : [HTML, Markdown, ...]
    If you prefer Markdown as markup language, you can set this as default
    filter like ``FILTERS = [Markdown, ]`` in your :doc:`conf.py <conf.py>`.

.. _view:

view : HTML or [Markdown, summarize, ...]
    Apply filters to specific views. For example you can provide a summarized
    feed.

    .. code-block:: python

        '/rss/': {'view': 'rss', filters: 'summarize'}

.. _entry:

entry : Jinja2 or [reST, ...]
    Switch between Markdown and reStructuredText? Use one of them as default
    filter but override it in the given article's metadata. For convenience
    both "filter" and "filters" can be used as key. An example YAML front
    matter::

        ---
        title: Test
        filter: reST
        ---

    Now if your default filter converts Markdown, this article uses reST.

.. [#] the evaluation order depends on an internal priority value for each
   filter so we don't confuse our users or produce unexpected behavior.

.. [#] an identifier is the name you use to enable this specific filter, most
   filters have multiple aliases for the same filter, like "reStructuredText"
   which you can also enable with "rst" or "reST".


Additional Arguments
--------------------

Filters may take additional arguments to use extensions like Markdown's
code-hilighting. Not every filter supports additional arguments, please
refer to the actual filter documentation.

**Examples**

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

Disabling Filters
-----------------

Sometimes it is useful to disable filters per entry or per view. You can annul
filters you have applied globally in per view filters or entry metadata. The
syntax is the filter name (without any arguments) prefixed with "no":

::

    filters: nosummary


Built-in Filters
****************

Acrylamid ships with good maintained filters but you are not restricted only to
them. Simply create a directory like *filters/* and add ``FILTERS_DIR +=
['filters/']`` to your *conf.py* and use your own filters. See
:ref:`custom-filters`.

A quick note to the following tables:

- *Requires* indicates what you have to install to use this filter.
- *Alias* is a list of alternate identifiers to this filter.
- *Conflicts* shows what filters don't work together (does not conflict if
  empty).
- *Arguments* what arguments you can apply to this filter.


Markdown
--------

Lets you write using Markdown which simplifies HTML generation and is a lot
easier. The Markdown filter uses `the official implementation by John Gruber
<http://freewisdom.org/projects/python-markdown/>`_ and all it's `available
extensions`_. *Note* that pygments_ is required for codehilite_.

Here's an online service converting Markdown to HTML and providing a handy
cheat sheet: `Dingus <http://daringfireball.net/projects/markdown/dingus>`_.

Acrylamid features some additional extension:

- inline math via AsciiMathML_. The aliases are: *asciimathml*, *mathml* and
  *math* and require the ``python-asciimathml`` package. *Note* put your formula
  into single dollar signs like ``$a+b^2$``!
- super_ und subscript_ via *sup* or *superscript* as well as *sub* or
  *subscript*. The syntax for subscript is ``H~2~O`` and for superscript
  ``a^2^``.
- `deletion and insertion`_ syntax via *delins*. The syntax is ``~~old~~`` and
  ``++new``.
- `GitHub:Gist <https://gist.github.com/>`__ embedding via ``[gist: id]`` and
  optional with a filename ``[gist: id filename]``. You can use ``[gistraw:
  id [filename]]`` to embed the raw text without JavaScript.

.. _available extensions: http://www.freewisdom.org/projects/python-markdown/Available_Extensions
.. _codehilite: http://freewisdom.org/projects/python-markdown/CodeHilite
.. _pygments: http://pygments.org/
.. _AsciiMathML: https://github.com/favalex/python-asciimathml
.. _super: https://github.com/sgraber/markdown.superscript
.. _subscript: https://github.com/sgraber/markdown.subscript
.. _deletion and insertion: https://github.com/aleray/mdx_del_ins

============  ====================================================
Requires      ``markdown`` or (``python-markdown``) -- already
              as a dependency implicitly installed
Aliases       md, mkdown, markdown
Conflicts     HTML, reStructuredText, Pandoc
Arguments     asciimathml, sub, sup, delins, gist, gistraw
              <built-in extensions>
============  ====================================================


reStructuredText
----------------

See :doc:`rst`.

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


Discount
--------

`Discount`__ -- a C implementation of John Gruber's Markdown including
definition lists, pseudo protocols and `Smartypants`__ (makes typography_
obsolete).

__ http://www.pell.portland.or.us/~orc/Code/discount/#smartypants
__ http://www.pell.portland.or.us/~orc/Code/discount/


============  =========================================================
Requires      `discount <https://github.com/trapeze/python-discount>`_
Aliases       Discount, discount
Conflicts     reStructuredText, Markdown, Pandoc, PyTextile, Typography
============  =========================================================


HTML
----

No transformation applied. Useful if your text is already written in HTML.

============  ==================================================
Requires      <built-in>
Aliases       pass, plain, html, xhtml, HTML
Conflicts     reStructuredText, Markdown, Pandoc
============  ==================================================


Liquid
------

Implementation of most plugins of the Jekyll/Octopress project. This filter
(unfortunately) can not be used with reST or any other markup language, that
can not handle inline HTML.

The liquid filters are useful of you are migrating from Jekyll/Octopress or
look for an inofficial standard (rather than custom Markdown extensions) that
is used by Jekyll_/Octopress_, Hexo_.

.. _Jekyll: https://github.com/mojombo/jekyll/wiki/Liquid-Extensions#tags
.. _Octopress: http://octopress.org/docs/plugins/
.. _Hexo: http://zespia.tw/hexo/docs/tag-plugins.html

Currently, the following tags are ported (I reference the Octopress plugin
documentation for usage details):

- blockquote__ -- generate beautiful, semantic block quotes
- img__ -- easily post images with class names and titles
- youtube__ -- easy embedding of YouTube videos
- pullquote__ -- generate CSS only pull quotes — no duplicate data, no javascript
- tweet__ -- embed tweets using Twitter's oEmbed API

__ http://octopress.org/docs/plugins/blockquote/
__ http://octopress.org/docs/plugins/image-tag/
__ http://www.portwaypoint.co.uk/jekyll-youtube-liquid-template-tag-gist/
__ http://octopress.org/docs/plugins/pullquote/
__ https://github.com/scottwb/jekyll-tweet-tag

If you need another plugin, just ask on `GitHub:Issues
<https://github.com/posativ/acrylamid/issues>`_ (plugins that will not
implemented in near future: Include Array, Render Partial, Code Block).

============  ==================================================
Requires      <built-in>
Aliases       liquid, octopress
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

Summarizes content to make listings of text previews (used in tag/page by
default). You can customize the ellipsis, CSS-class, link-text and the
behaviour how the link appears in your :doc:`conf.py`. You can override the
maximum words per entry using ``summarize.maxwords: 10`` in your metadata.

With ``<!-- break -->`` you can end the summarizing process preliminary. For
convenience ``excerpt``, ``summary`` and ``more`` will also work as keyword.

============  ==================================================
Requires      <built-in>
Aliases       sum
Arguments     Maximum words in summarize (an Integer), defaults
              to ``summarize+200``.
============  ==================================================

You can define the following additional :doc:`conf.py` parameters for the
summarize filter. You can overwrite all configuration values per entry
with ``summarize.link``, ``summarize.mode`` and ``summarize.ignore``.

SUMMARIZE_MODE : an integer value

    * 0 -- inject the link directly after the tag, which content has
      exceeded maxwords.
    * 1 -- inject link after certain blacklisted tags such as ``pre``, ``a``
      and ``b`` to avoid accidental miss-interpretion of the continuation link.
    * 2 -- close currently open tags and insert link afterwards.

SUMMARIZE_LINK : a continuation string with a ``%s`` inside

    String template for the continue reading link. Default uses an ellipsis
    (three typographical dots, …), a link with the css class ``continue`` and
    the text ``continue`` and a single dot afterwards. This string must contain
    ``%s`` where the link location will be inserted.

SUMMARIZE_IGNORE : a list of tags

    Ignores given self-closed HTML tags in the output generation, defaults to
    ``['img', 'video', 'audio']``. With ``[]`` you can disable this behavior.

intro
-----

This filter is an alternative to the summarize filter mentioned above.
With the latter it is harder to control what is shown in the entry
listings; sometimes headings also appear in the summary if the first
paragraph is short enough. This filter shows only up to N paragraphs.

You can overwrite the amount of paragraphs shown in each entry using
``intro.maxparagraphs: 3`` in the metadata section.

============  ==================================================
Requires      <built-in>
Arguments     Maximum paragraphs (an Integer), defaults
              to ``intro+1``.
============  ==================================================

Additional :doc:`conf.py` parameters for the introduction filter. You can
overwrite both configuration values per entry with ``intro.link`` and
``intro.ignore`` respectively.

INTRO_LINK : a string (may be empty)

    Same default value and usage like the ``SUMMARIZE_LINK`` but you can
    disable the intro link output, by setting ``INTRO_LINK=''``.

INTRO_IGNORE : a list of tags

    see ``SUMMARIZE_IGNORE``


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
and *typogrify* applyies *widont*, *smartypants*, *caps*, *amp*, *initial_quotes*.
All filters are applied in the order as they are written down.

.. code-block:: python

    TYPOGRAPHY_MODE = "2"  # in your conf.oy

`Smarty Pants`_ has modes that let you customize the modification. See `their
options`_ for reference. Acrylamid adds a custom mode ``"a"`` that behaves like
``"2"`` but does not educate dashes like ``--bare`` or ``bare--``.

.. _Smarty Pants: http://web.chad.org/projects/smartypants.py/
.. _their options: http://web.chad.org/projects/smartypants.py/#options

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

    You can find my previous article "{{ env.prev.title }}" here_. Not
    interesting enough? How about lorem ipsum?

    {{ lipsum(5) }}

    .. _here: {{ env.prev }}

Environment variables are the same as in :doc:`templating` plus some imported
modules from Python namely: ``time``, ``datetime`` and ``urllib`` because you
can't import anything from Jinja2. You can also access the root templating
environment when Jinja2. This means, you can import and inherit from templates
located in your theme folder.

For convenience, the Jinja2 filter automatically imports every macro from
``macros.html`` into your post context, so there is no need for a
``{% from 'macros.html' import foo %}``.

============  ==================================================
Requires      <built-in>
Aliases       Jinja2, jinja2
============  ==================================================


Mako
----

Just like Jinja2 filtering but using Mako. You have also ``system`` filter
available within Mako. Unlike Jinja2 Mako can import python modules during
runtime, therefore no additional modules are imported into the namespace.

============  ==================================================
Requires      `mako <http://docs.makotemplates.org/>`_
Aliases       Mako, mako
============  ==================================================


relative
--------

Some extension may generate relative references such as footnotes. While this
is a good practise, it can get ambiguous when multiple posts with footnotes
are included in an overview such as the index view does it. This ambiguity
can be easily solved with the *relative* filter.

============  ==================================================
Requires      <built-in>
Aliases       relative
============  ==================================================


absolute
--------

This also applies to feeds and many feed readers can't/won't resolve relative
urls. This is where the *absolute* filter comes into play. This filter just
expands a relative path to a valid URI. **Important:** if you ever change your
domain, you have to force compilation otherwise this filter won't notice this
change

============  ==================================================
Requires      <built-in>
Aliases       absolute
============  ==================================================


strip
-----

Strip tags and attributes from HTML to produce a clean text version. Primary
used by the static site search.  By default, this filter includes everything
between ``<tag>...</tag>`` but you can supply additional arguments to remove
code listings wrapped in ``<pre>`` from the site search.

============  ==================================================
Requires      <built-in>
Aliases       strip
Arguments     ignored tags (such as ``pre``)
============  ==================================================

Priorities
**********

  * 90.0-80.0 : pre
      Jinja2, Mako, Liquid
  * 70.0 : markup
      HTML, Markdown, pandoc, reST, textile
  * 50.0 : default
      metalogo, head_offset
  * 25.0 : post
      typography
  * 20.0 : post (conflict with typography)
      acronyms, hyphenate
  * 15.0 : shorten HTML
      intro, summarize
  * 10.0 : fix links
      relative, absolute
  *  0.0 : last
      strip

.. _custom-filters:

Custom Filters
**************

To write your own filter, take a look at the code of `already existing filters
<https://github.com/posativ/acrylamid/tree/master/acrylamid/filters>`_ shipped with
acrylamid and also visit :doc:`extending`.
