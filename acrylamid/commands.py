# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import sys
import os
import time
import shutil
import locale
import codecs

from urlparse import urlsplit
from datetime import datetime
from itertools import chain
from collections import defaultdict
from os.path import getmtime

from acrylamid import log
from acrylamid.errors import AcrylamidException

from acrylamid import readers, filters, views, assets, refs, helpers, __version__
from acrylamid.lib import lazy, history
from acrylamid.core import cache
from acrylamid.utils import hash, istext, HashableList, import_object
from acrylamid.helpers import event


def initialize(conf, env):
    """Initializes Jinja2 environment, prepares locale and configure
    some minor things. Filter and View are inited with conf and env,
    a data dict is returned.
    """
    # initialize cache, optional to cache_dir
    cache.init(conf.get('cache_dir'))

    env['version'] = type('Version', (str, ), dict(zip(
        ['major', 'minor', 'patch'], (int(x) for x in __version__.split('.'))
    )))(__version__)

    # crawl through CHANGES.md and stop on breaking changes
    if history.breaks(env, cache.emptyrun):
        print "Detected version upgrade that might break your configuration. Run"
        print "Acrylamid a second time to get rid of this message and premature exit."
        raise SystemExit

    # rewrite static directory
    assets.initialize(conf, env)

    # set up templating environment
    env.engine = import_object(conf['engine'])()

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
    env.views = views.Views(view for view in views.get_views())

    entryfmt, pagefmt = '/:year/:slug/', '/:slug/'
    for view in views.get_views():
        if view.name == 'entry':
            entryfmt = view.path
        if view.name == 'page':
            pagefmt = view.path

    conf.setdefault('entry_permalink', entryfmt)
    conf.setdefault('page_permalink', pagefmt)

    return {'conf': conf, 'env': env}


def compile(conf, env, force=False, **options):
    """The compilation process."""

    if force:
        cache.clear(conf.get('cache_dir'))

    # time measurement
    ctime = time.time()

    # populate env and corrects some conf things
    data = initialize(conf, env)

    # load pages/entries and store them in env
    rv = dict(zip(['entrylist', 'pages', 'translations', 'drafts'],
        map(HashableList, readers.load(conf))))

    entrylist, pages = rv['entrylist'], rv['pages']
    translations, drafts = rv['translations'], rv['drafts']

    # load references
    refs.load(entrylist, pages, translations, drafts)

    data.update(rv)
    env.globals.update(rv)

    # here we store all found filter and their aliases
    ns = defaultdict(set)

    # get available filter list, something like with obj.get-function
    # list = [<class head_offset.Headoffset at 0x1014882c0>, <class html.HTML at 0x101488328>,...]
    aflist = filters.get_filters()

    # ... and get all configured views
    _views = views.get_views()

    # filters found in all entries, views and conf.py (skip translations, has no items)
    found = sum((x.filters for x in chain(entrylist, pages, drafts, _views, [conf])), [])

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

    for entry in chain(entrylist, pages, drafts):
        for v in _views:

            # a list that sorts out conflicting and duplicated filters
            flst = filters.FilterList()

            # filters found in this specific entry plus views and conf.py
            found = entry.filters + v.filters + data['conf']['filters']

            for fn in found:
                fx, _ = next((k for k in ns.iteritems() if fn in k[1]))
                if fx not in flst:
                    flst.append(fx)

            # sort them ascending because we will pop within filters.add
            entry.filters.add(sorted(flst, key=lambda k: (-k.priority, k.name)),
                              context=v)

    # lets offer a last break to populate tags and such
    for v in _views:
        env = v.context(conf, env, data)

    # now teh real thing!
    for v in _views:

        for entry in chain(entrylist, pages, translations, drafts):
            entry.context = v

        for var in 'entrylist', 'pages', 'translations', 'drafts':
            data[var] = HashableList(filter(v.condition, locals()[var])) \
                if v.condition else locals()[var]

        tt = time.time()
        for buf, path in v.generate(conf, env, data):
            try:
                helpers.mkfile(buf, path, time.time()-tt, **options)
            finally:
                buf.close()
            tt = time.time()

    # copy modified/missing assets to output
    assets.compile(conf, env)

    # save conf/environment hash and new/changed/unchanged references
    helpers.memoize('Configuration', hash(conf))
    helpers.memoize('Environment', hash(env))
    refs.save()

    # remove abandoned cache files
    cache.shutdown()

    # print a short summary
    log.info('%i new, %i updated, %i skipped [%.2fs]', event.count('create'),
             event.count('update'), event.count('identical') + event.count('skip'),
             time.time() - ctime)


def autocompile(ws, conf, env, **options):
    """Subcommand: autocompile -- automatically re-compiles when something in
    content-dir has changed and parallel serving files."""

    mtime = -1
    cmtime = getmtime('conf.py')

    while True:

        ws.wait = True
        ntime = max(
            max(getmtime(e) for e in readers.filelist(
                conf['content_dir'], conf.get('content_ignore', [])) if istext(e)),
            max(getmtime(p) for p in readers.filelist(
                conf['theme'], conf.get('theme_ignore', []))))
        if mtime != ntime:
            try:
                compile(conf, env, **options)
            except (SystemExit, KeyboardInterrupt) as e:
                raise e
            except Exception as e:
                log.fatal(e.args[0])
            event.reset()
            mtime = ntime
        ws.wait = False

        if cmtime != getmtime('conf.py'):
            log.info(' * Restarting due to change in conf.py')
            # Kill the webserver
            ws.shutdown()
            # Restart acrylamid
            os.execvp(sys.argv[0], sys.argv)

        time.sleep(1)


__all__ = ["compile", "autocompile"]
