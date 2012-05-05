Testing `acrylamid init` in different ways:

  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ LANG="de_DE.UTF-8" && unset LC_ALL && unset LANGUAGE
  $ cd $TMPDIR

Setup in current directory?

  $ acrylamid init -C .
  create  ./output/style.css
  create  ./layouts/base.html
  create  ./layouts/main.html
  create  ./layouts/entry.html
  create  ./layouts/articles.html
  create  ./layouts/rss.xml
  create  ./layouts/atom.xml
  create  ./content/sample-entry.txt
  Created your fresh new blog at '.'. Enjoy!

Now set up in a given directory:

  $ rm -rf ./output ./layouts ./content conf.py
  $ acrylamid init -C foo
  create  foo/output/style.css
  create  foo/layouts/base.html
  create  foo/layouts/main.html
  create  foo/layouts/entry.html
  create  foo/layouts/articles.html
  create  foo/layouts/rss.xml
  create  foo/layouts/atom.xml
  create  foo/content/sample-entry.txt
  Created your fresh new blog at 'foo'. Enjoy!

Can we find all needed files?

  $ cd foo/
  $ [ -e conf.py ]
  $ [ -e content/sample-entry.txt ]

  $ [ -e layouts/base.html ]
  $ [ -e layouts/main.html ]
  $ [ -e layouts/entry.html ]
  $ [ -e layouts/articles.html ]
  $ [ -e layouts/rss.xml ]
  $ [ -e layouts/atom.xml ]

  $ [ -e output/style.css ]

Can we restore a stylesheet?

  $ rm output/style.css
  $ acrylamid init -fC output/style.css
  create output/style.css

An existing file?

  $ acrylamid init -fC conf.py
  re-initialized conf.py

And we should clean up everything:

  $ rm -rf output/ layouts/ content/ .cache/ conf.py
