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
        create  'articles/index.html', written to output/articles/index.html
        create  'Die Verwandlung', written to output/2011/die-verwandlung/index.html
        create  'rss/index.html', written to output/rss/index.html
        create  'atom/index.html', written to output/atom/index.html
        create  '/', written to output/index.html

A feature-complete blog has ben created in the ``output`` directory. Start
a web server using the built-in webserver:

::

    tutorial$> acrylamid view

Now, open your web browser and navigate to http://localhost:8000/. What you’ll
see is something like this:

#XXX: BILD!1!

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

    tutorial$> acrylamid compile
          skip  'articles/index.html' is up to date
       changed  content of 'Die Verwandlung'
       changed  content of 'rss/index.html'
       changed  content of 'atom/index.html'
       changed  content of '/'
       changed  content of '/tag/die-verwandlung/'
       changed  content of '/tag/franz-kafka/'


    

Adding a New Entry
------------------

When you have done all steps before, especially the previous one, creating an
article will be an ordinary step. To only thing you have to do, is to create a
new file in your content directory (by default ``content/``) and write your
text! Before publishing, don't forget to compile ;)

::

    tutorial$> cp content/sample\ entry.txt content/new\ entry.txt

Now you should adapt the settings (that's the first part of the file) and the
of course the text. Currently, the header looks like this:

::

    ---
    title: Die Verwandlung
    author: Franz Kafka
    tags: [Franz Kafka, Die Verwandlung]
    ---

An adopted header could look like this:

::

    ---
    title: hello world
    author: anonymous
    tags: [hello world, acrylamid]
    date: "31.01.2012, 14:57"
    filters: rest
    ---

Filters modify the appearance of the entry. ``rest`` defines REST as
markup language. For available filters see the section on
`filters </posativ/acrylamid/blob/master/docs/filters.rst>`_.

Another useful option is the date-option. The required format is
'%d.%m.%Y, %H:%M' which is used in acrylamid by default.
(See `conf.py </posativ/acrylamid/blob/master/docs/conf.py.rst>`_.
for informations about how to change that behavior)
If the date is not given, the last modifcation time of the file is used
(which could by bad when you only add updates to an entry).


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

