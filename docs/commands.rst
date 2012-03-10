Commands
========

init
----

new
---

compile
-------

autocompile
-----------

view
----

import
------

deploy
------

With ``acrylamid deploy TASK`` you can run single commands, e.g. push just generated
content to your server. Write new tasks into the DEPLOYMENT dict inside your ``conf.py``
like this:

::

	DEPLOYMENT = {
		"ls": "ls",
		"echo": "echo %s",
		"blog": "rsync -av --delete %s www@server:~/blog.example.org/"
	}

Now, you can invoke *ls*, *echo* and *blog* as TASK. This example config shows you all
possibilities to create your scripts. A plain ``ls`` is internally extended to ``ls %s``
where ``%s`` is substituted by the current ``OUTPUT_DIR``-variable (you can see this in
the second task). The third task is simple command to deploy your blog directly to your
server -- notice the substitution variable can be anywhere.

::
	$> acrylamid deploy ls
		2009
		2010
		...
		tag

	$> acrylamid deploy echo
    	output/

	$> acrylamid deploy blog
	    building file list ... done

	    sent 19701 bytes  received 20 bytes  7888.40 bytes/sec
	    total size is 13017005  speedup is 660.06

