from distutils.core import setup

"""acrylamid documentation
=======================

acrylamid is yet another lightweight static blogging software written in python
and designed to get a high quality output. Its licensed under BSD Style, 2 clauses.

Features
********

- blog articles, pages and rss/atom feeds
- theming support (using jinja2_)
- Markdown_ and reStructuredText_ as markup languages
- MathML generation using AsciiMathML_
- hyphenation using `&shy;`
- modern web-typography

.. _jinja2: http://jinja.pocoo.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _AsciiMathML: http://www1.chapman.edu/~jipsen/mathml/asciimath.html

Quickstart
**********

::

    pip install acrylamid

You'll need ``python``, ``jinja2`` and either ``markdown`` (default) or
``docutils``. ``pygments`` and ``asciimathml`` for colored code listings
respectively MathML. Typography needs ``smartypants``. To get a full-featured
installation do:

::

    pip install docutils pygments asciimathml smartypants

Get acrylamid and edit *conf.yaml* and *layouts/*. Run acrylamid with:

::

    $> acrylamid init myblog
        create  myblog/content/
        ...
    $> cd myblog/
    $> acrylamid gen
          warn  using mtime from <fileentry f'content/sample entry.txt'>
        create  '/articles/index.html', written to output/articles/index.html
        create  'Die Verwandlung', written to output/2011/die-verwandlung/index.html
        create  '/atom/index.html', written to output/atom/index.html
        create  '/rss/index.html', written to output/rss/index.html
        create  '/', written to output/index.html

Using acrylamid
***************

- `conf.yaml <https://github.com/posativ/acrylamid/blob/master/docs/conf.yaml.rst>`_
- `filters <https://github.com/posativ/acrylamid/blob/master/docs/filters.rst>`_

Filters
**********

See `docs/filters.rst
<https://github.com/posativ/acrylamid/blob/master/docs/filters.rst>`_ for
detailed information. Currently supported by acrylamid:

- **markdown**: rendering Markdown (+asciimathml,pygments)
- **rest**: reStructuredText (+pygments)
- **typography**: https://code.google.com/p/typogrify/ (and custom modifications)
- **summarize**: summarizes posts to 200 words
- **hyphenation**: hyphenate words (len > 10) based on language
- **head_offset**: decrease headings by offset
- **pass-through**: don't render with Markdown or reStructuredText

Views
*****

- **articles**: articles overview
- **entry**: renders single entry to given slug
- **index**: creates pagination / and /page/:num
- **feeds**: valid atom/rss feed
- **tags**: sort by tag with pagination (/:tag and /:tag/:num)
"""

hyph_files = ['hyph-de-1996.chr.txt', 'hyph-en-us.chr.txt', 'hyph-fr.chr.txt',
    'hyph-de-1996.lic.txt', 'hyph-en-us.lic.txt', 'hyph-fr.lic.txt',
    'hyph-de-1996.pat.txt', 'hyph-en-us.pat.txt', 'hyph-fr.pat.txt']

setup(
    name='acrylamid',
    version='0.2.0',
    author='posativ',
    author_email='info@posativ.org',
    packages=['acrylamid', 'acrylamid.filters', 'acrylamid.views'],
    scripts=['bin/acrylamid'],
    package_data={'acrylamid.filters': ['hyph/*.txt']},
    url='http://pypi.python.org/pypi/acrylamid/',
    license='LICENSE.txt',
    description='yet another static blog generator',
    long_description=__doc__,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
    ],
    install_requires=[
        'Jinja2>=2.4',
        'Markdown>=2.0.1',
        'translitcodec>=0.2'
    ],
)
