# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import sys
import os
import time
import locale
import codecs
import tempfile
import shlex

from os.path import join, dirname, getmtime, isfile
from urlparse import urlsplit
from datetime import datetime
from jinja2 import Environment, FileSystemBytecodeCache

from acrylamid import filters, views, log, utils
from acrylamid.lib.importer import fetch, parse, build
from acrylamid.errors import AcrylamidException
from acrylamid.utils import cache, ExtendedFileSystemLoader, FileEntry, event, escapes, \
                            system, filelist

from acrylamid.filters import FilterList


def initialize(conf, env):
    """Initializes Jinja2 environment, prepares locale and configure
    some minor things. Filter and View are inited with conf and env,
    a request dict is returned.
    """
    # set up templating environment
    env['tt_env'] = Environment(loader=ExtendedFileSystemLoader(conf['layout_dir']),
                                bytecode_cache=FileSystemBytecodeCache('.cache/'))
    env['tt_env'].filters.update({'safeslug': lambda x: x, 'tagify': lambda x: x})

    # initialize the locale, will silently fail if locale is not
    # available and uses system's locale
    try:
        locale.setlocale(locale.LC_ALL, conf.get('lang', ''))
    except (locale.Error, TypeError):
        # invalid locale
        locale.setlocale(locale.LC_ALL, '')
        log.warn("unsupported locale '%s', set to '%s'", conf['lang'], locale.getlocale()[0])
    conf['lang'] = locale.getlocale()

    if 'www_root' not in conf:
        log.warn('no `www_root` specified, using localhost:8000')
        conf['www_root'] = 'http://localhost:8000/'

    env['protocol'], env['netloc'], env['path'], x, y = urlsplit(conf['www_root'])

    # take off the trailing slash for www_root and path
    conf['www_root'] = conf['www_root'].rstrip('/')
    env['path'] = env['path'].rstrip('/')

    # check if encoding is available
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
    env['views'] = [v['view'] for k, v in conf['views'].iteritems()]

    return {'conf': conf, 'env': env}


def compile(conf, env, force=False, **options):

    # time measurement
    ctime = time.time()

    # populate env and corrects some conf things
    request = initialize(conf, env)

    if force:
        # acrylamid compile -f
        cache.clear()

    # list of FileEntry-objects reverse sorted by date.
    entrylist = sorted([FileEntry(e, conf) for e in filelist(conf['entries_dir'],
                                                             conf.get('entries_ignore', []))],
                       key=lambda k: k.date, reverse=True)

    # here we store all possible filter configurations
    ns = set()

    # get available filter list, something like with obj.get-function
    # list = [<class head_offset.Headoffset at 0x1014882c0>, <class html.HTML at 0x101488328>,...]
    aflist = filters.get_filters()


    # ... and get all configured views
    _views = views.get_views()

    # filters found in all entries, views and conf.py
    found = sum((x.filters for x in entrylist+_views), []) + request['conf']['filters']

    for val in found:
        # first we for `no` and get the function name and arguments
        f = val[2:] if val.startswith('no') else val
        fname, fargs = f.split('+')[:1][0], f.split('+')[1:]

        try:
            # initialize the filter with its function name and arguments
            fx = aflist[fname](val, *fargs)
            if val.startswith('no'):
                fx.transform = lambda x, y, *z: x
                fx.__hash__ = lambda : 0
        except ValueError:
            try:
                fx = aflist[val.split('+')[:1][0]](val, *fargs)
            except ValueError:
                raise AcrylamidException('no such filter: %s' % val)

        ns.add(fx)

    for entry in entrylist:
        for v in _views:

            # a list that sorts out conflicting and duplicated filters
            flst = FilterList()

            # filters found in this specific entry plus views and conf.py
            found = entry.filters + v.filters + request['conf']['filters']

            for fn in found:
                fx = filter(lambda k: fn == k.name, ns)[0]
                if fx not in flst:
                    flst.append(fx)

            # sort them ascending because we will pop within filters.add
            entry.filters.add(sorted(flst, key=lambda k: (-k.__priority__, k.name)),
                              context=v.__class__.__name__)

    # lets offer a last break to populate tags or so
    # XXX this API component needs a review
    for v in _views:
        env = v.context(env, {'entrylist': filter(v.condition, entrylist)})

    # now teh real thing!
    for v in _views:

        # XXX the entry should automatically determine its caller (using
        # some sys magic to recursively check wether the calling class is
        # derieved from `View`.)
        for entry in entrylist:
            entry.context = v.__class__.__name__

        request['entrylist'] = filter(v.condition, entrylist)
        tt = time.time()

        for res in v.generate(request):
            try:
                html, path, message = res
            except ValueError:
                # also allow two items yielding for simplicity
                html, path = res
                message = path.replace(conf['output_dir'], '')

            utils.mkfile(html, path, message, time.time()-tt, **options)
            tt = time.time()

    log.info('Blog compiled in %.2fs' % (time.time() - ctime))


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


def new(conf, env, title):
    """Subcommand: new -- create a new blog entry the easy way.  Either run
    ``acrylamid new My fresh new Entry`` or interactively via ``acrylamid new``
    and the file will be created using the preferred permalink format."""

    fd, tmp = tempfile.mkstemp(suffix='.txt', dir='.cache/')
    editor = os.getenv('VISUAL') if os.getenv('VISUAL') else os.getenv('EDITOR')

    if not title:
        title = raw_input("Entry's title: ")
    title = escapes(title)

    with os.fdopen(fd, 'wb') as f:
        f.write('---\n')
        f.write('title: %s\n' % title)
        f.write('date: %s\n' % datetime.now().strftime(conf['date_format']))
        f.write('---\n\n')

    entry = FileEntry(tmp, conf)
    p = join(conf['entries_dir'], dirname(entry.permalink)[1:])

    try:
        os.makedirs(p.rsplit('/', 1)[0])
    except OSError:
        pass

    filepath = p + '.txt'
    if isfile(filepath):
        raise AcrylamidException('Entry already exists %r' % filepath)
    os.rename(tmp, filepath)
    event.create(title, filepath)

    try:
        if editor:
            retcode = os.system(editor + ' ' + filepath)
        elif sys.platform == 'darwin':
            retcode = os.system('open ' + filepath)
        else:
            retcode = os.system('xdg-open ' + filepath)
    except OSError:
        raise AcrylamidException('Could not launch an editor')

    # XXX process detaches... m(
    if retcode < 0:
        raise AcrylamidException('Child was terminated by signal %i' % -retcode)

    if os.stat(filepath)[6] == 0:
        raise AcrylamidException('File is empty!')


def importer(conf, env, url, **options):
    """Subcommand: import -- import entries and settings from an existing RSS/Atom
    feed.  ``acrylamid import http://example.com/feed/`` should do the job.

    If ``pandoc`` or ``html2text`` are available, first pandoc and second html2text
    are used to convert HTML back to Markdown-compatible text.  If you like reST more
    than Markdown, specify ``--format=rst`` and be sure you have either ``pandoc`` or
    ``html2rest`` installed on your system.

    If you don't like any reconversion, simply use ``--format=html``."""

    content = fetch(url, auth=options.get('auth', None))
    defaults, items = parse(content)
    build(conf, env, defaults, items, fmt=options['import_fmt'], keep=options['keep_links'])


def deploy(conf, env, task, *args):
    """Subcommand: deploy -- run the shell command specified in DEPLOYMENT[task] using
    Popen. Use ``%s`` inside your command to let acrylamid substitute ``%s`` with the
    output path, if no ``%s`` is set, the path is appended  as first argument. Every
    argument after ``acrylamid deploy task ARG1 ARG2``."""

    cmd = shlex.split(conf.get('deployment', {}).get(task, None))
    if not cmd:
        raise AcrylamidException('no tasks named %r in conf.py' % task)

    try:
        cmd[cmd.index('%s')] = conf['output_dir']
    except ValueError:
        cmd.append(conf['output_dir'])

    # apply ARG1 ARG2 ... and -v --long-args to the command, e.g.:
    # $> acrylamid deploy task arg1 -- -b --foo
    cmd.extend(args)

    try:
        result = system(cmd)
        print '\n'.join('    '+line for line in result.strip().split('\n'))
    except OSError as e:
        raise AcrylamidException(e.message)


__all__ = ["compile", "autocompile", "new"]
