Assets
======

Since Acrylamid ≥ 0.4 it is possible to include site specific files (also
known as assets) in your blog.  Acrylamid can either copy or compile files
from a number of directories.

To include assets, just add a bunch of directories to your :doc:`conf.py`:

.. code-block:: python

    STATIC = ['assets', 'static']

In addition all files from your theme are assets, too (except for HTML and XML
templates by default).  The next examples shows you how to compile static
pages using the Jinja2_ markup language:

.. _Jinja2: http://jinja.pocoo.org/

.. code-block:: python

    STATIC_FILTER += ['Jinja2']

Now with an HTML file in ``static/projects.html`` you can inherit from all
templates inside the ``THEME`` directory using Jinja2_.


Available Writers
-----------------

SASS : .sass -> .css
    compiles SASS_ to CSS (requires ``sass`` to be in your ``PATH``)

SCSS : .scss -> .css
    compiles SCSS_ to CSS (requires ``sass`` to be in your ``PATH``)

LESS : .less -> .css
    compiles LESS_ to CSS (requires ``lessc`` to be in your ``PATH``)

Jinja2 : .html -> .html
    renders Jinja2 templates

HTML : .html -> .html
    Copy HTML files to output if not in theme directory.

XML : .xml -> .xml
    Same as the HTML writer.

.. _SASS: http://sass-lang.com/docs/yardoc/file.INDENTED_SYNTAX.html
.. _SCSS: http://sass-lang.com/
.. _LESS: http://lesscss.org/
