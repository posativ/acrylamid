Hooks
=====

Although Acrylamid supports many libraries and external tools, it is rather
limited due its simple configuration syntax. To extend the compilation process,
you can to hook into internal events (create, update etc.) or execute code
before or after the compilation process. The former allows you to do something
with the generated files, for example generating image thumbnails on-the-fly
and/or compress the produced HTML, while the latter might useful for a general
pre-processing or post-processing (think of macros and/or sprites generation).

By default, all hooks are executed in parallel (not limited by the GIL if you
run external processes/commands), you can disable this behavior by setting
``HOOKS_MT`` to ``False``.

on-the-fly Hooks
----------------

There are two different types of hooks. The simple hook "listens" on the create
and update events and simply calls your function with the name space [#1]_ of the
event and the path, in this order. Whereas the advanced hook hooks into all
available event types but requires a path translation function to automatically
determine whether the callback should be executed or not.

Instead of writing callbacks in Python, you can also supply a shell command
with one (simple) or two (advanced) arguments. The name space is not available
within shell commands.

.. [#] the name space indicates the originator of the event. It can be on of the
       following: archive, articles, entry, feeds, index, sitemap, tag, assets
       or None.

Simple Hook
***********

The simplest hook is just a function that receives the original name space and
path from the :class:`event` utility. You have more freedom, but it may have
an impact to compilation speed if not implemented correctly.

.. code-block:: python

    def doit(namespace, path):
        """"Do something. Take care of skipping unmodified content.

        :param namespace: assets, entry and so on
        :param path: output/path/to/file"""

        pass

    HOOKS = {
        '.+': doit,
        '.+\.html': 'htmlcompressor %1',  # compress HTML (duh ;-)
                                          # %1 is the destination path
    }

Advanced Hook
*************

An advanced hook is less readable than the naive, but tighter integrated into
Acrylamid's modification detection mechanisms. You need to provide your
function as in the naive hook and additionally a path translation function.
The path translation helps Acrylamid to determine whether it is necessary to
execute the hook or not.

.. code-block:: python

    from acrylamid import log
    from acrylamid.helpers import system, AcrylamidException
    from os import makedirs
    from os.path import exists, dirname, basename, join

    def mkthumb(ns, src, dest):
        if not exists(dirname(dest)):
            makedirs(dirname(dest))
        try:
            system(['convert',
                    '-define', 'jpeg:size=320x320',
                    '-thumbnail', '160x160^',
                    '-gravity', 'center',
                    '-extent', '160x160',
                    src, dest])
        except (AcrylamidException, OSError):
           log.exception("uncaught exception for %s", src)
        else:
            log.info('create  thumbnail  %s', dest)

    HOOKS = {
        'images/.+\.(jpg|png)': (
            mkthumb,
            lambda p: join(dirname(p), 'thumbs/', basename(p))
        ),
    }

The hook above will create thumbnails on-the-fly using `Imagemagick's`_
``convert`` and saves these thumbnails to a dedicated `thumbs/` folder.

You can achieve the very same with the following:

.. code-block:: python

    from os.path import join, dirname, basename

    HOOKS = {
        '.+\.jpg' : (
            # %1 is the original file path, %2 the destination path
            'convert -thumbnail 150x150^ -gravity center -extent 150x150 %1 %2',

            # path translation
            lambda p: join(dirname(p), 'thumbs/', basename(p))
        )

.. _imagemagick's: http://www.imagemagick.org/


Pre and Post Hooks
------------------

If you do not operate on file names, you can use custom pre and post hooks (if
you need other hook "types", open an issue please). Hooks are stored at the
``hooks/`` directory next to your :doc:`conf.py` (``HOOKS_DIR`` allows you to
override the location).

You can write all your hooks in a single file or spread them across different
files. The file names are irrelevant. Inside your python files, you use the
``hooks.pre`` and ``hooks.post`` decorator to assign your functions to be run
before (pre) or after (post) compilation.

.. code-block:: python

    # cat hooks/foo.py
    from acrylamid import hooks

    @hooks.pre
    def baz(conf, env):
        print "Hello, "


    @hooks.post
    def bar(conf, env):
        print "World!"


Beside this rather dumb example, think of some code that generates a sprites
image from thumbnails located in a dedicated *thumbs/* directory.

.. code-block:: python

    # cat hooks/sprites.py

    import os
    from os.path import join, getmtime

    from acrylamid import log, hooks

    from acrylamid.errors import AcrylamidException
    from acrylamid.helpers import system, chdir


    @hooks.post
    def sprites(conf, env):

        for directory, _, files in os.walk(conf['output_dir']):
            if not directory.endswith('thumbs'):
                continue

            try:
                modified = getmtime(join(directory, 'sprites.png'))
                files.remove('sprites.png')
            except OSError:
                modified = 0.0

            if any(filter(lambda p: getmtime(join(directory, p)) <= modified, files)):
                continue

            with chdir(directory):
                system('convert * -append sprites.png', shell=True)
                log.info('create  %s', join(directory, 'sprites.png'))

Simple, isn't it? Just be careful, when you use ``event.create`` to log the
newly generated files -- this will trigger the thumbnail hook again!
