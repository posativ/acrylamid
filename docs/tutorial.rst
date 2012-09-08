Tutorial
========

Thanks for choosing acrylamid as your static blog generator. The next section
will cover the basic usage to build and write efficiently blog entries.

Creating a Blog
---------------

Acrylamid is a command line application. That means you should have at least
a clue how to open the terminal on your operation system (excluding windows).

An acrylamid-powered blog is basically a configuration file and three
directories containing the content, layout and the generated output. To create
basic structure, type into the terminal:

.. raw:: html

    <pre>
    $ acrylamid init tutorial
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/theme/style.css
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/theme/base.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/theme/main.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/theme/entry.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/theme/articles.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/theme/rss.xml
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/theme/atom.xml
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/content/sample-entry.txt
    Created your fresh new blog at 'tutorial'. Enjoy!
    </pre>

A new directory named ``tutorial`` has been created. Go into the directory
and type ``ls -l``

.. raw:: html

    <pre>
    $ cd tutorial/
    $ ls -l
    total 4
     -rw-r--r-- 1 ich 1452 Mai 23 19:48 conf.py
     drwxr-xr-x 3 ich  102 Mai 23 19:42 <span class="ansi1 ansi34">content</span>/
     drwxr-xr-x 8 ich  272 Mai 23 19:42 <span class="ansi1 ansi34">theme</span>/
    </pre>

In ``conf.py`` you configure the whole generation behavior and you can set default
values that you may override in a specific entry. By default, all your text goes into
``content/`` and your theme is located in ``theme/``. All assets such as images and
other binary stuff goes into ``theme/``. Acrylamid will automatically copy stuff from
there into the output directory (defaults to ``output/``).

Compiling the Blog
------------------

Before doing anything else, make sure the current working directory is the
blog you just created. All acrylamid commands, except for init and serve,
require the current working directory have a valid *conf.py*. So, if you
haven’t done it before::

    $ cd tutorial/

Every new acrylamid blog already has a single entry to show you the basic
structure. Before you can view your blog, it needs to be compiled. To compile,
do this::

    $ acrylamid compile

This is what’ll appear in the terminal while acrylamid is compiling:

.. raw:: html

    <pre>
    $ acrylamid compile
       <span class="ansi1 ansi32">   create</span>  [0.06s] output/articles/index.html
       <span class="ansi1 ansi32">   create</span>  [0.44s] output/2012/die-verwandlung/index.html
       <span class="ansi1 ansi32">   create</span>  [0.00s] output/index.html
       <span class="ansi1 ansi32">   create</span>  [0.00s] output/tag/die-verwandlung/index.html
       <span class="ansi1 ansi32">   create</span>  [0.00s] output/tag/franz-kafka/index.html
       <span class="ansi1 ansi32">   create</span>  [0.03s] output/atom/index.html
       <span class="ansi1 ansi32">   create</span>  [0.03s] output/rss/index.html
       <span class="ansi1 ansi32">   create</span>  [0.00s] output/sitemap.xml
    Blog compiled in 0.61s
    </pre>

A feature-complete blog has ben created in the ``output`` directory. Start
a web server using the built-in webserver::

    $ acrylamid view

Now, open your web browser and navigate to http://localhost:8000/. What you’ll
see is something like `this screenshot <http://posativ.org/acrylamid/example.png>`_.

Editing the Entry
-----------------

The first step in getting to know how acrylamid really works will involve
editing the content of the new entry. First, though, a quick explanation of
how uncompiled pages are stored.

All entries are stored in the ``content/`` directory (or whatever you defined
in ``ENTRIES_DIR``). Currently, that directory has only one file:
``sample entry.txt``. If you open that file, you'll notice a section
containing metadata in YAML format at the top.

Let's change the content of this entry. Open ``sample entry.txt`` and add a
paragraph somewhere in the file. Something like this::

    This is a new paragraph which I've just inserted into this file. I can
    even write [Markdown](http://daringfireball.net/projects/markdown/)!

To view the changes, you must recompile first. So, run the **compile**
command. You should see something like this:

.. raw:: html

    <pre>
    $ acrylamid compile
       <span class="ansi1 ansi30">     skip</span>  output/articles/index.html
       <span class="ansi1 ansi33">   update</span>  [0.40s] output/2012/die-verwandlung/index.html
       <span class="ansi1 ansi33">   update</span>  [0.00s] output/index.html
       <span class="ansi1 ansi33">   update</span>  [0.00s] output/tag/die-verwandlung/index.html
       <span class="ansi1 ansi33">   update</span>  [0.00s] output/tag/franz-kafka/index.html
       <span class="ansi1 ansi33">   update</span>  [0.01s] output/atom/index.html
       <span class="ansi1 ansi33">   update</span>  [0.01s] output/rss/index.html
       <span class="ansi1 ansi30">identical</span>  output/sitemap.xml
    Blog compiled in 0.48s
    </pre>

The number between brackets next to the ``output/index.html`` filename
indicates the time it took for acrylamid to compile the this item. At the
bottom, the total time needed for compiling the entire blog is also shown.

Make sure that the preview server (acrylamid view) is still running, reload
http://localhost:8000/ in your browser, and verify that the page has indeed
been updated.

In the same file, let’s change the entry title from “Die Verwandlung” to
something more interesting. Change the line that reads ``title: Die
Verwandung`` to something else. The file should now start with this::

    ---
    title: My Opinion on “The Metamorphosis”
    date: 13.12.2011, 23:42
    tags: [Franz Kafka, Die Verwandlung]
    ---

The metadata section at the top of the file is formatted as YAML. All
attributes are free-form; you can put anything you want in the attributes: the
title, date, keyword for this post, the language the content is
written in, etc.

Recompile the site and once again load http://localhost:8000/ in your browser.
You will see that the title and the permalink to this entry has changed.

Adding a New Entry
------------------

Unlike other static site compiler, acrylamid does not rely on any fileystem's
structure to route entries to urls. You can create for each item a new folder,
sort them by year (I do prefer this), by category or by year/month – the main
thing is, it is a text file with a YAML-header in it.

When you have done all steps before, especially the previous one, creating an
article will be an ordinary step. You can either create a new text file in
your content directory (by default ``content/``) with your editor of choice or
use the builtin shortcut, which also creates a safe filename:

.. raw:: html

    <pre>
    $ acrylamid new Hello World!
    <span class="ansi1 ansi32">   create</span>  content/2012/hello-world.txt
    </pre>

That the YAML-header (that's the first part of the file) is created
by acrylamid automatically, this should simplify the start.
But it's of course possible and recommended to adapt these settings and the
body (the text of your entry). Currently, the header looks like this::

    $ cat content/2012/hello-world.txt
    ---
    title: Hello World!
    date: 31.01.2012, 19:47
    ---

An adopted header could look like this::

    ---
    title: Hello World!
    author: John
    tags: [Hello World, Acrylamid]
    date: "31.01.2012, 14:57"
    filters: rest
    ---

    Acrylamid_ is awesome!

    .. _acrylamid: http://posativ.org/acrylamid/

Filters modify the appearance of the entry. ``rest`` defines reStructuredText
as markup language. For available filters see the section on :doc:`filters`.

Another useful option is the date-option. The required format is ``'%d.%m.%Y,
%H:%M'`` which is used in acrylamid by default. (See :doc:`conf.py`. for
informations about how to change that behavior) If the date is not given, the
last modifcation time of the file is used (which could by bad when you only
add updates to an entry).


If you're done, just compile like above:

.. raw:: html

    <pre>
    $ acrylamid compile
       <span class="ansi1 ansi33">   update</span>  [0.03s] output/articles/index.html
       <span class="ansi1 ansi32">   create</span>  [0.52s] output/2012/hello-world/index.html
       <span class="ansi1 ansi30">     skip</span>  output/2012/die-verwandlung/index.html
       <span class="ansi1 ansi33">   update</span>  [0.00s] output/index.html
       <span class="ansi1 ansi30">     skip</span>  output/tag/die-verwandlung/index.html
       <span class="ansi1 ansi32">   create</span>  [0.00s] output/tag/hello-world/index.html
       <span class="ansi1 ansi32">   create</span>  [0.00s] output/tag/acrylamid/index.html
       <span class="ansi1 ansi30">     skip</span>  output/tag/franz-kafka/index.html
       <span class="ansi1 ansi33">   update</span>  [0.01s] output/atom/index.html
       <span class="ansi1 ansi33">   update</span>  [0.01s] output/rss/index.html
       <span class="ansi1 ansi33">   update</span>  [0.00s] output/sitemap.xml
    Blog compiled in 0.60s
    </pre>

You can see, that no additional warning is thrown, because we've set the date
correctly.

Customizing the Layout
----------------------

You'll find all templates inside the (wait for it) template directory::

    $ ls layouts/
    articles.html  atom.xml  base.html  entry.html  main.html  rss.xml

Most of them are self-explanatory and described in your used :doc:`views`. Basically all
HTML templates are derived from ``base.html`` which gives us the skeleton where we can
derieve an article view as well as the blog blog posts.

.. note::

    Did you about the ``--mako`` flag that initializes all templates with a Mako analogon?
    Just create your blog like this: ``acrylamid init --mako``. Unfortunately you can't mix
    different tempating engines.

To edit a layout, just open and change something. Acrylamid automatically detects changes
(even in parent layouts) and re-renders the blog.

You can also apply a different layout to a view, like so:

.. code-block:: python

    '/:year/:slug/': {
        'view': 'entry',
        'template': 'other.html'
    }

Writing Entries in reStructuredText
-----------------------------------

