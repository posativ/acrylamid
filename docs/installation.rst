Installation
============

Acrylamid doesn't reinvent the wheel. It integrates a lot of useful projects
to provide a feature-rich user experience. You can use acrylamid in a very
minimalistic way and write your posts in plain markdown or add more expensive
features you may not have with dynamic web pages such as code highlighting,
typography, mathml and hyphenation. See :doc:`about` for a listing of
third-party libraries used.

I'm aware of tools like javascript-based syntax highlighting and
browser/javascript provided hyphenation, but the latter is rather slow and a
browser may not distuingish between different languages. Acrylamids focuses on
plain HTML generation and avoids javascript usage whenever possible.

Linux/Debian and OS X
*********************

You'll need the python interpreter with version ≥ 2.6 and a python package
manager. If you are on Linux (Debian-based), just ``apt-get install python
python-setuputils``. If you are using OS X the proper Python version is
already installed (10.6 or later).

::

    $> easy_install -U acrylamid

And you are done with the simplest setup (by the way even markdown and
translitcodec are not must-have dependency).

.. note::

    Avoid removing ``translitcodec`` egg after you started writing your blog. It
    might break all your permanent links.

Additional Supported Modules
----------------------------

+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| Feature                                                                                 | Dependency                                                                 |
+=========================================================================================+============================================================================+
| reStructuredText                                                                        | `docutils <htthttp://docutils.sourceforge.net/README.html#quick-start>`_   |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| Textile                                                                                 | `pytextile <http://pypi.python.org/pypi/textile/>`_                        |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| Syntax Highlighting                                                                     | `pygments <http://pygments.org/>`_                                         |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| Typography enhancements                                                                 | `smartypants <http://daringfireball.net/projects/smartypants/>`_           |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| AsciiMathML to MathML                                                                   | `asciimathml <https://github.com/favalex/python-asciimathml>`_             |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| cyrillic/chinese ascii slugs                                                            | `unidecode <http://pypi.python.org/pypi/Unidecode/>`_                      |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| Mako Templates                                                                          | `mako <http://www.makotemplates.org/>`_                                    |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| exact YAML parser                                                                       | `PyYAML <http://pyyaml.org/>`_                                             |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+


Asian/Russian Users
-------------------

If you write in your native language, you have to install ``unidecode`` for
ASCII transcription of your characters. This is only required for the safe
slug to your post.


Windows
*******

Not supported currently.

Python 3
********

Within the release of 0.3.4 Acrylamid has experimental support for Python 3. I
hope *2to3* gets automatically applied, if not:


.. code-block:: bash

	$ 2to3 -wn -x execfile acrylamid/
	$ python setup.py install
