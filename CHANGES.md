# Acrylamid Changelog

Version 0.5
----------

Not released – TBD

### What is new?

- #78 – `acrylamid import` now uses RSS/Atom categories as tags
- #80 – new config variable `CONTENT_EXTENSION` to set the default filename
  extension when using `acrylamid new`, defaults to `.txt` (Günter Kolousek)

### What changes?

- `env.views` is now a list containing the actual view objects, but retains
  `if 'sitemap' in env.views` and `env.views['sitemap']` syntax.

### What was fixed?

- #82 – theme files copied to output if they are not used
- #77 – missing items in sitemap view
- #75 – dotfiles not copied from the static folder (Mark van Lent)

Version 0.4
-----------

Released on September, 19th 2012 – Arrr!

### What's new?

- support for translations, #22
- Mako as second templating engine of choice, #39
- opt-in for native markdown and reStructuredText metadata style, #40
- `acrylamid autocompile` now detects layout and conf.py changes, #48
- new kind of entry – page – that should be used for static sites, #50
- summarize by keyword, #51
- new Mako filter, #52
- asset handling, #62
- per-tag feeds, #68
- support for LESS, SASS and SCSS
- new theme "shadowplay"
- subcommand `acrylamid ping` for PingBack and Twitter announces
- superscript, subscript and delins extensions for Markdown
- compatibility for russion and asian characters to ASCII
  via unidecode
- ability to add custom metadata pairs to entry header on import

### What changes?

- discover Markdown and reST extension in `FILTERS_DIR`
- `ENTRIES_IGNORE` was renamed to `CONTENT_IGNORE`, a list of git-like patterns
- new `SUMMARIZE_LINK` for continue reading link instead of the old three
  `SUMMARIZE_*` variables to allow more customization, #45
- `LAYOUT_DIR` was renamed to `THEME`
- `PERMALINK_FORMAT` is no longer used. Acrylamid will automatically determine
  the permalink format or you can explicitly set it with `ENTRY_PERMALINK` and
  `PAGE_PERMALINK`

### Bugfixes

Way too many to mention here. Over 700 (!) commits from 0.3.5. I would like to
thank @markvl, @moschlar and @t-8ch for their patches and patience to test
broken builds.


Version 0.3
-----------

### 0.3.5

- new command `acrylamid check` W3C compliance and validates external
  links, closes #32
- new command `acrylamid info` showing version, cache size and latest
  articles and number of drafted and published writings.
- add previous and next relations to single entry, closes #29
- entry has now zero-padded day and month, thanks to Mark, #37
- default smartypants behaviour is now unmodified, custom changes
  require TYPOGRAPHY_MODE = "a", see #36 (thanks to Mark)
- compilation summary and hide skip/identical by default
- deployments are now executed in a real shell environment
- verified python 3 support (via p3test.sh)
- templates are now configurable per view, #24
- use argparse instead of optparse
- few bugfixes to core (that induces new compilation :-/)

### 0.3.4

- per entry settings for summarize filter
- add split filter to jinja filter
- fix a block when importing something
- unicode awareness
- experimental python 3 support (!)
- new filter: Discount – a faster Markdown implementation

### 0.3.3

- new sitemap generator
- add experimental bash_completion (source it from GitHub repository)
- `acrylamid deploy` now shows available tasks when no argument is given
- add SSL and start options for reST's YouTube directive
- new test framework `cram`
- new API: you can now register callbacks to events (sitemap view
  and `acrylamid clean` are implemented that way).
- refactoring and first API docs available under
  http://posativ.org/acrylamid/ (yes, that's the Werkzeug theme).
- lazy imports to ease writing custom filters
- less I/O on cache objects (= speed improvements)
- fix invalid cache objects
- fix unescaped attributes
- more robust error handling for filters

### 0.3.2

- use a single, compressed cache file for each entry
- fix (hopefully) the last issue with system locales
- don't touch permalinks with trailing slash
- make custom keys in YAML header available in templating
- new YouTube embed code for reStructuredText
- new metalogo filter by sebix
- add explicit `static` for static pages
- fix a serious issue where <tag foo> raises an exception
- clean removes abandoned cache files as well, #27
- add filter version, #26

### 0.3.1

- new content filter: textile (thanks to sebix)
- add import for WordPress (thanks to ametaireau/pelican) and Atom
- new reStructuredText directives: code (JS), code-block (Pygments)
  and YouTube
- bugfixes in various built-in filters and internals
- deployment is no longer limited to a single command (thanks to sebix)
- deployment has now incremental output
- Markdown 2.1 compatibility for asciimathml

### 0.3.0

Released on April, 1th 2012 – Aprilscherz

- new command `acrylamid new` to create a new post with some defaults
- new command `acrylamid view` an internal webserver to view your output
- new command `acrylamid autocompile` automatically compile if something as
  has changed and a parallel running webserver on port -p 8000
- new command `acrylamid clean` to clean untracked files (orphans)
- new command `acrylamid deploy` to run your own commands with acrylamid
- new command `acrylamid import` to import content from an existing RSS feed
- new condition property in Filter so you can e.g. make a per-tag feed or
  get multilanguage support in your blog
- new jinja2, acronyms and pandoc filters
- new HTML5 layout (and it even validates)
- pelican inspired configuration
- optional PyYAML support
- documentation
- major refactoring
- API overhaul
- tons of bugfixes
- sub-uri support
- some unit tests
- speed improvements

Version 0.2
-----------

### 0.2.2

- add static page support (see docs/howtows.rst)
- fix update when entry moved/drafted

### 0.2.1

- new draft feature that excludes entries from everything except entry view
- minor bugfixes

### 0.2.0

Released on 16th December 2011

- introduced caching
- lazy evaluation for expensive operations
- first docs

Version 0.1.11
--------------

- Tag-View
- pass-through filter
- removed pyyaml dependency

Version 0.1.10
--------------

Initial release, released on November 16th 2011
