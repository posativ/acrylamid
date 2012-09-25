# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import os
import io
import time
import locale
import codecs
import tempfile
import subprocess
import shutil

from urlparse import urlsplit
from datetime import datetime
from collections import defaultdict
from os.path import join, dirname, getmtime, isfile

from acrylamid import log
from acrylamid.errors import AcrylamidException

from acrylamid import readers, filters, views, assets, utils, helpers
from acrylamid.lib import lazy
from acrylamid.core import cache
from acrylamid.helpers import event, safe


def initialize(conf, env):
    """Initializes Jinja2 environment, prepares locale and configure
    some minor things. Filter and View are inited with conf and env,
    a request dict is returned.
    """
    # initialize cache, optional to cache_dir
    cache.init(conf.get('cache_dir', None))

    # rewrite static directory
    assets.initialize(conf, env)

    # set up templating environment
    env.engine = utils.import_object(conf['engine'])()

    env.engine.init(conf['theme'], cache.cache_dir)
    env.engine.register('safeslug', helpers.safeslug)
    env.engine.register('tagify', lambda x: x)

    # try language set in LANG, if set correctly use it
    try:
        locale.setlocale(locale.LC_ALL, str(conf.get('lang', '')))
    except (locale.Error, TypeError):
        # try if LANG is an alias
        try:
            locale.setlocale(locale.LC_ALL, locale.locale_alias[str(conf.get('lang', '')).lower()])
        except (locale.Error, KeyError):
            # LANG is not an alias, so we use system's default
            try:
                locale.setlocale(locale.LC_ALL, '')
            except locale.Error:
                pass  # hope this makes Travis happy
            log.info('notice  your OS does not support %s, fallback to %s', conf.get('lang', ''),
                     locale.getlocale()[0])
    if locale.getlocale()[0] is not None:
        conf['lang'] = locale.getlocale()[0][:2]
    else:
        # getlocale() is (None, None) aka 'C'
        conf['lang'] = 'en'

    if 'www_root' not in conf:
        log.warn('no `www_root` specified, using localhost:8000')
        conf['www_root'] = 'http://localhost:8000/'

    # figure out timezone and set offset, more verbose for 2.6 compatibility
    td = (datetime.now() - datetime.utcnow())
    total_seconds = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
    offset = round(total_seconds / 3600.0)
    conf['tzinfo'] = readers.Timezone(offset)

    # determine http(s), host and path
    env['protocol'], env['netloc'], env['path'], x, y = urlsplit(conf['www_root'])

    # take off the trailing slash for www_root and path
    conf['www_root'] = conf['www_root'].rstrip('/')
    env['path'] = env['path'].rstrip('/')

    # check if encoding is available
    try:
        codecs.lookup(conf['encoding'])
    except LookupError:
        raise AcrylamidException('no such encoding available: %r' % conf['encoding'])

    # prepare, import and initialize filters and views
    if isinstance(conf['filters_dir'], basestring):
        conf['filters_dir'] = [conf['filters_dir'], ]

    if isinstance(conf['views_dir'], basestring):
        conf['views_dir'] = [conf['views_dir'], ]

    lazy.enable()
    filters.initialize(conf["filters_dir"], conf, env)
    lazy.disable()  # this has weird side effects with jinja2, so disabled after filters

    views.initialize(conf["views_dir"], conf, env)
    env['views'] = dict([(v.view, v) for v in views.get_views()])

    entryfmt, pagefmt = '/:year/:slug/', '/:slug/'
    for view in views.get_views():
        if view.view == 'entry':
            entryfmt = view.path
        if view.view == 'page':
            pagefmt = view.path

    conf.setdefault('entry_permalink', entryfmt)
    conf.setdefault('page_permalink', pagefmt)

    return {'conf': conf, 'env': env}


def compile(conf, env, force=False, **options):
    """The compilation process."""

    # time measurement
    ctime = time.time()

    # populate env and corrects some conf things
    request = initialize(conf, env)

    # load pages/entries and store them in env
    entrylist, pages = readers.load(conf)
    env.globals['entrylist'] = entrylist
    env.globals['pages'] = pages

    # XXX translations should be moved out of core
    env.globals['translations'] = translations = []

    if force:
        # acrylamid compile -f
        cache.clear()

    # here we store all found filter and their aliases
    ns = defaultdict(set)

    # get available filter list, something like with obj.get-function
    # list = [<class head_offset.Headoffset at 0x1014882c0>, <class html.HTML at 0x101488328>,...]
    aflist = filters.get_filters()

    # ... and get all configured views
    _views = views.get_views()

    # filters found in all entries, views and conf.py
    found = sum((x.filters for x in entrylist+pages+_views), []) + request['conf']['filters']

    for val in found:
        # first we for `no` and get the function name and arguments
        f = val[2:] if val.startswith('no') else val
        fname, fargs = f.split('+')[:1][0], f.split('+')[1:]

        try:
            # initialize the filter with its function name and arguments
            fx = aflist[fname](conf, env, val, *fargs)
            if val.startswith('no'):
                fx = filters.disable(fx)
        except ValueError:
            try:
                fx = aflist[val.split('+')[:1][0]](conf, env, val, *fargs)
            except ValueError:
                raise AcrylamidException('no such filter: %s' % val)

        ns[fx].add(val)

    for entry in entrylist + pages:
        for v in _views:

            # a list that sorts out conflicting and duplicated filters
            flst = filters.FilterList()

            # filters found in this specific entry plus views and conf.py
            found = entry.filters + v.filters + request['conf']['filters']

            for fn in found:
                fx, _ = next((k for k in ns.iteritems() if fn in k[1]))
                if fx not in flst:
                    flst.append(fx)

            # sort them ascending because we will pop within filters.add
            entry.filters.add(sorted(flst, key=lambda k: (-k.priority, k.name)),
                              context=v)

    # lets offer a last break to populate tags or so
    # XXX this API component needs a review
    for v in _views:
        env = v.context(env, {'entrylist': entrylist, 'pages': pages,
                              'translations': translations})

    # now teh real thing!
    for v in _views:

        # XXX the entry should automatically determine its caller (using
        # some sys magic to recursively check wether the calling class is
        # derieved from `View`.)
        for entry in entrylist + pages + translations:
            entry.context = v

        request['pages'], request['translations'] = pages, translations
        request['entrylist'] = filter(v.condition, entrylist)
        tt = time.time()

        for buf, path in v.generate(request):
            helpers.mkfile(buf, path, time.time()-tt, **options)
            tt = time.time()

    # copy modified/missing assets to output
    assets.compile(conf, env)

    # remove abandoned cache files
    cache.shutdown()

    # print a short summary
    log.info('%i new, %i updated, %i skipped [%.2fs]', event.count('create'),
             event.count('update'), event.count('identical') + event.count('skip'),
             time.time() - ctime)


def autocompile(ws, conf, env, **options):
    """Subcommand: autocompile -- automatically re-compiles when something in
    content-dir has changed and parallel serving files."""

    CONF_PY = './conf.py'

    mtime = -1
    cmtime = getmtime(CONF_PY)

    while True:
        ntime = max(
            max(getmtime(e) for e in readers.filelist(conf['content_dir'], conf.get('content_ignore', [])) if utils.istext(e)),
            max(getmtime(p) for p in readers.filelist(conf['theme'], conf.get('theme_ignore', []))))
        if mtime != ntime:
            try:
                compile(conf, env, **options)
            except AcrylamidException as e:
                log.fatal(e.args[0])
                pass
            event.reset()
            mtime = ntime

        if cmtime != getmtime(CONF_PY):
            log.info(' * Restarting due to change in %s' % (CONF_PY))
            # Kill the webserver
            ws.shutdown()
            # Force compilation since no template was changed
            argv = sys.argv if options['force'] else sys.argv[:] + ["--force"]
            # Restart acrylamid
            os.execvp(sys.argv[0], argv)

        time.sleep(1)


def new(conf, env, title, prompt=True):
    """Subcommand: new -- create a new blog entry the easy way.  Either run
    ``acrylamid new My fresh new Entry`` or interactively via ``acrylamid new``
    and the file will be created using the preferred permalink format."""

    # we need the actual defaults values
    initialize(conf, env)

    fd, tmp = tempfile.mkstemp(suffix='.txt', dir='.cache/')
    editor = os.getenv('VISUAL') if os.getenv('VISUAL') else os.getenv('EDITOR')

    if not title:
        title = raw_input("Entry's title: ")
    title = safe(title).decode('utf-8')

    with io.open(fd, 'w') as f:
        f.write(u'---\n')
        f.write(u'title: %s\n' % title)
        f.write(u'date: %s\n' % datetime.now().strftime(conf['date_format']))
        f.write(u'---\n\n')

    entry = readers.Entry(tmp, conf)
    p = join(conf['content_dir'], dirname(entry.permalink)[1:])

    try:
        os.makedirs(p.rsplit('/', 1)[0])
    except OSError:
        pass

    filepath = p + '.txt'
    if isfile(filepath):
        raise AcrylamidException('Entry already exists %r' % filepath)
    shutil.move(tmp, filepath)
    event.create(filepath)

    if datetime.now().hour == 23 and datetime.now().minute > 45:
        log.info("notice  consider editing entry.date-day after you passed mignight!")

    if not prompt:
        return

    try:
        if editor:
            retcode = subprocess.call([editor, filepath])
        elif sys.platform == 'darwin':
            retcode = subprocess.call(['open', filepath])
        else:
            retcode = subprocess.call(['xdg-open', filepath])
    except OSError:
        raise AcrylamidException('Could not launch an editor')

    # XXX process detaches... m(
    if retcode < 0:
        raise AcrylamidException('Child was terminated by signal %i' % -retcode)

    if os.stat(filepath)[6] == 0:
        raise AcrylamidException('File is empty!')


__all__ = ["compile", "autocompile", "new"]
