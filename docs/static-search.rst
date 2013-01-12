Search
======

A space-efficient and fast full text search engine for Acrylamid using
compressed `suffix trees`_ (CST).  In comparison to a single index file
like in Sphinx_ this has several advantages:

  - :math:`O(\frac{1}{27} n \log n)` instead of :math:`O(n)` space efficiency
  - full text search with no arbitrary character set limitation
  - exact and partial matches in :math:`O(m) + O(k \log n)`

.. For the record (index for around 170 posts):

..  - JSON index with no special characters allowed (such as dash): 375k (132k gzipped)
..  - CST  index with special characters (except punctuation): 42k (12k gzipped) per prefix

So, what is a prefix?  The idea is, that a user does mostly search for a
single keyword a single time and maybe with a refinement afterwards. The user
does not need to load the whole site index just to query for "python" or
"python project". With (compressed) suffix trees, it is possible to split
the index to one-character prefixes. In the example, `p` for `python` and
fortunately even for `project`. Acrylamid can construct in :math:`O(n \log n)`
for a constant size alphabet. The alphabet use 26 lowercase ascii characters
and a tree for everything else, hence :math:`O(\frac{1}{27} n \log n)` space
efficiency per sub tree. In practice (due tree compression) this is more
space-efficient than a global index (42k versus 375k in average for 170 posts).

Like Sphinx_ the index only links to the article containing the keyword and
does not provide any context.  Hence, the search view renders a plain text
version of all posts and the API provides a method to get up to N paragraphs
containing the keyword (loaded asynchronously in background).

.. _suffix trees: https://en.wikipedia.org/wiki/Suffix_tree
.. _Sphinx: http://sphinx-doc.org/

Usage
-----

Note, that the new default theme includes the static site search by default.
Just enable the search view in your configuration and point to a directory
where you would like to store the index.

.. code-block:: python

    '/search/': {'view': 'search', 'filters': 'strip+pre'}  # ignores <pre> tag

The search view does not run by default because the construction of a compressed
suffix tree is very expensive. Hence, supply ``--search`` to build the index.

.. code-block:: sh

    $ acrylamid compile --search

You can query the CST as shown in the example below.  You still have to
highlight the keyword yourself. The API only returns you the article and
optional a context.

.. code-block:: html

    <head>
        <script type="text/javascript" src="/search/search.js"></script>
        <script type="text/javascript">

        function doit() {

            var rv, keyword = document.getElementById("searchinput").value;
            rv = search(keyword);  // returns a tuple [[1, 2], [1, 3]]

            console.log(rv);

            // context for first exact match
            if (typeof rv != "undefined")
                console.log(search.context(keyword, rv[0][0]));
        }

        </script>
    </head>
    <body>
        <form onsubmit="return false;">
            <input type="text" id="searchinput" onchange="doit()">
        </form>
    </body>

Javascript API
--------------

.. js:function:: search(keyword)

   :param keyword: keyword to search for
   :returns: a tuple of exact matches and partial matches as array or
             undefined if not found

.. js:function:: search.context(keyword, id[, limit=1])

    :param keyword: keyword used for :js:func:`search`
    :param int id: id from search result
    :param int limit: limit context to N paragraphs
    :returns: a list of paragraphs containing the keyword

.. js:attribute:: search.lookup

    An id to entry mapping. Use the ids from :js:func:`search` to get a tuple
    containing the (relative) permalink and title back.

.. js:attribute:: search.path

    Relative location of the search index.
