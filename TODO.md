extensions
------------

- multilang
- disqus

0.1
-------

- think of some more tools.py functions to provide easier access to feedgenerators and
  such things
- speed up re-generation:
    - avoid rendering entries which have not changed
    - calculate which pages/feeds have to be regenerated
    - use timestamp delta, to get modified entries (including rendering offset)
- custom title
- draft generation (not included in feeds, pages and articles overview)
- colored INFO, WARN, ERROR -> take a look at nanoc's color sheme

## known issues:

- hardcoded ignore directory in filelist
- check entry's dict in tt.render()
- summarizing + &shy; produces syllable orphan
- MathML only works in Firefox -> fallback using some stupid JS:
    http://www.mathjax.org/ | http://www1.chapman.edu/~jipsen/mathml/asciimath.html

## chores

- don't conf.get(key, default) all the time, set default once and forever

0.2
-------

- automatic keywords generation: <meta content="tags" name="keywords">
  based on optional tag-key and most used, non-default-lang words
- tag view (and tagcloud?)
- i18n
- HTML Tidy extension
- HTML validation

## ideas from [pelican](http://docs.notmyidea.org/alexis/pelican/)

- summary key in entry for <meta content="summary" name="description">
  (fallback to a summarize up to 30|40|50 words?)
- 

0.3
-------

- WordPress Theme Import
- deployment
- more filters from [nanoc](http://nanoc.stoneship.org/)