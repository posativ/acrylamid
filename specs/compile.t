Test (slow) full-featured compilation

  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ LANG="de_DE.UTF-8" && unset LC_ALL && unset LANGUAGE
  $ acrylamid init -q $TMPDIR
  $ cd $TMPDIR

When we use BSD touch we always have to reset the timestamps after
each test otherwise we may break following tests. This is done via
`find output -exec /usr/bin/touch -A 00 {} \;`.

Can we compile? Use a decent machine, everything should compile
in less than a second.

  $ acrylamid compile -C
  create  \[0.\d+s\] output/articles/index.html (re)
  create  \[0.\d+s\] output/2012/die-verwandlung/index.html (re)
  create  \[0.\d+s\] output/rss/index.html (re)
  create  \[0.\d+s\] output/atom/index.html (re)
  create  [0.00s] output/index.html
  create  [0.00s] output/tag/die-verwandlung/index.html
  create  [0.00s] output/tag/franz-kafka/index.html
  Blog compiled in 0.\d+s (re)

If we compile a second time, nothing should happen at all (except you use a
filter with version that randomly changes, but *this* is not an intented!)

  $ acrylamid compile -C
  skip  output/articles/index.html
  skip  output/2012/die-verwandlung/index.html
  skip  output/rss/index.html
  skip  output/atom/index.html
  skip  output/index.html
  skip  output/tag/die-verwandlung/index.html
  skip  output/tag/franz-kafka/index.html
  Blog compiled in 0.\d+s (re)

If we change the modification but this require a BSD touch, because GNU's
touch sucks!

  $ /usr/bin/touch -A 15 content/sample-entry.txt

  $ acrylamid compile -C
  skip  output/articles/index.html
  identical  output/2012/die-verwandlung/index.html
  identical  output/rss/index.html
  identical  output/atom/index.html
  identical  output/index.html
  identical  output/tag/die-verwandlung/index.html
  identical  output/tag/franz-kafka/index.html
  Blog compiled in 0.\d+s (re)

  $ /usr/bin/touch -A 00 content/sample-entry.txt
  $ find output -exec /usr/bin/touch -A 00 {} \;

Acrylamid should update a file if the content changes!

  $ echo "Foo." >> content/sample-entry.txt
  $ acrylamid compile -C
  skip  output/articles/index.html
  update  \[0.\d+s\] output/2012/die-verwandlung/index.html (re)
  update  \[0.\d+s\] output/rss/index.html (re)
  update  \[0.\d+s\] output/atom/index.html (re)
  identical  output/index.html
  identical  output/tag/die-verwandlung/index.html
  identical  output/tag/franz-kafka/index.html
  Blog compiled in 0.\d+s (re)

  $ /usr/bin/touch -A 00 content/sample-entry.txt
  $ find output -exec /usr/bin/touch -A 00 {} \;

Lets try if we have really incremental rendering:

  $ acrylamid new -q Spam
  $ acrylamid compile -C
  update  \[0.\d+s\] output/articles/index.html (re)
  skip  output/2012/die-verwandlung/index.html
  create  \[0.\d+s\] output/2012/spam/index.html (re)
  update  \[0.\d+s\] output/rss/index.html (re)
  update  \[0.\d+s\] output/atom/index.html (re)
  update  \[0.\d+s\] output/index.html (re)
  skip  output/tag/die-verwandlung/index.html
  skip  output/tag/franz-kafka/index.html
  Blog compiled in 0.\d+s (re)

Now with templates. We have patched jinja2 template loader so we have a
recognition wether a template (including its parent templates) has changed.
*Note*, that this required BSD touch, too.

Let's randomly (chosen by fair dice) change some mtimes...

  $ /usr/bin/touch -A 05 layouts/articles.html
  $ /usr/bin/touch -A 42 layouts/entry.html
  $ /usr/bin/touch -A 23 layouts/rss.xml
  $ /usr/bin/touch -A 59 layouts/atom.xml

  $ acrylamid compile -C
  identical  output/articles/index.html
  identical  output/2012/die-verwandlung/index.html
  identical  output/2012/spam/index.html
  identical  output/rss/index.html
  identical  output/atom/index.html
  identical  output/index.html
  identical  output/tag/die-verwandlung/index.html
  identical  output/tag/franz-kafka/index.html
  Blog compiled in 0.\d+s (re)

  $ /usr/bin/touch -A 00 layouts/articles.html
  $ /usr/bin/touch -A 00 layouts/entry.html
  $ /usr/bin/touch -A 00 layouts/rss.xml
  $ /usr/bin/touch -A 00 layouts/atom.xml

  $ find output -exec /usr/bin/touch -A 00 {} \;

Now we touch a parent template and all inherited templates should change as, too.

  $ /usr/bin/touch -A 05 layouts/base.html

  $ acrylamid compile -C
  identical  output/articles/index.html
  identical  output/2012/die-verwandlung/index.html
  identical  output/2012/spam/index.html
  skip  output/rss/index.html
  skip  output/atom/index.html
  identical  output/index.html
  identical  output/tag/die-verwandlung/index.html
  identical  output/tag/franz-kafka/index.html
  Blog compiled in 0.\d+s (re)

  $ /usr/bin/touch -A 00 layouts/base.html
  $ find output -exec /usr/bin/touch -A 00 {} \;

And now vice versa: we touch completely different templates:

  $ /usr/bin/touch -A 05 layouts/rss.xml

  $ acrylamid compile -C
  skip  output/articles/index.html
  skip  output/2012/die-verwandlung/index.html
  skip  output/2012/spam/index.html
  identical  output/rss/index.html
  skip  output/atom/index.html
  skip  output/index.html
  skip  output/tag/die-verwandlung/index.html
  skip  output/tag/franz-kafka/index.html
  Blog compiled in 0.\d+s (re)

  $ /usr/bin/touch -A 00 layouts/rss.xml
  $ find output -exec /usr/bin/touch -A 00 {} \;

Now we change the base template and should see some updates:

  $ echo "Bar!" >> layouts/base.html
  $ /usr/bin/touch -A 01 layouts/base.html

  $ acrylamid compile -C
  update  \[0.\d+s\] output/articles/index.html (re)
  update  \[0.\d+s\] output/2012/die-verwandlung/index.html (re)
  update  [0.00s] output/2012/spam/index.html
  skip  output/rss/index.html
  skip  output/atom/index.html
  update  [0.00s] output/index.html
  update  [0.00s] output/tag/die-verwandlung/index.html
  update  [0.00s] output/tag/franz-kafka/index.html
  Blog compiled in 0.\d+s (re)

  $ /usr/bin/touch -A 00 layouts/base.html
  $ find output -exec /usr/bin/touch -A 00 {} \;

If we change a filter in conf.py we should see an update:

  $ sed -i "" -e s/\'hyphenate/\'nohyphenate/g conf.py
  $ acrylamid compile -C
  skip  output/articles/index.html
  update  \[0.\d+s\] output/2012/die-verwandlung/index.html (re)
  identical  output/2012/spam/index.html
  identical  output/rss/index.html
  identical  output/atom/index.html
  update  [0.00s] output/index.html
  update  [0.00s] output/tag/die-verwandlung/index.html
  update  [0.00s] output/tag/franz-kafka/index.html
  Blog compiled in 0.\d+s (re)

And we should clean up everything:

  $ rm -rf output/ layouts/ content/ .cache/ conf.py
