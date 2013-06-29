Preprocessors
=============

Filters that are executed before compiling the markup language to HTML are
called preprocessors.

.. _filters-pre-jinja2:

Jinja2
------

In addition to HTML+jinja2 templating you can also use `Jinja2
<http://jinja.pocoo.org/docs/>`_ in your postings, which may be useful when
implementing a image gallery or other repeative tasks.

Within jinja you have a custom ``system``-filter which allows you to call
something like ``ls`` directly in your content (use it with care, when you
rebuilt this content, the output might differ).

::

    ---
    title: "Jinja2's system filter"
    filters: jinja2
    ---

    Take a look at my code:

    .. code-block:: python

        {{ "cat ~/work/project/code.py" | system | indent(4) }}

    You can find my previous article "{{ env.prev.title }}" here_. Not
    interesting enough? How about lorem ipsum?

    {{ lipsum(5) }}

    .. _here: {{ env.prev }}

Environment variables are the same as in :doc:`templating` plus some imported
modules from Python namely: ``time``, ``datetime`` and ``urllib`` because you
can't import anything from Jinja2. You can also access the root templating
environment when Jinja2. This means, you can import and inherit from templates
located in your theme folder.

For convenience, the Jinja2 filter automatically imports every macro from
``macros.html`` into your post context, so there is no need for a
``{% from 'macros.html' import foo %}``.

============  ==================================================
Requires      <built-in>
Aliases       Jinja2, jinja2
============  ==================================================

.. _filters-pre-mako:

Mako
----

Just like Jinja2 filtering but using Mako. You have also ``system`` filter
available within Mako. Unlike Jinja2 Mako can import python modules during
runtime, therefore no additional modules are imported into the namespace.

============  ==================================================
Requires      `mako <http://docs.makotemplates.org/>`_
Aliases       Mako, mako
============  ==================================================


.. _filters-pre-liquid:

Liquid
------

Implementation of most plugins of the Jekyll/Octopress project. This filter
(unfortunately) can not be used with reST or any other markup language, that
can not handle inline HTML.

The liquid filters are useful of you are migrating from Jekyll/Octopress or
look for an inofficial standard (rather than custom Markdown extensions) that
is used by Jekyll_/Octopress_, Hexo_.

.. _Jekyll: https://github.com/mojombo/jekyll/wiki/Liquid-Extensions#tags
.. _Octopress: http://octopress.org/docs/plugins/
.. _Hexo: http://zespia.tw/hexo/docs/tag-plugins.html

Currently, the following tags are ported (I reference the Octopress plugin
documentation for usage details):

- blockquote__ -- generate beautiful, semantic block quotes
- img__ -- easily post images with class names and titles
- youtube__ -- easy embedding of YouTube videos
- pullquote__ -- generate CSS only pull quotes — no duplicate data, no javascript
- tweet__ -- embed tweets using Twitter's oEmbed API

__ http://octopress.org/docs/plugins/blockquote/
__ http://octopress.org/docs/plugins/image-tag/
__ http://www.portwaypoint.co.uk/jekyll-youtube-liquid-template-tag-gist/
__ http://octopress.org/docs/plugins/pullquote/
__ https://github.com/scottwb/jekyll-tweet-tag

If you need another plugin, just ask on `GitHub:Issues
<https://github.com/posativ/acrylamid/issues>`_ (plugins that will not
implemented in near future: Include Array, Render Partial, Code Block).

============  ==================================================
Requires      <built-in>
Aliases       liquid, octopress
============  ==================================================
