Assets
======

A web log merely consists of text only, hence you might want CSS -- or even
more advanced -- SCSS or LESS to style your content, use some fancy JavaScript
or just include an image. These are all assets.

By convention, you put your static files into the `static/` folder, but you
may change this via ``STATIC = "/path/to/dir"`` in your :doc:`conf.py`.
Without extensions, Acrylamid will just copy the content from your static
directory to the output directory, the same applies to your assets located
in your `THEME` folder.

The Concept of Writers
----------------------

If you have several static pages, that do not belong to your blog, you can use
them as plain HTML files in your asset folder and you have the ability to use
your prefered templating language here.

Available Writers
^^^^^^^^^^^^^^^^^

Template : .j2, .mako or .html -> .html
    renders HTML (and engine specific extensions) with your current templating
    engine. You can inherit from your theme directory as well from all
    templates inside your static directory.

    This writer is activated by default.

HTML : .html -> .html
    Copy plain HTML files to output if not in theme directory.

XML : .xml -> .xml
    Same as the HTML writer but for XML.

Webassets Integration
---------------------

To handle SASS, SCSS and LESS (and much more) Acrylamid uses the Webassets_
project. To use Webassets_ you first need to install the egg via::

    $ easy_install "webassets<0.10"

and you need a working SASS, LESS or whatever-you-want compiler. Next you
define your assets in your template like this:

.. code-block:: html+jinja

    {% for url in compile('style.scss', filters="scss", output="style.%(version)s.css",
                                        depends=["scss/*.css", "scss/*.scss"]) %}
        <link media="all" href="{{ url }}" rel="stylesheet" />
    {% endfor %}

This will compile the master `theme/style.scss` file using SCSS_ to the
specified output (the ``%(version).s`` is a placeholder for the version hash).
Use the `depends` keyword to watch additional files for changes (the `import`
clause within a stylesheet does not work yet).

.. _webassets: http://webassets.readthedocs.org/en/latest/index.html
.. _SCSS: http://sass-lang.com/
