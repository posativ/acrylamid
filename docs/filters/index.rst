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

Markup Languages
----------------

* :doc:`markup/md`
* :doc:`markup/rst`
* :doc:`markup/other`

Preprocessors
-------------

* :ref:`filters-pre-jinja2`
* :ref:`filters-pre-mako`
* :ref:`filters-pre-liquid`

Postprocessors
--------------

* :ref:`filters-post-headoffset`
* :ref:`filters-post-summarize`
* :ref:`filters-post-intro`
* :ref:`filters-post-hyphenate`
* :ref:`filters-post-typography`
* :ref:`filters-post-acronyms`
* :ref:`filters-post-relative`
* :ref:`filters-post-absolute`
* :ref:`filters-post-strip`

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
