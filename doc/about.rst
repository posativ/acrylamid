Third-party tools used by lilith
================================

- `pyyaml <http://pyyaml.org/>`_ – human-readable config
- `jinja2 <http://jinja.pocoo.org/>`_ – awesome templating
- `shpaml <http://shpaml.webfactional.com/>`_ – simple xml/html generation

Markup languages
****************

- `reStructuredText <http://docutils.sourceforge.net/rst.html>`_
- `Markdown <http://daringfireball.net/projects/markdown/>`_
- syntax highlighting via `pygments <http://pygments.org/>`_

Extensions
**********

- `AsciiMathML <http://www1.chapman.edu/~jipsen/mathml/asciimath.html>`_ via
  `python-asciimathml <https://github.com/favalex/python-asciimathml>`_
- Hyphenation is based on `Frank Liang's algorithm <http://nedbatchelder.com/code/modules/hyphenate.py>`_
  `TEX hyphenation patterns <http://tug.org/tex-hyphen/>`_

Ideas
=====

lilith is a mixture of mainly three ingredients: PyBlosxom_, nanoc_ and
several complete rewrites (including data loss near the end) of lilith_
itself.

From PyBlosxom I've stolen the awesome flat filesystem idea and the concept of
chaining callbacks to produce a default blog and/or extend it to your needs,
when you need it. Nanoc is quite difficult for me, since I am not familiar
with the ruby language, but is has two cool aspects: YAML configuration
files and filters. And from my own project, I got boring markup rendering,
several HTML/XML preprocessors and the basic concept of how to develop a
web 2.0 blog system.

.. _PyBlosxom: http://pyblosxom.bluesock.org/
.. _nanoc: http://nanoc.stoneship.org/
.. _lilith: http://blog.posativ.org/2010/es-lebt/