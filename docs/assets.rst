Assets
======

Since Acrylamid ≥ 0.4 it is possible to include site specific files (also
known as assets) in your blog.  Acrylamid can either copy or compile files
from a number of directories.

To include assets, just add a bunch of directories to your :doc:`conf.py`:

.. code-block:: python

    STATIC = ['assets', 'static']

In addition all files from your theme are assets, too (except for HTML and XML
templates by default) and will be copied to the output directory.

Available Writers
-----------------

SASS : .sass -> .css
    compiles SASS_ to CSS (requires ``sass`` to be in your ``PATH``)

SCSS : .scss -> .css
    compiles SCSS_ to CSS (requires ``sass`` to be in your ``PATH``)

LESS : .less -> .css
    compiles LESS_ to CSS (requires ``lessc`` to be in your ``PATH``)

CoffeeScript : .coffee -> .js
    compiles CoffeeScript_ to JavaScript (requires ``coffee`` to be in your ``PATH``)

IcedCoffeeScript : .iced -> .js
    compiles IcedCoffeeScript_ to JavaScript (requires ``iced`` to be in your ``PATH``)

Template : .html -> .html
    renders HTML (and engine specific extensions) with your current templating
    engine. You can inherit from your theme directory as well from all
    templates inside your static directory.

HTML : .html -> .html
    Copy HTML files to output if not in theme directory.

XML : .xml -> .xml
    Same as the HTML writer.

.. _SASS: http://sass-lang.com/docs/yardoc/file.INDENTED_SYNTAX.html
.. _SCSS: http://sass-lang.com/
.. _LESS: http://lesscss.org/
.. _CoffeeScript: http://coffeescript.org/
.. _IcedCoffeeScript: http://maxtaco.github.com/coffee-script/
