Test translation feature

  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ LANG="en_US.UTF-8" && unset LC_ALL && unset LANGUAGE
  $ acrylamid init -q $TMPDIR
  $ cd $TMPDIR

Add a german and english post. No translation route so far.

  $ cat > content/hello-de.txt << EOF
  > ---
  > title: Hallo Welt
  > lang: de
  > date: 12.12.2012, 13:24
  > identifier: hello
  > ---
  > Hallo Welt!
  > EOF

  $ cat > content/hello.txt << EOF
  > ---
  > title: Hello World
  > date: 12.12.2012, 13:23
  > identifier: hello
  > ---
  > Hello World!
  > EOF

  $ acrylamid compile -Cv
  create  [0.??s] output/articles/index.html (glob)
  create  [?.??s] output/2012/hallo-welt/index.html (glob)
  create  [0.??s] output/2012/hello-world/index.html (glob)
  create  [0.??s] output/2012/die-verwandlung/index.html (glob)
  create  [0.??s] output/index.html (glob)
  create  [0.??s] output/tag/die-verwandlung/index.html (glob)
  create  [0.??s] output/tag/franz-kafka/index.html (glob)
  create  [0.??s] output/atom/index.html (glob)
  create  [0.??s] output/rss/index.html (glob)
  create  [0.??s] output/sitemap.xml (glob)
  create  output/style.css
  11 new, 0 updated, 0 skipped [?.??s] (glob)

Now we add the translation view to /:year/:slug/:lang/, this should affect a
re-generation of all views since an entry has vanished.

  $ if [ `uname` = "Linux" ]; then
  >   sed -i -e /translation/,/translation/s/[#].// conf.py
  > else
  >   sed -i "" -e /translation/,/translation/s/[#].// conf.py
  > fi

  $ acrylamid compile -Cv
  update  [0.??s] output/articles/index.html (glob)
  update  [0.??s] output/2012/hello-world/index.html (glob)
  identical  output/2012/die-verwandlung/index.html
  create  [0.??s] output/2012/hallo-welt/de/index.html (glob)
  update  [0.??s] output/index.html (glob)
  identical  output/tag/die-verwandlung/index.html
  identical  output/tag/franz-kafka/index.html
  update  [0.??s] output/atom/index.html (glob)
  update  [0.??s] output/rss/index.html (glob)
  update  [0.??s] output/sitemap.xml (glob)
  skip  output/style.css
  1 new, 6 updated, 4 skipped [?.??s] (glob)

When we now edit the translation, it should not affect anything.

  $ echo "Ohai." >> content/hello-de.txt
  $ acrylamid co -Cv
  skip  output/articles/index.html
  skip  output/2012/hello-world/index.html
  skip  output/2012/die-verwandlung/index.html
  update  [?.??s] output/2012/hallo-welt/de/index.html (glob)
  skip  output/index.html
  skip  output/tag/die-verwandlung/index.html
  skip  output/tag/franz-kafka/index.html
  skip  output/atom/index.html
  skip  output/rss/index.html
  identical  output/sitemap.xml
  skip  output/style.css
  0 new, 1 updated, 10 skipped [?.??s] (glob)

But if we edit the title, the references should check for any updates.

  $ if [ `uname` = "Linux" ]; then
  >   sed -i "s/title: Hallo Welt/title: Ohai Welt/" content/hello-de.txt
  > else
  >   sed -i "" "s/title: Hallo Welt/title: Ohai Welt/" content/hello-de.txt
  > fi
  $ acrylamid co -Cv
  identical  output/articles/index.html
  identical  output/2012/hello-world/index.html
  identical  output/2012/die-verwandlung/index.html
  create  [?.??s] output/2012/ohai-welt/de/index.html (glob)
  identical  output/index.html
  identical  output/tag/die-verwandlung/index.html
  identical  output/tag/franz-kafka/index.html
  identical  output/atom/index.html
  identical  output/rss/index.html
  update  [0.??s] output/sitemap.xml (glob)
  skip  output/style.css
  1 new, 1 updated, 9 skipped [?.??s] (glob)

Clean up.

  $ rm -rf output/ theme/ content/ .cache/ conf.py
