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

performance tweaks
******************

Though acrylamid caches as much as possible, re-generation in worst-case can
be something like f(x) = 0.5 + 0.1x where x is the amount of entries
processed. *f(x)* returns the computing time if you have expensive
filters like *hyphenate* or *reStructuredText*.
On my MacBook (i5 2,4 Ghz) *hyphenate* takes around 257 ms for each language
just for generating the pattern. To just import *reStructuredText* from
``docutils`` the interpreter spends 191 ms to compile regular expressions.

If acrylamid is too slow, first thing you can do is to **turn off
hyphenation**. If a single entry changes (must not be a reStructuredText post)
it loads at least the default language pattern and adds a huge constant in
`*O*-notation <https://en.wikipedia.org/wiki/Big_O_notation>`_. Below a short
profiling of generation using hyphenate and reST filters.

::
    
    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
         1    0.000    0.000    0.685    0.685 acrylamid:7(<module>)
     14263    0.130    0.000    0.257    0.000 hyphenation.py:45(_insert_pattern)
     25/23    0.004    0.000    0.244    0.011 {__import__}
     28848    0.031    0.000    0.201    0.000 re.py:228(_compile)
         1    0.003    0.003    0.191    0.191 rst.py:7(<module>)
       174    0.001    0.000    0.161    0.001 sre_compile.py:495(compile)

**Use Markdown instead of reST**, but this may optional. Acrylamid only
imports docutils if needed (= when an entry using reST has changed).