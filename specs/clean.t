XXX: check wether clean really removes files
Test `acrylamid clean`.

  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ LANG="en_US.UTF-8" && unset LC_ALL && unset LANGUAGE
  $ acrylamid init -q $TMPDIR
  $ cd $TMPDIR
  $ acrylamid compile -q

Does `acrylamid clean` work?

  $ acrylamid clean -C
  $ rm content/sample-entry.txt

  $ acrylamid clean -nC | sort
  remove  output/2012/die-verwandlung/index.html
  remove  output/index.html
  remove  output/tag/die-verwandlung/index.html
  remove  output/tag/franz-kafka/index.html

  $ acrylamid clean -C | sort
  remove  output/2012/die-verwandlung/index.html
  remove  output/index.html
  remove  output/tag/die-verwandlung/index.html
  remove  output/tag/franz-kafka/index.html

  $ acrylamid clean -fC | sort
  remove  output/articles/index.html
  remove  output/atom/index.html
  remove  output/rss/index.html
  remove  output/sitemap.xml

And we should clean up everything:

  $ rm -rf output/ theme/ content/ .cache/ conf.py
