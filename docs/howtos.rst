HowTos
======

about-page and other static pages
*********************************

If you want set up an about page like in WordPress you can
use an easy (but not intuitive) trick:

::

	---
	title: About Me
	draft: True
	permalink: /about/
	---

A YAML-header like this will hide the entry from the tag/page/article
views. Save static pages for example to ``content/about.txt`` instead
of ``content/2011/``.

This will render the entry (processed by the entry-view
and filters) into the given location */about/*.