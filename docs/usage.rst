Getting Started
===============

Acrylamid is a command line application. That means you should have at least
a clue how to open the terminal on your operation system (except for Windows).

Initialization
--------------

To create a new blog, just run ``acrylamid init``. You can choose between Mako
and Jinja2 as templating languages. See also :doc:`commands` for more details.

.. raw:: html

    <pre>
    $ acrylamid init /path/to/blog/
      <span style="font-weight: bold; color: #00aa00">   create</span>  blog/theme/style.css
      <span style="font-weight: bold; color: #00aa00">   create</span>  blog/theme/base.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  blog/theme/main.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  blog/theme/entry.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  blog/theme/articles.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  blog/theme/rss.xml
      <span style="font-weight: bold; color: #00aa00">   create</span>  blog/theme/atom.xml
      <span style="font-weight: bold; color: #00aa00">   create</span>  blog/content/sample-entry.txt
    Created your fresh new blog at 'blog'. Enjoy!
    </pre>

A new directory named ``tutorial`` has been created. Go into the directory
and type ``ls -l``

.. raw:: html

    <pre>
    $ ls -l /path/to/blog/
    total 4
     -rw-r--r-- 1 ich 1452 Mai 23 19:48 conf.py
     drwxr-xr-x 3 ich  102 Mai 23 19:42 <span class="ansi1 ansi34">content</span>/
     drwxr-xr-x 8 ich  272 Mai 23 19:42 <span class="ansi1 ansi34">theme</span>/
    </pre>

conf.py : Configuration
    That's your configuration file for Acrylamid!

content/ : Content Directory
    Here you should write your articles. You can also place other files like
    images here, but that slows down Acrylamid and won't be copied to
    destination.

theme/ : Theme Directory
    The location of your HTML tempales and other static files for that theme,
    that will be copied during compilation.


Write a new entry
-----------------

You can either fire up your editor and write an entry somewhere below
``content/`` or run ``acrylamid new`` which will open your favourite editor
save the entry to its permalink. BTW it does not matter how you name your
file. It is only important, that it doesn't contain binary in the first 512
bytes!

I'll give you a short description of all available fields.

title : String
    You know what that is.

date : String
    A date in the format your specified in your :doc:`conf.py` and several
    fallbacks you'll find here: `pelican/utils.py:21 <https://github.com/getpelican/pelican/blob/master/pelican/utils.py#L56>`_.

author : String
    Overwrites author in :doc:`conf.py`.

tags : String or List of Strings
    Tags that describe your content. In YAML and Markdown it has the format of
    ``[one, two, three]`` while in reStructuredText it is ``one, two``.

filters : String or List of Strings
    Additional filters for this entry. They can conflict with existing filters
    or add additional conversion. See :doc:`filters` for details.

permalink : String
    Link that will be used as full text destination. If you change the title of
    an entry but want to keep the permalink, set this to ``/2012/old-title/``
    or ``/my-entry.html``.

type: String
    Make this entry a blog article or static page. Possible values are
    ``entry`` (default) or ``page``.

encoding : String
    The encoding of that file. Defaults to your system's prefered encoding.

lang : String
    Language used in this post. Used for translation (if active) or to
    determine the hyphenation pattern.

draft : Boolean
    Set this to ``False`` to make this entry not visible in your feeds and
    listings. It will only show up as full text entry, so you can only access
    it when you know the path.

layout : String
  A user-defined template to use for the full-text (entry, page and translation) view,
  fallback to the view's default template.


YAML front matter
^^^^^^^^^^^^^^^^^

That is the default format of your articles. Similar to Jekyll::

    ---
    title: Foo
    date: 06/09/2012
    ---

native metadata style
^^^^^^^^^^^^^^^^^^^^^

With Acrylamid 0.4 you can also use the native metadata section provided by
Markdown and reStructuredText. Both nativ formats are only active when you set
``METASTYLE = "native"`` in your :doc:`conf.py` and your filenames end with
``.rst`` or ``.rest`` for reStructuredText and ``.md`` or ``.mkdown`` for
Markdown. Keep in mind, that the native metadata style only affects the parser.
It does *not* set the filter to reST or Markdown.

reStructuredText:

.. code-block:: rst

    Title
    #####

    :type: page
    :tags: one, two

    Here begins the body ...

Markdown::

    date: 06/09/2012
    title: Test
    tags: [one, two]

    Here starts my content ...

reStructuredText or textile
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you prefer reStructuredText or textile for a single entry or for your
whole blog, set either (a filter can have different aliases, so
reStructuredText or reST work both)::

    FILTERS = ['reStructuredText', ...]  # or textile

or in your entry::

    ---
    title: Hello World!
    tags: [Hello World, Acrylamid]
    filters: reST
    ---

    Acrylamid_ is awesome!

    .. _acrylamid: http://posativ.org/acrylamid/


Compilation
-----------

The heart of Acrylamid. Generating the content. You can abbreviate
``acrylamid compile`` to ``acrylamid co`` if you like. ``gen`` and
``generate`` are aliases, too.

.. raw:: html

    <pre>
    $ cd /path/to/blog/
    $ acrylamid compile
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.05s] output/articles/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.37s] output/2012/die-verwandlung/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.00s] output/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.00s] output/tag/die-verwandlung/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.00s] output/tag/franz-kafka/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.03s] output/atom/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.03s] output/rss/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.00s] output/sitemap.xml
      <span style="font-weight: bold; color: #00aa00">   create</span>  output/style.css
    9 new, 0 updated, 0 skipped [0.63s]
    </pre>

You want to see incremental compilation in action? Then create a new entry and
re-compile:

.. raw:: html

    <pre>
    $ acrylamid new test
    $ acrylamid co
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.02s] output/articles/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.30s] output/2012/test/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.00s] output/2012/die-verwandlung/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.00s] output/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.01s] output/atom/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.01s] output/rss/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.00s] output/sitemap.xml
    1 new, 6 updated, 3 skipped [0.49s]
    </pre>


Customizing the Layout
----------------------

You'll find all your theme files inside the (wait for it) theme directory.
Most variables are explained in :doc:`templating` and :doc:`views`. Of you
want to contribute your theme read :doc:`theming` first.

::

    $ ls theme/
    articles.html  atom.xml  base.html  entry.html  main.html  rss.xml

.. note::

    Did you about the ``--mako`` flag that initializes all templates with a
    Mako analogon? Just create your blog like this: ``acrylamid init --mako``.
    Unfortunately you can't mix different tempating engines.

To edit a layout, just open and change something. Acrylamid automatically
detects changes (even in parent templates) and re-renders the blog.

You can also apply a different templates to views, like so:

.. code-block:: python

    '/:year/:slug/': {
        'view': 'entry',
        'template': 'mytemplate.html'
    }


Deployment
----------

Now you have your rendered HTML in your output directory, how do you deploy?
First, Acrylamid does nothing for you but it provides a helper. You can add
different deployment tasks in your :doc:`conf.py <conf.py>` and run them from
Acrylamid. All what Acrylamid does is populating the shell environment with
your configuration variables::

    DEPLOYMENT = {
        'blog': 'rsync -ruv $OUTPUT_DIR www@server:~/blog/'
    }

You can run that task with ``acrylamid deploy TASK`` or even shorter ``acrylamid dp TASK``. For more information, head over to :ref:`deploy`.

.. raw:: html

    <pre>
    $ acrylamid deploy blog
    <span style="font-weight: bold; color: #000316">    execute</span> rsync -av --delete output/ www@server:~/blog/
    building file list ... done

    sent 19701 bytes  received 20 bytes  7888.40 bytes/sec
    total size is 13017005  speedup is 660.06
    </pre>


Dive Into Acrylamid
-------------------

Now, you know the basic usage of Acrylamid, you can go on with one of these
topics:

- :doc:`advanced`
- :doc:`commands`
- :doc:`filters`
- :doc:`views`
