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

::

    $> acrylamid init tutorial
        create  tutorial/conf.py
        create  tutorial/content/sample entry.txt
        create  tutorial/layouts/articles.html
        create  tutorial/layouts/entry.html
        create  tutorial/layouts/main.html
        create  tutorial/output/blog.css
    Created your fresh new blog at 'tutorial'. Enjoy!

A new directory named ``tutorial`` has been created. Go into the directory
and type ``ls -l``

::

    $> cd tutorial/
    tutorial$> ls -l
    total 8
    -rw-r--r--  1 ich  staff  942 20 Jan 12:09 conf.py
    drwxr-xr-x  3 ich  staff  102 20 Jan 12:09 content
    drwxr-xr-x  6 ich  staff  204 20 Jan 12:09 layouts
    drwxr-xr-x  3 ich  staff  102 20 Jan 12:09 output

You see one file and three directories and they should be pretty
self-explanatory, at least their intention.

Compiling the Blog
------------------

Before doing anything else, make sure the current working directory is the
blog you just created. All acrylamid commands, except for init and serve,
require the current working directory have a valid *conf.py*. So, if you
haven’t done it before:

::

    $> cd tutorial/
    tutorial$>

Every new acrylamid blog already has a single entry to show you the basic
structure. Before you can view your blog, it needs to be compiled. To compile,
do this:

::

    tutorial$> acrylamid compile

This is what’ll appear in the terminal while acrylamid is compiling:

::

    tutorial$> acrylamid compile
        create  [0.00s] output/articles/index.html
        create  [0.27s] output/2011/die-verwandlung/index.html
        create  [0.25s] output/rss/index.html
        create  [0.00s] output/atom/index.html
        create  [0.26s] output/index.html
        create  [0.00s] output/tag/die-verwandlung/index.html
        create  [0.00s] output/tag/franz-kafka/index.html
    Blog compiled in 0.79s

A feature-complete blog has ben created in the ``output`` directory. Start
a web server using the built-in webserver:

::

    tutorial$> acrylamid view

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
paragraph somewhere in the file. Something like this:

::

    This is a new paragraph which I've just inserted into this file. I can
    even write [Markdown](http://daringfireball.net/projects/markdown/)!

To view the changes, you must recompile first. So, run the **compile**
command. You should see something like this:

::

    tutorial$>  acrylamid compile
      identical  output/articles/index.html
        update  [0.26s] output/2011/die-verwandlung/index.html
        update  [0.25s] output/rss/index.html
        update  [0.00s] output/atom/index.html
        update  [0.25s] output/index.html
        update  [0.01s] output/tag/die-verwandlung/index.html
        update  [0.01s] output/tag/franz-kafka/index.html
    Blog compiled in 0.77s

The number between brackets next to the ``output/index.html`` filename
indicates the time it took for acrylamid to compile the this item. At the
bottom, the total time needed for compiling the entire blog is also shown.

Make sure that the preview server (acrylamid view) is still running, reload
http://localhost:8000/ in your browser, and verify that the page has indeed
been updated.

In the same file, let’s change the entry title from “Die Verwandlung” to
something more interesting. Change the line that reads ``title: Die
Verwandung`` to something else. The file should now start with this:

::

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
article will be an ordinary step.
You can either create a new text file in your content directory (by default ``content/``)
with your editor of choice or use the
builtin shortcut, which also creates a safe filename:

::

    tutorial$> cp acrylamid new New Entry!


That the YAML-header (that's the first part of the file) is created
by acrylamid automatically, this should simplify the start.
But it's of course possible and recommended to adapt these settings and the
body (the text of your entry). Currently, the header looks like this:

::

    tutorial$> cat content/2012/hello-world.txt
    ---
    title: New Entry!
    date: 31.01.2012, 19:47
    ---

An adopted header could look like this:

::

    ---
    title: My New Entry!
    author: anonymous
    tags: [hello world, acrylamid]
    date: "31.01.2012, 14:57"
    filters: rest
    ---

Filters modify the appearance of the entry. ``rest`` defines REST as markup
language. For available filters see the section on :doc:`filters`.

Another useful option is the date-option. The required format is '%d.%m.%Y,
%H:%M' which is used in acrylamid by default. (See :doc:`conf.py. for
informations about how to change that behavior) If the date is not given, the
last modifcation time of the file is used (which could by bad when you only
add updates to an entry).


If you're done, just compile like above:

::

    tutorial$> acrylamid compile
          warn  using mtime from <fileentry f'content/sample entry.txt'>
          skip  '/tag/die-verwandlung' is up to date
        create  '/tag/hello-world', written to output/tag/hello-world/index.html
        create  '/tag/acrylamid', written to output/tag/acrylamid/index.html
          skip  '/tag/franz-kafka' is up to date
       changed  content of '/articles/index.html'
       changed  content of '/'
       changed  content of '/atom/index.html'
       changed  content of '/rss/index.html'
          skip  'Die Verwandlung' is up to date
        create  'hello world', written to output/2012/hello-world/index.html

You can see, that no additional warning is thrown, because we've set the date
correctly.

Customizing the Layout
----------------------

Writing Entries in reStructuredText
-----------------------------------

