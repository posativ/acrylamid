HTML, Textile, Pandoc
=====================

HTML
----

No transformation applied. Useful if your text is already written in HTML.

============  ==================================================
Requires      <built-in>
Aliases       pass, plain, html, xhtml, HTML
Conflicts     reStructuredText, Markdown, Pandoc
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
pandoc) to HTML. A typical call would look like
``filters: [pandoc+Markdown+mathml+...]``.

You can write your posts with `pandoc's title block`_::

    % Title
    % Author

You can find a complete list of pandocs improved (and bugfixed) Markdown
implementation in the `Pandoc User's Guide`_.

.. _Pandoc's title block: http://johnmacfarlane.net/pandoc/README.html#title-block>
.. _Pandoc User's Guide: http://johnmacfarlane.net/pandoc/README.html#pandocs-markdown

============  ==================================================
Requires      `Pandoc – a universal document converter
              <http://johnmacfarlane.net/pandoc/>`_ in PATH
Aliases       Pandoc, pandoc
Conflicts     reStructuredText, HTML, Markdown
Arguments     First argument is the FORMAT like Markdown,
              textile and so on. All arguments after that are
              applied as additional long-opts to pandoc.
============  ==================================================

