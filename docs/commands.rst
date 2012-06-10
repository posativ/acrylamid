Commands
========

Unlike other popular static blog compiler Acrylamid uses a CLI interface that
uses positional arguments for each task. Long options are used for special
flags like force or dry run. The basic call is ``acrylamid <subcommand>
[options] [args]``.

-q, --quiet     less verbose
-v, --verbose   more verbose
-C, --no-color  disable color
-h, --help      show this help message and exit
--version       print version details


init
----

This initializes the base structure of an Acrylamid blog, thus it should be
the first command you'll execute. In addition to initialization it also can
restore changed/deleted files if you specify the complete path as argument.

-f, --force       don't ask, just overwrite
--html5           use HTML5 layout (default)
--xhtml           use legacy XHTML 1.1 layout

.. raw:: html

    <pre>
    $ acrylamid init tutorial
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/output/style.css
         ...
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/layouts/atom.xml
      <span style="font-weight: bold; color: #00aa00">   create</span>  tutorial/content/sample-entry.txt
    Created your fresh new blog at 'tutorial'. Enjoy!
    </pre>

If you give . (dot) as argument the current working dir is used. Let's say you
have edited *output/style.css* and want restore the original version.

.. raw:: html

    <pre>
    $ cd foo/
    $ acrylamid init output/blog.css
    re-initialize 'output/style.css'? [yn]: y
        <span style="font-weight: bold; color: #aa5500">re-initialized</span> output/style.css
    </pre>


new
---

With ``acrylamid new`` you specify a title in [args] or you'll get prompted to
enter a title and Acrylamid automatically create the post using the current
datetime and places the file into ``CONTENT_DIR`` (defaults to content/) using
``PERMALINK_FORMAT`` as path expansion. Afterwards it'll launch your
favourite $EDITOR.

.. raw:: html

    <pre>
    $ acrylamid new
    Entry's title: This rocks!
    <span style="font-weight: bold; color: #00aa00">   create</span>  content/2012/this-rocks.txt
         [opens TextMate for me]
    </pre>


compile
-------

Compiles all your content using global, view and entry filters with some magic
and generates all files into ``OUTPUT_DIR`` (defaults to output/). Note that
this command will *not* remove orphaned files. Depending on your changes and
content size it may take some time.

-f, --force     clear cache before compilation
-n, --dry-run   show what would have been compiled
-i, --ignore    ignore critical errors (e.g. missing module used in a filter)

.. raw:: html

    <pre>
    $ acrylamid compile
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.03s] output/articles/index.html
      <span style="font-weight: bold; color: #000316">     skip</span>  output/2012/die-verwandlung/index.html
      <span style="font-weight: bold; color: #00aa00">   create</span>  [0.41s] output/2012/this-rocks/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.00s] output/index.html
      <span style="font-weight: bold; color: #000316">     skip</span>  output/tag/die-verwandlung/index.html
      <span style="font-weight: bold; color: #000316">     skip</span>  output/tag/franz-kafka/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.01s] output/atom/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.01s] output/rss/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.00s] output/sitemap.xml
    Blog compiled in 0.52s
    </pre>


view
----

After you compiled your blog you could ``cd output/ && python -m
SimpleHTTPServer`` to view the output, but this is rather exhausting. Its much
simpler to run ``acrylamid view`` and it automatically serves on port 8000.
Hit *Ctrl-C* to exit.

-p PORT, --port=PORT  webserver port

::

    $ acrylamid view -p 1234
     * Running on http://127.0.0.1:1234/


autocompile
-----------

If you need visual feedback while you write an entry, Acrylamid can
automatically compile and serve when you save your document. Hit *Ctrl-C* to
quit.

-f, --force           clear cache before compilation
-i, --ignore    ignore critical errors (e.g. missing module used in a filter)
-p PORT, --port=PORT  webserver port

.. raw:: html

    <pre>
    $ acrylamid aco
     * Running on http://127.0.0.1:8000/
    Blog compiled in 0.12s
     * [echo 1 >> content/sample-entry.txt]
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.32s] output/2011/die-verwandlung/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.02s] output/rss/index.html
      <span style="font-weight: bold; color: #aa5500">   update</span>  [0.01s] output/atom/index.html
    Blog compiled in 0.40s
    </pre>


clean
-----

With the time Acrylamid compiles some files you later renamed or just removed.
These files are not touched until you force it with ``acrylamid clean``. This
actually run a ``acrylamid compile -q`` and tracks all visited files thus
afterwards it can show and delete untracked files in ``OUTPUT_DIR``.

If you have static files in ``OUTPUT_DIR`` you should add them to
``OUTPUT_IGNORE`` which defaults to ``['style.css', 'img/*', 'images/*']`` --
otherwise Acrylamid removes them.

-f, --force     remove all files generated by Acrylamid
-n, --dry-run   show what would have been deleted

.. raw:: html

    <pre>
    $ rm content/2012/foo.txt
    $ acrylamid clean
    <span style="font-weight: bold; color: #000316">    removed</span>  output/2012/foo/index.html
    </pre>

The syntax for patterns in ``OUTPUT_IGNORE`` is similar to ``git-ignore``: a
path with a leading slash means absolute position (to /path/to/output/),
path with trailing slash marks a directory and everything else is just
relative fnmatch.

- ``".hidden"`` matches every file named *.hidden*, ``"/.hidden"`` matches
  a file in the base directory named the same.
- ``".git/*"`` excludes *HEAD*, *config* and *description* but not the
  directories  *hooks/* and *info/*.
- ``".git/"`` ignores a *.git* folder anywhere in the output directory,
  ``"/.git/"`` only *output/.git*.

If you are unsure, wether your pattern works, use -n/--dry-run!


import
------

Acrylamid features a basic RSS and Atom feed importer as well as a WordPress
dump importer to make it more easy to move to Acrylamid. To import a feed,
point to an URL or local FILE. By default, all HTML is reconversed to Markdown
using, first html2text_ if found then pandoc_ if found, otherwise plain HTML.
reStructuredText is also supported via html2rest_ and optionally by pandoc_.

Migrating from WordPress is more difficult than an RSS/Atom feed because WP does
not store a valid HTML content but a pre-HTML state. Thus we fix this with some
stupid <br />-Tags to convert it back to Markdown/reStructuredText. It is not
recommended to import WordPress blogs as pure HTML because it does not validate!

.. _html2text: http://www.aaronsw.com/2002/html2text/
.. _html2rest: http://pypi.python.org/pypi/html2rest
.. _pandoc: http://johnmacfarlane.net/pandoc/

.. raw:: html

    <pre>
    $ acrylamid init foo  # we need a base structure before we import

    $ acrylamid import http://example.com/rss/
      <span style="font-weight: bold; color: #00aa00">   create</span>  content/2012/entry.txt
      <span style="font-weight: bold; color: #00aa00">   create</span>  content/2012/another-entry.txt
         ...
    $ acrylamid import -k example.wordpress.xml
      <span style="font-weight: bold; color: #00aa00">   create</span>  content/dan/wordpress/2008/08/a-simple-post-with-text.txt
      <span style="font-weight: bold; color: #00aa00">   create</span>  content/dan/wordpress/news/our-company.txt
         ...
    </pre>

.. note::

    If you get a *critical  Entry already exists u'content/2012/update.txt'*,
    you may change your ``PERMALINK_FORMAT`` to a more fine-grained
    ``"/:year/:month/:day/:slug/index.html"`` import strategy. If you don't
    which a re-layout of your entries, you can use ``--keep-links`` to use the
    permalink as path.

-f, --force         override existing entries, use with care!
-m FMT              reconversion of HTML to FMT, supports every language that
                    pandoc supports (if you have pandoc installed). Use "HTML"
                    if you don't whish any reconversion.
-k, --keep-links    keep original permanent-links and also create content
                    structure in that way. This does *not* work, if you links
                    are like this: ``/?p=23``.
-p, --pandoc        use pandoc first, then ``html2rest`` or ``html2text``


deploy
------

With ``acrylamid deploy TASK`` you can run single commands, e.g. push just
generated content to your server. Write new tasks into the DEPLOYMENT dict
inside your ``conf.py`` like this. You can invoke *ls*, *echo* and *deploy* as
TASK.

.. code-block:: python

    DEPLOYMENT = {
        "ls": "ls $OUTPUT_DIR",
        "echo": "echo '$OUTPUT_DIR'",
        "upload": "rsync -av --delete $OUTPUT_DIR www@server:~/blog.example.org/"
    }

The first task will print out a file listing from your output directory. The
command is pure shell, you could also use ``$HOME`` as variable. The most
configuration parameters are added to the execution environment. The second
task marks the substitution string as non-substituable and you'll get the
variable itself. The last task is a simple command to deploy your blog
directly to your server.

.. raw:: html

    <pre>
    $ acrylamid deploy ls
    <span style="font-weight: bold; color: #000316">    execute</span> ls output/
    2009
    2010
    ...
    tag

    $ acrylamid dp echo
    <span style="font-weight: bold; color: #000316">    execute</span> echo '$OUTPUT_DIR'
    $OUTPUT_DIR

    $ acrylamid deploy blog
    <span style="font-weight: bold; color: #000316">    execute</span> rsync -av --delete output/ www@server:~/blog.example.org/
    building file list ... done

    sent 19701 bytes  received 20 bytes  7888.40 bytes/sec
    total size is 13017005  speedup is 660.06
    </pre>

It's also possible to pass additional commands to tasks. Every argument and
flag/option after the task identifier is passed to:

.. raw:: html

    <pre>
    $ acrylamid deploy ls -- content/ -d
    <span style="font-weight: bold; color: #000316">    execute</span> ls output/ content/ -d
    content/
    output/
    </pre>

info
----

Prints a short summary about your blog and lists recent entries (drafted entries are grey).

.. raw:: html

    <pre>
    $ acrylamid info -2
    acrylamid <span style="color: #0000aa">0.3.4</span>, cache size: <span style="color: #0000aa">1.24</span> mb

       <span style="color: #00aa00">13 hours ago</span> Linkschleuder #24
       <span style="color: #00aa00">14 hours ago</span> <span style="color: #888888">About Python Packages</span>

    <span style="color: #0000aa">157</span> published, <span style="color: #0000aa">2</span> drafted articles
    last compilation at <span style="color: #0000aa">01. June 2012, 10:41</span>
    </pre>

-2   a git-like digit to show the last N articles. Defaults to 5.
