Test (incremental) compilation.

  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ LANG="en_US.UTF-8" && unset LC_ALL && unset LANGUAGE
  $ acrylamid init -q $TMPDIR
  $ cd $TMPDIR

Can we compile? Use a decent machine, everything should compile
in less than a second.

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

If we compile a second time, nothing should happen at all (except you use a
filter with version that randomly changes, but *this* is not an intented!)

  $ acrylamid compile -Cv
  skip  output/articles/index.html
  skip  output/2012/die-verwandlung/index.html
  skip  output/index.html
  skip  output/tag/die-verwandlung/index.html
  skip  output/tag/franz-kafka/index.html
  skip  output/atom/index.html
  skip  output/rss/index.html
  skip  output/sitemap.xml
  skip  output/style.css
  0 new, 0 updated, 9 skipped [?.??s] (glob)

If we change the modification, it should re-render!

  $ touch content/sample-entry.txt

  $ acrylamid compile -Cv
  skip  output/articles/index.html
  identical  output/2012/die-verwandlung/index.html
  identical  output/index.html
  identical  output/tag/die-verwandlung/index.html
  identical  output/tag/franz-kafka/index.html
  identical  output/atom/index.html
  identical  output/rss/index.html
  identical  output/sitemap.xml
  skip  output/style.css
  0 new, 0 updated, 9 skipped [?.??s] (glob)

Acrylamid should update a file if the content changes!

  $ sleep 1
  $ echo "Foo." >> content/sample-entry.txt
  $ acrylamid compile -Cv
  skip  output/articles/index.html
  update  [?.??s] output/2012/die-verwandlung/index.html (glob)
  identical  output/index.html
  identical  output/tag/die-verwandlung/index.html
  identical  output/tag/franz-kafka/index.html
  update  [?.??s] output/atom/index.html (glob)
  update  [?.??s] output/rss/index.html (glob)
  identical  output/sitemap.xml
  skip  output/style.css
  0 new, 3 updated, 6 skipped [?.??s] (glob)

Lets try if we have really incremental rendering:

  $ acrylamid new -q Spam
  $ acrylamid compile -Cv
  update  [?.??s] output/articles/index.html (glob)
  create  [?.??s] output/2012/spam/index.html (glob)
  update  [0.??s] output/2012/die-verwandlung/index.html (glob)
  update  [?.??s] output/index.html (glob)
  skip  output/tag/die-verwandlung/index.html
  skip  output/tag/franz-kafka/index.html
  update  [?.??s] output/atom/index.html (glob)
  update  [?.??s] output/rss/index.html (glob)
  update  [0.??s] output/sitemap.xml (glob)
  skip  output/style.css
  1 new, 6 updated, 3 skipped [?.??s] (glob)

Now with templates. We have patched jinja2 template loader so we have a
recognition wether a template (including its parent templates) has changed.
*Note*, that this required BSD touch, too.

Let's change some mtimes ...

  $ touch theme/articles.html
  $ touch theme/entry.html
  $ touch theme/rss.xml
  $ touch theme/atom.xml

  $ acrylamid compile -Cv
  identical  output/articles/index.html
  identical  output/2012/spam/index.html
  identical  output/2012/die-verwandlung/index.html
  identical  output/index.html
  identical  output/tag/die-verwandlung/index.html
  identical  output/tag/franz-kafka/index.html
  identical  output/atom/index.html
  identical  output/rss/index.html
  identical  output/sitemap.xml
  skip  output/style.css
  0 new, 0 updated, 10 skipped [?.??s] (glob)

Now we touch a parent template and all inherited templates should change as, too.

  $ touch theme/base.html

  $ acrylamid compile -Cv
  identical  output/articles/index.html
  identical  output/2012/spam/index.html
  identical  output/2012/die-verwandlung/index.html
  identical  output/index.html
  identical  output/tag/die-verwandlung/index.html
  identical  output/tag/franz-kafka/index.html
  skip  output/atom/index.html
  skip  output/rss/index.html
  identical  output/sitemap.xml
  skip  output/style.css
  0 new, 0 updated, 10 skipped [?.??s] (glob)

And now vice versa: we touch completely different templates:

  $ touch theme/rss.xml

  $ acrylamid compile -Cv
  skip  output/articles/index.html
  skip  output/2012/spam/index.html
  skip  output/2012/die-verwandlung/index.html
  skip  output/index.html
  skip  output/tag/die-verwandlung/index.html
  skip  output/tag/franz-kafka/index.html
  skip  output/atom/index.html
  identical  output/rss/index.html
  identical  output/sitemap.xml
  skip  output/style.css
  0 new, 0 updated, 10 skipped [0.??s] (glob)

Now we change the base template and should see some updates:

  $ echo "Bar!" >> theme/base.html
  $ touch theme/base.html

  $ acrylamid compile -Cv
  update  [?.??s] output/articles/index.html (glob)
  update  [?.??s] output/2012/spam/index.html (glob)
  update  [0.??s] output/2012/die-verwandlung/index.html (glob)
  update  [0.??s] output/index.html (glob)
  update  [0.??s] output/tag/die-verwandlung/index.html (glob)
  update  [0.??s] output/tag/franz-kafka/index.html (glob)
  skip  output/atom/index.html
  skip  output/rss/index.html
  identical  output/sitemap.xml
  skip  output/style.css
  0 new, 6 updated, 4 skipped [?.??s] (glob)

If we change a filter in conf.py we should see an update:

  $ if [ `uname` = "Linux" ]; then
  >   sed -i -e s/\'hyphenate/\'nohyphenate/g conf.py
  > else
  >   sed -i "" -e s/\'hyphenate/\'nohyphenate/g conf.py
  > fi
  $ acrylamid compile -Cv
  skip  output/articles/index.html
  identical  output/2012/spam/index.html
  update  [?.??s] output/2012/die-verwandlung/index.html (glob)
  update  [0.??s] output/index.html (glob)
  update  [0.??s] output/tag/die-verwandlung/index.html (glob)
  update  [0.??s] output/tag/franz-kafka/index.html (glob)
  identical  output/atom/index.html
  identical  output/rss/index.html
  identical  output/sitemap.xml
  skip  output/style.css
  0 new, 4 updated, 6 skipped [?.??s] (glob)

And we should clean up everything:

  $ rm -rf output/ theme/ content/ .cache/ conf.py
