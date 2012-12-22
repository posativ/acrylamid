Advanced Usage
==============

Actually, most things from :doc:`usage` you'll find all other static blog
compilers.  But features from here you won't find in typical 500 lines of code
compilers.


Advanced Filter Usage
---------------------

Acrylamid already supports a few filters.  See :doc:`filters` for reference. A
few we'll point out here.

Jinja2 or Mako in entry
^^^^^^^^^^^^^^^^^^^^^^^

You can script your content with Jinja2_ or Mako_:

.. code-block:: html+jinja

    ---
    title: Test
    filters: [Markdown, Jinja2]
    ---

    [See my previous article]({{ env.prev }}).

    {% for i in range(5) %}
    - {{ i + 1 }}
    {% endfor %}

    # How about Lorem Ipsum?

    {{ lipsum(2) }}

You can do the same with Mako_, of course. Keep in mind, that both Mako_ and
Jinja2_ are always evaluated before they go through Markdown or reST. Within
your entry you have access to all variables described in :doc:`templating`.

.. _Jinja2: http://jinja.pocoo.org/
.. _Mako: http://www.makotemplates.org/


using the system's shell
^^^^^^^^^^^^^^^^^^^^^^^^

Within Mako_ or Jinja2_ you can execute shell code.  This makes it possible to
to include other files, e.g. when you write about your ``.bashrc``. You can also
show your latest commits and stuff like this. See
:func:`acrylamid.helpers.system` for API reference.

.. code-block:: html+jinja

    ---
    title: System
    filters: [Markdown, Jinja2]
    ---

    # inline git log

        $> git log -3 --no-color --oneline
        {{ "git log -3 --no-color --oneline" | system | indent(4) }}

    # pentadactyl.rc
    {{ "cat ~/.pentadactylrc" | system | indent(4, True) }}

An useful utility is `ansi2html <https://github.com/ralphbean/ansi2html>`_. It
can preserve `ANSI escape codes
<https://en.wikipedia.org/wiki/ANSI_escape_code>`_ in HTML.  Here is an example
with `lolcat <https://github.com/busyloop/lolcat>`_:

.. code-block:: html+jinja

    ---
    title: lolcat is fun
    filters: Jinja2
    ---

    {{ "lolcat -f -p 10 | ansi2html --inline" | system(lipsum(2, False)) }}


View Routing
------------

Acrylamid supports a concept called routing similar to `nanoc
<http://nanoc.stoneship.org/>`_. Unfortunately python's syntactic sugar is not
as intuitive as ruby's.  A view in Acrylamid is something like a full text
entry, RSS or Atom feed, a tag site and so on.

You can route these views with their optional arguments to any location you
like. By default, all your post are rendered to ``/:year/:slug`` but you can
also use ``/:year/:month/:day/:slug/`` (similar to WordPress). A route with
trailing slash gets automatically expanded to ``/path/index.html``.

An example from my personal blog:

.. code-block:: python

    # produce a full text version of topic
    "/topic/full/" : {
         "filters": "hyph", "view": "index", "items_per_page": 1000,
         "if": lambda e: 'topic' in e.tags
    }

This will create an additional routes for a specific topic to a location of my
choice. Routing does not remove entries from your blog articles, it only creates
a new "view". You can find all available views and their arguments :doc:`here
<views>`.


Static Pages
------------

For WordPress-like pages, just change the `type` to page like this::

    ---
    title: About
    type: page
    ---

    ...

and in your conf.py view configuration, add::

    "/:slug/": {"view": "page"}


Translations
------------

Since version 0.4 Acrylamid has also support for translated posts. To enable the
Translation view, add this to your :doc:`conf.py <conf.py>`:

.. code-block:: python

    '/:year/:slug/:lang/': {
        'view': 'translation', 'template': 'main.html'
    }

Translations are posts with the same `identifier` and a different `lang`
attribute. An example:

The English article::

    ---
    title: Foobar is not dead
    identifier: foobar-is-not-dead
    ---

    That's true, foobar is still alive!

And the French version::

    ---
    title: Foobar n'est pas mort !
    identifier: foobar-is-not-dead
    lang: fr
    ---

    Oui oui, foobar est toujours vivant !

If the blog language is ``"en"`` then the english article will be included into
the default listing but the french version not. You can link to the translated
versions with:

.. code-block:: html+jinja

    {% if 'translation' in env.views and env.translationsfor(entry) %}
    <ul>
        {% for tr in env.translationsfor(entry) %}
            <li><strong>{{ tr.lang }}:</strong>
                <a href="{{ env.path ~ tr.permalink }}">{{ tr.title }}</a>
            </li>
        {% endfor %}
    </ul>
    {% endif %}
