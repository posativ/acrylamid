Postprocessors
==============

Filters that are executed after compiling the markup language to HTML are
called postprocessors.

.. _filters-post-headoffset:

h, head_offset
--------------

This filter increases HTML headings tag by N whereas N is the suffix of
this filter, e.g. ``h2`` increases headers by two.

============  ==================================================
Requires      <built-in>
Aliases       h1, h2, h3, h4, h5
============  ==================================================

.. _filters-post-summarize:

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

SUMMARIZE_LINK : a continuation string. If a ``%s`` is present the link
                 location will be inserted.

    String template for the continue reading link. Default uses an ellipsis
    (three typographical dots, …), a link with the css class ``continue`` and
    the text ``continue`` and a single dot afterwards. This string can
    optionally contain a ``%s`` where the link location will be inserted.

SUMMARIZE_IGNORE : a list of tags

    Ignores given self-closed HTML tags in the output generation, defaults to
    ``['img', 'video', 'audio']``. With ``[]`` you can disable this behavior.

.. _filters-post-intro:

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

.. _filters-post-hyphenate:

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

.. _filters-post-typography:

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

.. _filters-post-acronyms:

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

.. _filters-post-relative:

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

.. _filters-post-absolute:

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

.. _filters-post-strip:

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
