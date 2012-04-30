# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import os
import time
import locale
import codecs
import tempfile
import subprocess

from os.path import join, dirname, getmtime, isfile
from fnmatch import fnmatch
from urlparse import urlsplit
from datetime import datetime
from jinja2 import Environment, FileSystemBytecodeCache

from acrylamid import filters, views, log, utils
from acrylamid.lib.importer import fetch, parse, build
from acrylamid.errors import AcrylamidException
from acrylamid.utils import cache, ExtendedFileSystemLoader, FileEntry, event, escape, \
                            system, filelist

from acrylamid.filters import FilterList


def initialize(conf, env):
    """Initializes Jinja2 environment, prepares locale and configure
    some minor things. Filter and View are inited with conf and env,
    a request dict is returned.
    """
    # initialize cache, optional to cache_dir
    cache.init(conf.get('cache_dir', None))

    # set up templating environment
    env['jinja2'] = Environment(loader=ExtendedFileSystemLoader(conf['layout_dir']),
                                bytecode_cache=FileSystemBytecodeCache(cache.cache_dir))
    env['jinja2'].filters.update({'safeslug': utils.safeslug, 'tagify': lambda x: x})

    # try language set in LANG, if set correctly use it
    try:
        locale.setlocale(locale.LC_ALL, conf.get('lang', ''))
    except (locale.Error, TypeError):
        # try if LANG is an alias
        try:
            locale.setlocale(locale.LC_ALL, locale.locale_alias[conf['lang'].lower()])
        except (locale.Error, KeyError):
            # LANG is not an alias, so we use system's default
            locale.setlocale(locale.LC_ALL, '')
            log.info('notice  your OS does not support %s, fallback to %s', conf['lang'],
                     locale.getlocale()[0])
    if locale.getlocale()[0] is not None:
        conf['lang'] = locale.getlocale()[0][:2]
    else:
        # getlocale() is (None, None) aka 'C'
        conf['lang'] = 'en'

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

    # prepare, import and initialize filters and views
    if isinstance(conf['filters_dir'], basestring):
        conf['filters_dir'] = [conf['filters_dir'], ]

    if isinstance(conf['views_dir'], basestring):
        conf['views_dir'] = [conf['views_dir'], ]

    filters.initialize(conf["filters_dir"], conf, env, exclude=conf["filters_ignore"],
                                                       include=conf["filters_include"])
    views.initialize(conf["views_dir"], conf, env)
    env['views'] = dict([(v.view, v) for v in views.get_views()])

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
    entrylist = sorted([FileEntry(e, conf) for e in filelist(conf['content_dir'],
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
            entry.filters.add(sorted(flst, key=lambda k: (-k.priority, k.name)),
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

        for html, path in v.generate(request):
            utils.mkfile(html, path, time.time()-tt, **options)
            tt = time.time()

    log.info('Blog compiled in %.2fs' % (time.time() - ctime))


def autocompile(conf, env, **options):
    """Subcommand: autocompile -- automatically re-compiles when something in
    content-dir has changed and parallel serving files."""

    mtime = -1

    while True:
        ntime = max(getmtime(e) for e in filelist(conf['content_dir']))
        if mtime != ntime:
            try:
                compile(conf, env, **options)
            except AcrylamidException as e:
                log.fatal(e.message)
                pass
            mtime = ntime
        time.sleep(1)


def clean(conf, everything=False, dryrun=False, **kwargs):
    """Attention: this function may eat your data!  Every create, changed
    or skip event call tracks automatically files. After generation,
    ``acrylamid clean`` will call this function and remove untracked files.

    - with OUTPUT_IGNORE you can specify a list of patterns which are ignored.
    - you can use --dry-run to see what would have been removed
    - by default acrylamid does NOT call this function
    - it removes silently every empty directory

    :param conf: user configuration
    :param every: remove all tracked files, too
    :param dryrun: don't delete, just show what would have been done
    """

    def excluded(root, path, excl_files):
        """Test wether a path is excluded by the user. The ignore syntax is
        similar to Git: a path with a leading slash means absolute position
        (relative to output root), path with trailing slash marks a directory
        and everything else is just relative fnmatch.

        :param root: current directory
        :param path: current path
        :param excl_files: a list of patterns
        """
        for pattern in excl_files:
            if pattern.startswith('/'):
                if fnmatch(join(root, path), join(conf['output_dir'], pattern[1:])):
                    return True
            elif fnmatch(path, pattern):
                return True
        else:
            return False

    _tracked_files = utils.get_tracked_files()
    for root, dirs, files in os.walk(conf['output_dir'], topdown=True):
        found = set([join(root, p) for p in files
                     if not excluded(root, p, conf['output_ignore'])])

        for i, p in enumerate(found.difference(_tracked_files)):
            if not dryrun:
                os.remove(p)
            event.removed(p)

        if everything:
            for i, p in enumerate(found.intersection(_tracked_files)):
                if not dryrun:
                    os.remove(p)
                event.removed(p)

        # don't visit excluded dirs
        for dir in dirs[:]:
            if excluded(root, dir+'/', conf['output_ignore']):
                dirs.remove(dir)

    # remove empty directories
    for root, dirs, files in os.walk(conf['output_dir'], topdown=True):
        for p in (join(root, k) for k in dirs):
            try:
                os.rmdir(p)
            except OSError:
                pass

    # remove abandoned cache files
    utils.cache.clean(dryrun)


def new(conf, env, title, prompt=True):
    """Subcommand: new -- create a new blog entry the easy way.  Either run
    ``acrylamid new My fresh new Entry`` or interactively via ``acrylamid new``
    and the file will be created using the preferred permalink format."""

    fd, tmp = tempfile.mkstemp(suffix='.txt', dir='.cache/')
    editor = os.getenv('VISUAL') if os.getenv('VISUAL') else os.getenv('EDITOR')

    if not title:
        title = raw_input("Entry's title: ")
    title = escape(title)

    with os.fdopen(fd, 'wb') as f:
        f.write('---\n')
        f.write('title: %s\n' % title)
        f.write('date: %s\n' % datetime.now().strftime(conf['date_format']))
        f.write('---\n\n')

    entry = FileEntry(tmp, conf)
    p = join(conf['content_dir'], dirname(entry.permalink)[1:])

    try:
        os.makedirs(p.rsplit('/', 1)[0])
    except OSError:
        pass

    filepath = p + '.txt'
    if isfile(filepath):
        raise AcrylamidException('Entry already exists %r' % filepath)
    os.rename(tmp, filepath)
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
    argument after ``acrylamid deploy task ARG1 ARG2`` is appended to cmd."""

    cmd = conf.get('deployment', {}).get(task, None)
    if not cmd:
        raise AcrylamidException('no tasks named %r in conf.py' % task)

    if '%s' in cmd:
        cmd = cmd.replace('%s', conf['output_dir'])
    else:
        # append output-string
        cmd += ' ' + conf['output_dir']

    # apply ARG1 ARG2 ... and -v --long-args to the command, e.g.:
    # $> acrylamid deploy task arg1 -- -b --foo
    cmd += ' ' + ' '.join(args)

    log.info('execute %s', cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        output = p.stdout.read(1)
        if output == '' and p.poll() != None:
            break
        if output != '':
            sys.stdout.write(output)
            sys.stdout.flush()


__all__ = ["compile", "autocompile", "new", "clean", "importer", "deploy"]
