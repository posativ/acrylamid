Theming
=======

With the release of Acrylamid version 0.4 it is also possible to create and
ship custom themes. Unlike other static blog compilers Acrylamid supports both
Jinja2_ and Mako_ as templating language. Unfortunately you can't mix both, so
you may write only a Jinja2_ theme or Mako_, although it is possible to ship
both versions.

Themes
------

HTML5
^^^^^

A minimalistic theme using HTML5 available for Mako and Jinja2.
`Preview <http://posativ.org/acrylamid/_static/html5.png>`_. Install with::

    $ acrylamid init --theme html5  # --mako optional

shadowplay
^^^^^^^^^^

New theme from `HTML5Webtemplates.co.uk
<http://www.html5webtemplates.co.uk/templates/shadowplay_2/index.html>`_ with
slightly modified colors. `Preview
<http://posativ.org/acrylamid/_static/shadowplay.png>`_. Unfortunately
Jinja2-only.

::

    $ acrylamid init --theme shadowplay

XHTML
^^^^^

From the dark days, Acrylamid also ships an XHTML theme that is no longer supported but still works™.

::

    $ acrylamid init --theme xhtml  # --mako optional


Where to start?
---------------

In the beginning, you may start from an existing theme like the minimalstic
HTML5 theme. At this point you can choose your templating engine of choice::

    $ acrylamid init --mako  # or --jinja2

This initializes all templates and static files into `theme/`. This directory
is configurable. Set ``THEME`` to any directory of your choice (but it should
include your used templates). You can now modify and extend the theme (use
:doc:`templating` as reference).


Contribute
----------

I'd be glad if you contribute a theme to Acrylamid and I'm also willing to
translate a Mako_ theme back to Jinja2_. This requires a working copy if
Acryamid itself::

    $ git clone https://github.com/posativ/acrylamid.git

All templates and default values are stored in ``acrylamid.defaults``
(incuding the sample text and default configuraton as well as Atom and RSS
templates). A theme consists basically of a directory structure like this::

    acrylamid/defaults/html5/
    ├── __init__.py
    ├── jinja2
    │   ├── articles.html
    │   ├── base.html
    │   ├── entry.html
    │   └── main.html
    ├── mako
    │   ├── articles.html
    │   ├── base.html
    │   ├── entry.html
    │   └── main.html
    └── style.css

The theme is called "html5" hence it is stored in this directory. Even if you
don't support all templating engines, you have to put your theme into your
used language. Otherwise Acrylamid won't be able to locate it.

Instead of just copy'n'paste the files, Acrylamid uses a MANIFEST-like build
system. A ``__init__.py`` file can be either placed into the root directory of
your theme or in the template language folder. The latter has a higher
priority. So if you only provide a single templating engine, it is better to
write your MANIFEST there. Let's look what is inside of the ``mystical``::

    from acrylamid.defaults import copy

    def rollout(engine):

        return 'theme', {
            'content/sample-entry.txt': copy('sample-entry.txt'),
            'theme/': [
                'base.html',
                'main.html',
                'entry.html',
                'articles.html',
                copy(engine + '/atom.xml'),
                copy(engine + '/rss.xml'),
                copy('html5/style.css')],
        }

The only import function there is :func:`rollout`. This necessary for the
theme to work! It returns a hash of all files that need to be copied. If you
don't provide a ``conf.py`` Acrylamid will automatically one for you. But back
to the actual *meaning* of the hash.

- ``'directory/somefile.txt': 'foobar.txt'`` is rather simple. Copy `foobar.txt`
  to ``directory/somefile.txt`. `foobar.txt`` is a relative to your theme.

- ``'directory/another-file.txt': copy('some-file.txt')`` is a bit trickier. It
  uses the file called `some-file.txt` that is relatively located to
  `acrylamid/defaults/` and copies it to the destination.

You can use a list of files, too. But keep in mind that `copy(file)` searches
in `acrylamid/defaults/` and the regular `main.html` in
`acrylamid/defaults/mytheme/engine/`! Take a look into `acrylamid/defaults` to
get an idea why this manifest above works.

The first parameter tolds Acrylamid how your templating directory is called.
You may set this to your theme's name or leave it just "theme".


custom configuration
--------------------

By default Acrylamid includes the configuration via `copy('conf.py')` and it
only replaces the used templating engine. If you want to set custom routes and
other template variables you have to provide your own `conf.py`.

.. _Jinja2: http://jinja.pocoo.org/
.. _Mako: http://makotemplates.org/
