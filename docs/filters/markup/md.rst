Markdown (and Variants)
=======================

Markdown is a text-to-HTML conversion tool for web writers. Markdown allows
you to write using an easy-to-read, easy-to-write plain text format, then
convert it to structurally valid XHTML (or HTML). -- `John Gruber`_

Here's an online service converting Markdown to HTML and providing a handy
cheat sheet: `Dingus <http://daringfireball.net/projects/markdown/dingus>`_.

.. _John Gruber: http://daringfireball.net/projects/markdown/

Implementation
--------------

There are many different Markdown implementations and extensions. Acrylamid
uses `Python Markdown`_ as primary library to parse, compile and extend
Markdown. The library is almost compliant with the reference implementation,
but has a few very `minor differences`_.

You can write your posts with a so called "meta data" header; an unofficial
extension used by the popular MultiMarkdown_ and `Python Markdown`_ (keys are
case-insensitive and converted to lowercase):

.. code-block:: text

    Title: A Sample MultiMarkdown Document
    Author: Fletcher T. Penney
    Date: Feb 9, 2011
    Comment: This is a comment intended to demonstrate
             metadata that spans multiple lines, yet
             is treated as a single value.
    Test: And this is a new key-value pair
    Tags: [Are, parsed, YAML-like]

.. _Python Markdown: http://pythonhosted.org/Markdown/
.. _minor differences: http://pythonhosted.org/Markdown/#differences
.. _MultiMarkdown: http://fletcherpenney.net/multimarkdown/

Usage
^^^^^

============  ====================================================
Requires      ``markdown`` or (``python-markdown``) -- already
              as a dependency implicitly installed
Aliases       md, mkdown, markdown
Conflicts     HTML, reStructuredText, Pandoc
Arguments     asciimathml, sub, sup, delins, gist, gistraw
              <built-in extensions>
============  ====================================================

Extensions
^^^^^^^^^^

`Python Markdown`_ ships with a few popular extensions such as ``tables``,
see their `supported extensions` page for details. You can add extensions
selectively via ``markdown+tables+...`` or add the most common extensions
via ``markdown+extras``.

In addition to the official extensions, Acrylamid features

* inline math via AsciiMathML_. The aliases are: *asciimathml*, *mathml* and
  *math* and require the ``python-asciimathml`` package. *Note* put your formula
  into single dollar signs like ``$a+b^2$``!
* super_ und subscript_ via *sup* (or *superscript*) and *sub* (or
  *subscript*). The syntax for subscript is ``H~2~O`` and for superscript
  ``a^2^``.
* `deletion and insertion`_ syntax via *delins*. The syntax is ``~~old~~`` and
  ``++new++``.
* `GitHub:Gist <https://gist.github.com/>`__ embedding via ``[gist: id]`` and
  optional with a filename ``[gist: id filename]``. You can use ``[gistraw:
  id [filename]]`` to embed the raw text without JavaScript.

out-of-the-box.

.. _supported extensions: http://pythonhosted.org/Markdown/extensions/
.. _AsciiMathML: https://github.com/favalex/python-asciimathml
.. _super: https://github.com/sgraber/markdown.superscript
.. _subscript: https://github.com/sgraber/markdown.subscript
.. _deletion and insertion: https://github.com/aleray/mdx_del_ins

Limitations
^^^^^^^^^^^

Markdown is very easy to write, but especially as a developer, you might
experience some rare "issues" not covered by the official test suite, for
example it is impossible to write an unordered list followed by a code
listing. Read `Pandoc's Markdown`_ to see what's "wrong" or difficult to
achieve in markdown.

.. _Pandoc's Markdown: http://johnmacfarlane.net/pandoc/README.html#pandocs-markdown

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
