Knowledge base
==============

Per-Tag Feed
************

A single feed pretty easy, just add this into your *conf.py*:

.. code-block:: python

    '/my/feed': {'view': 'feed', 'if': lambda e: 'whatever' in e.tags}

To have a feed for all tags, we must use a little more python. TODO!

Image Gallery
*************

Acrylamid does not ship an image gallery and will properbly never do -- it's
too complex to fit to everyones need. But that does not mean, you can not have
a automated image gallery. You can write:

.. code-block:: html+jinja

    {% set images = "ls output/img/2012/st-petersburg/*.jpg" | cut -d / -f 5"  %}
    {% for bunch in images | system | split | batch(num) %}
    <figure>
      {% for file in bunch %}
      <a href="/img/2012/st-petersburg/{{ file }}" style="float: left; width: 25%">
      <img src="/img/2012/st-petersburg/thumbs/{{ file }}" width="150" height="150"
           alt="{{ file }}"/>
      </a>
      {% endfor %}
    </figure>
    <br style="clear: both" />
    {% endfor %}

this into your jinja2-enabled post (= ``filter: jinja2``) and make sure you
point to your image location. To convert thumbnails from your images, you
can use `ImageMagick's`_ convert to create 150x150 px thumbnails in *thumbs/*:

.. code-block:: bash

    $ for file in `ls *.jpg`; do
    >   convert -define jpeg:size=300x300 $file -thumbnail 150x150^ -gravity center -extent 150x150 "thumbs/$file";
    > done

.. _ImageMagick's: http://www.imagemagick.org/

That will look similar to my blog article about `St. Petersburg <http://blog.posativ.org/2012/impressionen-aus-russland-st-petersburg/>`_.

Performance Tweaks
******************

Markdown instead of reStructuredText as markup language might be faster.
Another important factor is the typography-filter (disabled by default) which
consumes about 40% of the whole compilation process. If you don't care about
web typography, disable this feature gives you a huge performance boost when
you compile your whole site.

A short list from slow filters (slowest to less slower):

1. Typography
2. Acronyms
3. reStructuredText
4. Hyphenation

Though reStructuredText is not *that* slow, it takes about 300 ms just to
initialize itself. But Typography as well as Acronyms and Hyphenation are
limited by their underlying library, namely :class:`HTMLParser` and
:class:`re`.

.. _PCRE: http://www.pcre.org/

Static Site Search
******************

.. note:: This does not work with our HTML5 theme (default)

Currently acrylamid has no support for an integrated search based on the
`sphinx' approach <http://sphinx.pocoo.org/>`_, therefore you can either use
`Google Custom Search <https://www.google.com/cse/>`_, `Tapir
<http://tapirgo.com/>`_ or an independend listed here. This work is completely
stolen from `Joe Vennix on Forrst
<http://forrst.com/posts/Static_site_e_g_Jekyll_search_with_JQuery-zL9>`_ and
only modified to match acrylamid's default layout (and fixing some issues).

.. code-block:: console

    cd ~/your/blog/output
    mkdir js images
    wget http://code.jquery.com/jquery-1.7.1.min.js -O js/jquery-1.7.1.min.js
    wget http://github.com/cowboy/jquery-bbq/raw/master/jquery.ba-bbq.min.js -O js/jquery.ba-bbq.min.js
    wget https://gist.github.com/gists/1575138/download -O js/search.js
    cd images/
    wget http://joevennix.com/images/searchicon.png
    wget http://joevennix.com/images/closelabel.png
    wget http://joevennix.com/images/ajax-loader.gif

layouts/main.html
-----------------

.. code-block:: html
    :emphasize-lines: 7-9, 14-20

    <!DOCTYPE html
      PUBLIC "-//W3C//DTD XHTML 1.1 plus MathML 2.0//EN"
             "http://www.w3.org/Math/DTD/mathml2/xhtml-math11-f.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <!-- ... -->
      <link media="all" href="/blog.css" type="text/css" rel="stylesheet" />
      <script type="text/javascript" src="/js/jquery-1.7.1.min.js"></script>
      <script type="text/javascript" src="/js/jquery.bbq.min.js"></script>
      <script type="text/javascript" src="/js/search.js"></script>
      <link href="/favicon.ico" rel="shortcut icon" />
      <!-- ... -->
                <a href="/articles/">articles</a>
            </li>
            <li>
              <div id="search">
                <form id="search_form" method="POST">
                    <input type="text" id="query" name="query" style="display: inline-block; width: 120px;">
                </form>
              </div>
            </li>
        <!-- ... -->

output/blog.css
---------------

.. code-block:: css

    #blogheader #search {
      margin-right: 5%;
      text-align: right; }
    #blogheader #search input {
      background: url("/images/searchicon.png") no-repeat scroll 0 0 white;
      border: 1px solid #aaaaaa;
      border-radius: 15px 15px 15px 15px;
      box-shadow: 0 0 1px 1px #f2f2f2 inset;
      padding: 3px 10px 3px 30px; }

    #blogbody .results_row {
      border-bottom: 1px dotted #aaaaaa;
      padding: 5px;
      clear: both; }
    #blogbody .results_row_left {
      display: inline;
      font-size: 1.3em; }
    #blogbody .results_row_left a {
      font-family: Helvetica, Arial, sans-serif;
      font-weight: normal;
      padding: 5px; }
    #blogbody .results_row_right {
      color: #333333;
      display: block;
      padding-top: 9px;
      float: right;
      color: #333333;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 0.8em; }
    #blogbody #loader {
      text-align: center;
      margin-top: 100px;
      height: 25px;
      width: 100%;
      background: url(/images/ajax-loader.gif);
      background-position: center;
      background-repeat: no-repeat; }
