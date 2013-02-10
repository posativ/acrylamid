Hooks
=====

Although Acrylamid supports many libraries and external tools, it is rather
limited due the simple configration syntax. To extend the compilation process,
Acrylamid allows you to hook into its events (create, update and so on). This
allows you to do something witht the generated files, for example generating
image thumbnails on-the-fly and/or compress the produced HTML.

There are two different types of hooks. The simple hook "listens" on the
create and update events and simply calls your function with the namespace [#1] of
the event and the path, in this order. Whereas the advanced hook hooks into
all available event types but requires a path translation function to
automatically determine whether the callback should be executed or not.

Instead of writing callbacks in Python, you can also supply a shell command
with one (simple) or two (advanced) arguments. The namespace is not available
within shell commands.

.. code-block:: python

    from os.path import join, dirname, basename

    HOOKS = {
        # stdout is written to a temporary file and then moved to %1
        '.+\.html': 'htmlcompressor %1',

        # with path translation, you have src and dest (%1 and %2)
        '.+\.jpg' : (
            'convert -thumbnail 150x150^ -gravity center -extent 150x150 %1 %2',
            lambda p: lambda p: join(dirname(p), 'thumbs/', basename(p))
        )
    }

.. [#] the namespace indicates the originator of the event. It can be on of the
       following: archive, articles, entry, feeds, index, sitemap, tag, assets
       or None.

Simple Hook
-----------

The simplest hook is just a function that receives original namespace and
path from the :class:`event` utility. You have more freedom, but it may have
an impact to compilation speed if not implemented correctly.

.. code-block:: python

    def doit(namespace, path):

        # namespace -> assets, entry and so on.
        # path -> output/path/to/file
        pass

    HOOKS = {
        '.+\.html': doit
    }

Advanced Hook
-------------

An advanced hook is less readable than the naive, but tightlier integrated into
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
        except AcrylamidException as e:
           log.warn(e.args[0])
        except OSError:
            pass
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

.. _imagemagick's: http://www.imagemagick.org/
