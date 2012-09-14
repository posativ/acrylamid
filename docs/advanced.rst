Advanced Usage
==============

Actually, most things from :doc:`usage` you'll find all other static blog
compilers.  But now some features you won't find in typical 500 lines of code
compilers.

Advanced Filter Usage
---------------------

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
