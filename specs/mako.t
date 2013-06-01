Test Mako tempating in Acrylamid.

  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ LANG="en_US.UTF-8" && unset LC_ALL && unset LANGUAGE
  $ acrylamid init -q --mako $TMPDIR
  $ cd $TMPDIR
  $ acrylamid compile -C
  create  [?.??s] output/articles/index.html (glob)
  create  [?.??s] output/2012/die-verwandlung/index.html (glob)
  create  [0.??s] output/index.html (glob)
  create  [0.??s] output/tag/die-verwandlung/index.html (glob)
  create  [0.??s] output/tag/franz-kafka/index.html (glob)
  create  [?.??s] output/atom/index.html (glob)
  create  [?.??s] output/rss/index.html (glob)
  create  [0.??s] output/sitemap.xml (glob)
  create  output/style.css
  9 new, 0 updated, 0 skipped [?.??s] (glob)

Clean up:

  $ rm -rf output/ theme/ content/ .cache/ conf.py
