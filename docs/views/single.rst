Single-Entry
============

.. _views-entry:

Entry
-----

Creates single full-length entry
(`Example <http://blog.posativ.org/2012/nginx/>`__).

To enable Entry view, add this to your :doc:`conf.py`:

.. code-block:: python

    '/:year/:slug/': {
        'view': 'entry',
        'template': 'main.html'  # default, includes entry.html
    }

The entry view renders an post to a unique location and should be used as
permalink URL. The url is user configurable, but may be overwritten by
setting ``ENTRY_PERMALINK`` explicitly to a URL in your configuration.

This view takes no other arguments and uses *main.html* and *entry.html* as
template.

.. _views-page:

Page
----

Creates a static page. To enable Entry view, add this to your :doc:`conf.py`:

.. code-block:: python

    '/:year/:slug/': {
        'view': 'page',
        'template': 'main.html'  # default, includes entry.html
    }

The page view renders an post to a unique location withouth any references
to other blog entries. The url is user configurable, but may be overwritten by
setting ``PAGE_PERMALINK`` explicitly to a URL in your configuration.

This view takes no other arguments and uses *main.html* and *entry.html* as
template.

.. _views-translation:

Translation
-----------

Creates translation of a single full-length entry.  To enable the
Translation view, add this to your :doc:`conf.py`:

.. code-block:: python

    '/:year/:slug/:lang/': {
        'view': 'translation',
        'template': 'main.html',  # default, includes entry.html
    }

Translations are posts with the same `identifier` and a different `lang` attribute.
An example:

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
versions via:

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
