# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import time
import locale
import codecs

from os.path import getmtime
from jinja2 import Environment, FileSystemBytecodeCache

from acrylamid import filters, views, log
from acrylamid.utils import cache, ExtendedFileSystemLoader
from acrylamid.errors import AcrylamidException

from acrylamid.core import handle as prepare, filelist
from acrylamid.filters import get_filters, FilterList
from acrylamid.views import get_views


def initialize(conf, env):
    """Initializes Jinja2 environment, prepares locale and configure
    some minor things. Filter and View are inited with conf and env,
    a request dict is returned.
    """
    # set up templating environment
    env['tt_env'] = Environment(loader=ExtendedFileSystemLoader(conf['layout_dir']),
                                bytecode_cache=FileSystemBytecodeCache('.cache/'))
    env['tt_env'].filters.update({'safeslug': False, 'tagify': False})

    # initialize the locale, will silently fail if locale is not
    # available and uses system's locale
    try:
        locale.setlocale(locale.LC_ALL, conf.get('lang', ''))
    except (locale.Error, TypeError):
        # invalid locale
        locale.setlocale(locale.LC_ALL, '')
        log.warn("unsupported locale '%s', set to '%s'", conf['lang'], locale.getlocale()[0])
    conf['lang'] = locale.getlocale()

    if 'www_root' not in conf and 'website' in conf:
        conf['www_root'] = conf['website']
    elif 'www_root' not in conf:
        log.warn('no `www_root` specified, using localhost:8000')
        conf['www_root'] = 'http://localhost:8000/'

    if 'website' not in conf:
        conf['website'] = conf['www_root']

    env['protocol'] = conf['www_root'][0:conf['www_root'].find('://')]
    # take off the trailing slash for base_url
    if conf['www_root'].endswith("/"):
        conf['www_root'] = conf['www_root'][:-1]

    # check encoding is available
    try:
        codecs.lookup(conf['encoding'])
    except LookupError:
        raise AcrylamidException('no such encoding available: %r' % conf['encoding'])

    # XXX implement _optional_ config argments like cache_dir
    # init to conf['cache_dir'] (defaults to '.cache/')
    cache.init()

    # import and initialize plugins
    filters.initialize(conf.get("filters_dir", []), conf, env,
                          exclude=conf.get("filters_ignore", []),
                          include=conf.get("filters_include", []))
    views.initialize(conf.get("views_dir", []), conf, env)

    return {'conf': conf, 'env': env}


def compile(conf, env, force=False, **options):

    request = initialize(conf, env)
    request = prepare(request)

    if force:
        cache.clear()

    filtersdict = get_filters()
    _views = get_views()

    for v in _views:
        log.debug(v)
        for entry in request['entrylist']:
            if not v.__filters__:
                break

            log.debug(entry.filename)
            entryfilters = entry.filters
            if isinstance(entryfilters, basestring):
                entryfilters = [entryfilters]
            viewsfilters = request['conf']['filters'] + v.filters

            _filters = FilterList()
            for f in entryfilters + viewsfilters:
                x, y = f.split('+')[:1][0], f.split('+')[1:]
                if filtersdict[x] not in _filters:
                    _filters.append((x, filtersdict[x], y))

            entry.lazy_eval = _filters

        v(request, **options)


def autocompile(conf, env, **options):

    f = lambda l: dict([(p, getmtime(p)) for p in l])

    # first run to have everything up-to-date
    files = f(filelist(conf))
    try:
        compile(conf, env, **options)
    except AcrylamidException as e:
        log.fatal(e.message)

    while True:
        if files != f(filelist(conf)):
            # something changed
            try:
                compile(conf, env, **options)
            except AcrylamidException as e:
                log.fatal(e.message)
                pass
            files = f(filelist(conf))
        time.sleep(1)


__all__ = ["compile", "autocompile"]
