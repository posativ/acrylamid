XXX: check wether clean really removes files
Test `acrylamid clean`.

  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ LANG="de_DE.UTF-8" && unset LC_ALL && unset LANGUAGE
  $ acrylamid init -q $TMPDIR
  $ cd $TMPDIR
  $ acrylamid compile -q

Does `acrylamid clean` work?

  $ acrylamid clean -C
  $ rm content/sample-entry.txt

  $ acrylamid clean -nC
  removed  output/index.html
  removed  output/2012/die-verwandlung/index.html
  removed  output/tag/die-verwandlung/index.html
  removed  output/tag/franz-kafka/index.html

  $ acrylamid clean -C
  removed  output/index.html
  removed  output/2012/die-verwandlung/index.html
  removed  output/tag/die-verwandlung/index.html
  removed  output/tag/franz-kafka/index.html

  $ acrylamid clean -fC
  removed  output/articles/index.html
  removed  output/atom/index.html
  removed  output/rss/index.html

And we should clean up everything:

  $ rm -rf output/ layouts/ content/ .cache/ conf.py
