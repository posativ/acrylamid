Installation
============

Acrylamid doesn't reinvent the wheel. It integrates a lot of useful projects
to provide a feature-rich user experience. You can use acrylamid in a very
minimalistic way and write your posts in plain markdown or add more expensive
features you may not have with dynamic web pages such as code highlighting,
typography, MathML and hyphenation.

Linux/Debian and OS X
*********************

You'll need the python interpreter with version ≥ 2.6 and a python package
manager. If you are on Linux (Debian-based), just ``apt-get install python
python-setuputils``. If you are using OS X the proper Python version is
already installed (10.6 or later).

::

    $> easy_install -U acrylamid

And you are done with the simplest setup (by the way even markdown and
translitcodec are not must-have dependency). You can install all supprted
modules via ``easy_install -U acrylamid[full]``.

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
| Discount                                                                                | `discount <http://www.pell.portland.or.us/~orc/Code/discount/>`_.          |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| Syntax Highlighting                                                                     | `pygments <http://pygments.org/>`_                                         |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| Typography enhancements                                                                 | `smartypants <http://daringfireball.net/projects/smartypants/>`_           |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| AsciiMathML to MathML                                                                   | `asciimathml <https://github.com/favalex/python-asciimathml>`_             |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| cyrillic/chinese ascii slugs                                                            | `unidecode <http://pypi.python.org/pypi/Unidecode/>`_                      |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| non-ASCII text detection                                                                | `python-magic <https://pypi.python.org/pypi/python-magic/>`_               |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| Mako Templating                                                                         | `mako <http://www.makotemplates.org/>`_                                    |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| exact YAML parser                                                                       | `PyYAML <http://pyyaml.org/>`_                                             |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+
| Twitter                                                                                 | `twitter <http://pypi.python.org/pypi/twitter>`_                           |
+-----------------------------------------------------------------------------------------+----------------------------------------------------------------------------+

Asian/Russian Users
-------------------

If you write in your native language, I recommend to install ``unidecode`` for
a better ASCII transcription of your characters. If not, provide either a
proper ASCII slug in your articles or use a fixed permalink with your native
characters.

Acrylamid also tries to detect text files, but that might fail if your post
has less than 30% ASCII characters within the first 512 bytes. Therefore you
can optionally install ``python-magic`` to circumvent this issue.

Windows
*******

Works, but remains uncovered by the developer and test suite.

Python 3
********

As of Acrylamid 0.4.4 Python 3 is covered by the testsuite. So, in theory it
might work. Please report any issues related to Python 3.
