Testing `acrylamid init` in different ways:

  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ LANG="en_US.UTF-8" && unset LC_ALL && unset LANGUAGE
  $ cd $TMPDIR

Setup in current directory?

  $ acrylamid init -C .
  create  ./content/sample-entry.txt
  create  ./theme/base.html
  create  ./theme/main.html
  create  ./theme/entry.html
  create  ./theme/articles.html
  create  ./theme/atom.xml
  create  ./theme/rss.xml
  create  ./theme/style.css
  create  ./conf.py
  Created your fresh new blog at '.'. Enjoy!

Now set up in a given directory:

  $ rm -rf ./theme ./content conf.py
  $ acrylamid init -C foo
  create  foo/content/sample-entry.txt
  create  foo/theme/base.html
  create  foo/theme/main.html
  create  foo/theme/entry.html
  create  foo/theme/articles.html
  create  foo/theme/atom.xml
  create  foo/theme/rss.xml
  create  foo/theme/style.css
  create  foo/conf.py
  Created your fresh new blog at 'foo'. Enjoy!

Can we find all needed files?

  $ cd foo/
  $ [ -e conf.py ]
  $ [ -e content/sample-entry.txt ]

  $ [ -e theme/base.html ]
  $ [ -e theme/main.html ]
  $ [ -e theme/entry.html ]
  $ [ -e theme/articles.html ]
  $ [ -e theme/rss.xml ]
  $ [ -e theme/atom.xml ]
  $ [ -e theme/style.css ]

Can we restore a stylesheet?

  $ rm theme/style.css
  $ acrylamid init -C .
  create  ./theme/style.css

And we should clean up everything:

  $ rm -rf output/ theme/ content/ .cache/ conf.py
