Commands
========

init
----

new
---

compile
-------

autocompile
-----------

view
----

import
------

Acrylamid features a basic RSS and Atom feed importer (WordPress dump is
planned) to make it more easy to move to Acrylamid. To import a feed, point to
an URL or local FILE. By default, all HTML is reconversed to Markdown using,
first pandoc_ if found, then `html2text
<http://www.aaronsw.com/2002/html2text/>`_ if found, else the plain HTML is
stored into plaintext files. reStructuredText is also supported by pandoc_ and
optional by `html2rest <http://pypi.python.org/pypi/html2rest>`_.

.. _pandoc: http://johnmacfarlane.net/pandoc/

::

    $> acrylamid import http://example.com/rss/
         create  content/2012/entry.txt
         create  content/2012/another-entry.txt
         ...

.. note::

    If you get a *critical  Entry already exists u'content/2012/update.txt'*,
    you may change your ``PERMALINK_FORMAT`` to a more fine-grained
    ``"/:year/:month/:day/:slug/index.html"`` import strategy. If you don't
    which a re-layout of your entries, you can use ``--keep-links`` to use the
    permalink as path.

--markup=LANG       reconversion of HTML to LANG, supports every language that
                    pandoc supports (if you have pandoc installed). Use "HTML"
                    if you don't whish any reconversion.
--keep-links        keep original permanent-links and also create content
                    structure in that way. This does *not* work, if you links
                    are like this: ``/?p=23``.


deploy
------

With ``acrylamid deploy TASK`` you can run single commands, e.g. push just
generated content to your server. Write new tasks into the DEPLOYMENT dict inside
your ``conf.py`` like this:

::

    DEPLOYMENT = {
        "ls": "ls",
        "echo": "echo %s",
        "blog": "rsync -av --delete %s www@server:~/blog.example.org/"
    }

Now, you can invoke *ls*, *echo* and *blog* as TASK. This example config shows
you all possibilities to create a scripts. A plain ``ls`` is internally extended
to ``ls %s`` where ``%s`` is substituted with the current ``OUTPUT_DIR``-variable
as you can see in the second task). The third task is simple command to deploy
your blog directly to your server -- notice the substitution variable can be
anywhere.

::

    $> acrylamid deploy ls
        2009
        2010
        ...
        tag

    $> acrylamid deploy echo
        output/

    $> acrylamid deploy blog
        building file list ... done

        sent 19701 bytes  received 20 bytes  7888.40 bytes/sec
        total size is 13017005  speedup is 660.06

It's also possible to pass additional commands to these tasks. Every argument after
the task identifier is passed to and using ``--`` as delimiter for acrylamid's flags
you can also apply opts and long-opts:

::

    $> acrylamid deploy ls -- content/ -d
        content/
        output/
