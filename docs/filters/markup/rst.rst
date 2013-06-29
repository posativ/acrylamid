reStructuredText
================

reStructuredText (frequently abbreviated as reST) is an easy-to-read,
what-you-see-is-what-you-get plaintext markup syntax and parser system.

- `Project Website <http://docutils.sourceforge.net/rst.html>`__
- `Reference <http://docutils.sourceforge.net/docs/user/rst/quickref.html>`__
- `Frequently Asked Questions <http://docutils.sourceforge.net/FAQ.html>`__

Implementation
--------------

Because there is only a single implementation, we use ``docutils`` to parse and
compile reStructuredText to HTML. You can write your posts in reST fashion:

.. code-block:: rst

    Title
    #####

    :type: page
    :tags: one, two

    Here begins the body ...

Note, that reST's metadata markup for lists is different to YAML and will throw
errors if not used correctly. Wrong reST markup will generally throw a lot of
warnings and errors in the generated output.

The reStructuredText filter has no further default settings beside
``initial_header_level`` set to 1. That means, the first-level heading uses
``<h2>``, the second-level heading ``<h3>`` and so on. ``<h1>`` is reserved
for the post's title.

Usage
^^^^^

============  ==================================================
Requires      ``docutils`` (or ``python-docutils``), optional
              ``pygments`` for syntax highlighting
Aliases       rst, rest, reST, restructuredtext
Conflicts     HTML, Markdown, Pandoc
============  ==================================================


Extensions
^^^^^^^^^^

* .. autosimple:: acrylamid.filters.rstx_gist.Gist
* .. autosimple:: acrylamid.filters.rstx_highlight.Highlight
* .. autosimple:: acrylamid.filters.rstx_youtube.YouTube
* .. autosimple:: acrylamid.filters.rstx_vimeo.Vimeo

Limitations
^^^^^^^^^^^

Unlike Markdown or Textile, you can not write plain HTML in reST. The only
way to include raw HTML is to use the ``.. raw:: html`` directive. This also
means, that you can **not** use preprocessors that generate HTML such as ``liquid``.

Tips
----

* To write `inline math`_ with a subset of LaTeX math syntax, so there is no
  need for additional extension like in Markdown, just use the ``math`` directive.

* For highlighting source code, you can use the new `code directive`_ from
  docutils. For convenience (and backwards compatibility), ``code-block``,
  ``sourcecode`` and ``pygments`` map to the ``code`` directive as well. To
  generate a style sheet, you use ``pygmentize``:

  ::

      $ pygmentize -S trac -f html > pygments.css

  To get a list of all available styles use the interactive python interpreter.

  ::

      >>> from pygments import styles
      >>> print list(styles.get_all_styles())

.. _inline math: http://docutils.sourceforge.net/docs/ref/rst/directives.html#math
.. _code directive: http://docutils.sourceforge.net/docs/ref/rst/directives.html#code
