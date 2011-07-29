lilith documentation
====================

lilith is yet another lightweight static blogging software. It is designed to be
easily extendable and offers a various number of built-in plugins.

lilith is licensed under BSD Style, 2 clauses.

Features
********

- blog articles, pages and rss/atom feeds
- theming support (using jinja2_)
- reStructuredText_ and Markdown_ as markup languages
- (currently only german) hyphenation using `&shy;`
- MathML generation using AsciiMathML_

.. _jinja2: http://jinja.pocoo.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _AsciiMathML: http://www1.chapman.edu/~jipsen/mathml/asciimath.html

Quickstart
**********

Dependencies ``python`` (at least 2.5), ``pyyaml``, ``shpaml``, and ``jinja2``.
And of course ``docutils`` or ``markdown`` (and ``pygments`` for syntax
highlighting) markup, but not required in plain HTML.

::

    pip install pyyaml shpaml jinja2

Get lilith and edit *lilith.conf* and *layouts/*. Run lilith with:

::

    python lilith.py
    
which renders everything to ``output_dir`` (defaults to */out*). lilith has
a basic commandline interface, specify ``-c FILE`` to use another config file
and ``-l DIR`` to use an alternate layouts-folder (overwrites settings in
lilith.conf).

Using lilith
************

lilith uses a flat file db to store its blog entries. It does not depend on a
specific filesystem structure, neither the user's structure has any effect on
the rendered output. Just specify a ``entries_dir`` in ``lilith.conf``, lilith
will traverse this folder and processes all files in it.

An entry consists of two parts. A YAML_-header and then the real content.
Inside the YAML-header you must specify at least a ``title: My Title`` and
``date: 21.12.2012, 16:47`` key (if not set, lilith is using the last mtime).

If you don't know, what markup-language you prefer or if yo are using different
markup languages, use e.g. ``parser: rst`` for reStructuredText.

.. _YAML: http://en.wikipedia.org/wiki/YAML

Sample entry.txt
----------------

.. code-block:: yaml

    ---
    title: A meaningful title
    parser: Markdown # optional
    date: 19.06.2011, 12:45 # recommended
    ---

    Your content goes here...

lilith.conf – YAML syntax!
--------------------------

.. code-block:: yaml

    # required in templating
    author:     your name
    website:    http://mywebsite.org/
    email:      me@example.org
    blog_title: your website's title
    www_root:   http://path.to/blog/

    # optional keys:
    ext_dir:        a list of dirs containing extensions for lilith, defaults to "ext/"
    ext_ignore:     a list of extensions to ignore, e.g. [mathml, ]
    entries_dir:    dir holding your entries, defaults to "content/"
    output_dir:     output directory, defaults to "out/"
    items_per_page: used for pagination, defaults to 6
        
    parser:         a default entry parser # NOTE: currently not used
    strptime:       your human-readable time parsing format, defauts to "%d.%m.%Y, %H:%M"
    lang:           (de-DE, ...) # used in HTML-layout (and for hyphenation, later)


You can specify every other key-value pair you want use in plugins or as
Template variable. Adding an existing key-value pair in the YAML-header
of an entry will locally overwrite the config's value.

the output
----------

::

    out/
    ├── 2011/
    │   └── a-meaningful-title/
    │       └── index.html
    ├── articles/
    │   └── index.html
    ├── atom/
    │   └── index.xml
    ├── rss/
    │   └── index.xml
    └── index.html

You may need to set index.xml as index-page in your webserver's configuration
to get rss and atom feeds in *http://example.org/atom/* or */rss/*.

Extensions
**********

- **syndication**: produces valid atom and rss feeds
- **summarize**: summarizes posts to 200 words in pagination
- **hyphenate**: hyphenation using ``&shy;`` (currently german-only)
- **mathml**: asciimathml to MathML converter
- **articles**: simple article overview

multilang.py
------------

lilith has basic support for multilanguage blogging. This extension can be
enabled in *lilith.conf* by adding it to the list of ``ext_include``. The
extension is called *multilang*.

multilang.py watches for entries, which have an identifier key in their
YAML-header. Entries with identical identifier are bundled as translations,
if their ``lang`` differs from config's language (system's locale by default).

An example (system's locale is en_US)

.. code-block:: yaml

    ---
    title: english entry
    lang: en    # <-- this is not required, en is the default language!
    identifier: mykey
    ---

    your content goes here...
    
and the german translation

.. code-block:: yaml

    ---
    title: deutscher Eintrag
    lang: de
    identifier: mykey
    ---

    Inhalt hier rein...
    
In this example, every non-default language article is rendered into
*http://example.org/2011/de/deutscher-eintrag/*. See this commit_ for
additional information.

.. _commit: https://github.com/posativ/lilith/commit/d7198673b812861268ad4335200f6d9b8fc76cbf

When you render "english title", you have an additional variable called
``translations``, containing all translations of this article. Which you can
use to link to. In jinja2 templating (*entry.html*), e.g.:

.. code-block:: html

    {% if 'multilang' in extensions and translations %}
    <ul>
        {% for tr in translations %}
            <li><strong>{{ tr.lang }}:</strong> <a href="{{ tr.url }}">{{ tr.title }}</a></li>
        {% endfor %}
    </ul>
    {% endif %}

Which renders something like into "english entry":

.. code-block:: html

    <ul>
        <li><strong>de:</strong> <a href="http://example.org/2011/de/deutscher-eintrag/">deutscher Eintrag</a></li>
    </ul>


.. toctree::
   :maxdepth: 2
   
   todo
   about

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
