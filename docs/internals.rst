Internals
=========

Dive into Acrylamid is not that trivial as dive into Pelican or Nikola. To make it a little bit
easier I wrote this short overview possible program flows, namely:

- ``acrylamid compile``
.. - ``acrylamid clean``

Synopsis
--------

- *entry* is a single post you publish
- *filter* is a function that makes some modifications to a given input
- *view* takes a list of entries, adds some variables and yields HTML
- *cache object* is a collection of all intermediates of an entry

Initialization
--------------

- create a single ``acrylamid.Environment`` object
- initialize our cache from ``core.cache``

  - create directory if not exist
  - read all existing cache objects keys
  - load memorized keys

- create an environment for our templating engine
  using the same cache directory

  - for Jinja2, we use a custom ``core.ExtendedFileSystemLoader`` that
    can give us persistent information if a template has changed in this run.
  - for Mako, we just exploit Mako's internal mechanism to check for changed templates.
    We also substitute the function that generates the cached template's filenames
    so that we can leave them when we shutdown the cache.

- add internal filters like ``helpers.safeslug`` and ``helpers.tagify`` to the templating environment
- setup locale
- remove trailing slash from *www_root* and *path*
- get filters and views (not initializing them)

Compilation
-----------

Preparation
^^^^^^^^^^^

- if we force compilation remove cache objects
- walk through content_dir and collect all entries, sorted by date
- get filters and views (still not initialized)
- do some magic and add each filter (initialized) to an entry using a specific context, that
  means it will return a list of filters that are bound a key. Internally we build a tree
  and can compile common "ways" (intermediates) only once.
- filters are first sorted by priority, than by name

Context
^^^^^^^

- call ``view.context`` which takes and returns the environment object to provide view
  across objects, for example a tag cloud

Generation
^^^^^^^^^^

- we generate per view
- assign view's context to entry
- filter list of entries by view's condition
- generate HTML and save it to disk

  - if nothing changed, skip
  - if template has changed, rerender from cache
  - if entry has changed, remove invalid cache object keys
    and rebuilt when we access ``entry.content``

shutdown
--------

- shutdown cache

  - save memorized keys
  - remove unused cache objects and keys

- print compilation time
