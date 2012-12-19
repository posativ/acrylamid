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
