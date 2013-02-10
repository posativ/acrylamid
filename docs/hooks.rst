Hooks
=====

Although Acrylamid supports many libraries and external tools, it is rather
limited due the simple configration. With the new hook feature, you can write
your own functions to do something with the generated files, for example
generating image thumbnails on-the-fly or compress the produced HTML.

Naive Hook
----------

The simplest hook is just a function that receives original namespace and
path from the :class:`event` utility. You have more freedom, but it may have
an impact to compilation speed if not implemented correctly.

.. code-block:: python

    def minify(ns, path):
        pass

    HOOKS = {
        '.+\.html': minify,
    }

Complex Hook
------------

A complex hook is less readable than the naive, but tightlier integrated into
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
