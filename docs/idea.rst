Idea
====

Acrylamid is not a dumb blog compiler. Over one thousand lines of code have
been written to detect changes in your blog and reflect these changes with
minimum effort in the output while on the other side being highly modular. How
is this done?


Fundamental Concepts
--------------------

#. Caching. Acrylamid caches *everything*. So if you have several pages on your
   blog index and you add a new entry, it pulls all existing entries from its
   cache without any recompilation.

#. Explicit modification recognition. Only two things can change: content or
   layout. If the content changes, only this specific item must be re-compiled.
   If you modify your layout, all content is retrieved from cache.

#. Lazy evaluation. Acrylamid is that lazy; it even delays the import of
   libraries. If you write your current article in Markdown, why should it
   initialize ``docutils`` that takes nearly half a second to import?

That is the idea behind. Now how it is actually implemented. Instead of rushing
from beginning to the end, we do it reverse.


Implementation
--------------

View :
    An Atom feed, an index page with a summarized listing of recent posts, a full
    version of that entry, an articles overview. A view generates that and also
    checks whether a page must be re-compiled or can be skipped.

    Now the best: you can add as many views as you like. You route them to your
    index page or render out a full-text feed beside a summarized feed. Acrylamid
    will find out the most efficient way to compile your content to HTML.

Filters :
    A filter is like a UNIX pipe. It gets text, processes it and returns
    text (preferably HTML). You can apply as many filters as you like all
    content, per view or per entry. That's also the hierarchy. A filter
    specified in an entry will always override per view or global filters (but
    only if the filter is in conflict with other filters such as Markdown vs.
    reStructuredText).

You may ask why you need multiple filters per entry and/or per view? Well, let
me explain: you write some text, and you are to lazy to sum up the context. A
filter can do that for you. You prefer hyphenation in your browser, but don't
want it in your feed. But you have to.

Here is an example configuration::

    FILTERS = ["Markdown", "hyphenation"]
    VIEWS = {
        # h1 means headings decreased by 1, h2 by 2 ...
        '/:year/:slug/': {'view': 'entry', filters: ['h1', ]},
        '/':             {'view': 'index', filters: ['h1', 'summarize']},
        '/atom/':        {'view': 'atom',  filters: ['h3', 'nohyphenate']}
    }

So, how does Acrylamid figure out, that the markup can be used for multiple
routes? It basically builds a tree with all used paths and looks whether a
path can be used more than once:


.. blockdiag::

    blockdiag concept {
      orientation = portrait
      Markdown -> "h3" -> "/atom/";
      Markdown -> hyphenation -> "h1" -> "/:year/:slug/";
      Markdown -> hyphenation -> "h1" -> summarize -> "/";
    }

You can clearly see that markdown conversion is only computed once and is re-
used. That makes it possible to re-adjust the maximum of words you want to
summarize without any markdown conversion. It simply uses the cached version.

Using a disk cache makes it also possible to track changes. Each time you
modify the filter chain (evaluated per entry) it figures out what
intermediates are not used anymore and which ones are not affected.


Trivia
------

Q : What is the overhead of saving each intermediate to disk?

    I can only give my personal blog as comparison: 165 articles are using
    1.45 mb cache. Actually all intermediates are minimized with ``zlib``.

Q : How fast is Acrylamid in comparison to Pelican, Octopress, Nikola?

    For what it's worth: Pelican and Acrylamid are almost equally fast
    in their default configuration, although Acrylamid has hyphenation active
    and renders much more pages like tags and index.

    When it comes to incremental updates, Acrylamid is much faster than
    Pelican (something like "less than a second versus several seconds").
