# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of posativ <info@posativ.org>.

__version__ = '0.3.5'
__author__ = 'posativ <info@posativ.org>'
__url__ = 'https://github.com/posativ/acrylamid/'

import sys
PY3 = sys.version_info[0] == 3

import os
import time
import argparse
import traceback
import signal

from acrylamid import defaults, log, commands, colors, tasks
from acrylamid.utils import execfile, Bunch
from acrylamid.errors import AcrylamidException

signal.signal(signal.SIGINT, signal.SIG_DFL)
sys.path.append(os.path.dirname(__file__))


class AcrylFormatter(argparse.HelpFormatter):
    """Remove {a,b,c,d,e,...} subcommand listing from help."""

    def _metavar_formatter(self, action, default_metavar):
        if action.metavar is not None:
            result = action.metavar
        elif action.choices is not None:
            result = ''
        else:
            result = default_metavar

        def format(tuple_size):
            if isinstance(result, tuple):
                return result
            else:
                return (result, ) * tuple_size

        return format


class Environment(dict):

    def __getattribute__(self, attr):
        try:
            return getattr(super(Environment, self), attr)
        except AttributeError:
            try:
                return self[attr]
            except KeyError:
                raise AttributeError

    def __setattribute__(self, attr, value):
        self[attr] = value


def Acryl():
    """The main function that dispatches the CLI.  We use :class:`AcrylFormatter`
    as custom help formatter that ommits the useless list of available subcommands
    and their aliases.

    All flags from acrylamid --help are also available in subcommands altough not
    explicitely printed in their help."""

    parser = argparse.ArgumentParser(
        parents=[], formatter_class=AcrylFormatter
    )
    parser.add_argument("-v", "--verbose", action="store_const", dest="verbosity",
        help="more verbose", const=log.SKIP, default=log.INFO)
    parser.add_argument("-q", "--quiet", action="store_const", dest="verbosity",
        help="less verbose", const=log.WARN)
    parser.add_argument("-C", "--no-color", action="store_false", dest="colors",
        help="disable color", default=True)
    parser.add_argument("--version", action="version",
        version=colors.blue('acrylamid ') + __version__)

    subparsers = parser.add_subparsers(dest="parser")

    # a repeat yourself of default arguments but not visible on subcommand --help
    default = argparse.ArgumentParser(add_help=False)
    default.add_argument("-v", "--verbose", action="store_const", dest="verbosity",
        help=argparse.SUPPRESS, const=log.SKIP, default=log.INFO)
    default.add_argument("-q", "--quiet", action="store_const", dest="verbosity",
        help=argparse.SUPPRESS, const=log.WARN)
    default.add_argument("-C", "--no-color", action="store_false", dest="colors",
        help=argparse.SUPPRESS, default=True)

    # --- init params --- #
    init = subparsers.add_parser('init', help='initializes base structure in DIR',
        parents=[default, ])
    init.add_argument("dest", metavar="DEST|FILE", nargs="?")
    init.add_argument("-f", "--force", action="store_true", dest="force",
        help="don't ask, just overwrite", default=False)
    init.add_argument("--xhtml", action="store_const", dest="theme", const="xhtml",
        help="use XHTML theme", default="html5")
    init.add_argument("--html5", action="store_const", dest="theme", const="html5",
        help="use HTML5 theme (default)")
    init.add_argument("--mako", action="store_const", dest="engine", const="mako",
        help="use the Mako template engine")
    init.add_argument("--jinja2", action="store_const", dest="engine", const="jinja2",
        help="use the Jinja2 template engine (default)", default="jinja2")

    # --- gen params --- #
    generate = subparsers.add_parser('compile', help='compile blog', parents=[default])
    generate.add_argument("-f", "--force", action="store_true", dest="force",
        help="clear cache before compilation", default=False)
    generate.add_argument("-n", "--dry-run", dest="dryrun", action='store_true',
        help="show what would have been compiled", default=False)
    generate.add_argument("-i", "--ignore", dest="ignore", action="store_true",
        help="ignore critical errors", default=False)

    # --- webserver params --- #
    view = subparsers.add_parser('view', help="fire up built-in webserver", parents=[default])
    view.add_argument("-p", "--port", dest="port", type=int, default=8000,
        help="webserver port")

    # --- aco params --- #
    autocompile = subparsers.add_parser('autocompile', help="automatic compilation and serving",
        parents=[default])
    autocompile.add_argument("-f", "--force", action="store_true", dest="force",
        help="clear cache before compilation", default=False)
    autocompile.add_argument("-n", "--dry-run", dest="dryrun", action='store_true',
        help="show what would have been compiled", default=False)
    autocompile.add_argument("-i", "--ignore", dest="ignore", action="store_true",
        help="ignore critical errors", default=False)
    autocompile.add_argument("-p", "--port", dest="port", type=int, default=8000,
        help="webserver port")

    # --- import params --- #
    importer = subparsers.add_parser('import', help="import content from URL or FILE",
        parents=[default])
    importer.add_argument("src", metavar="FILE|URL")
    importer.add_argument("-f", "--force", dest="force", action="store_true",
        help="overwrite existing entries", default=False)
    importer.add_argument("-m", dest="fmt", default="Markdown", help="reconvert HTML to FMT")
    importer.add_argument("-k", "--keep-links", dest="keep", action="store_true",
        help="keep permanent links", default=False)
    importer.add_argument("-p", "--pandoc", dest="pandoc", action="store_true",
        help="use pandoc first", default=False),

    for alias in ('co', 'gen', 'generate'):
        subparsers._name_parser_map[alias] = generate

    for alias in ('serve', 'srv'):
        subparsers._name_parser_map[alias] = view

    subparsers._name_parser_map['aco'] = autocompile

    new = subparsers.add_parser('new', help="create a new entry", parents=[default],
        epilog=("Takes all leading [args] as title or prompt if none given. creates "
                "a new entry based on your PERMALINK_FORMAT and opens it with your "
                "favourite $EDITOR."))
    new.add_argument("title", nargs="*", default='')

    # initialize other tasks
    tasks.initialize(subparsers, default)

    # parse args
    options = parser.parse_args()

    # initialize colored logger
    log.init('acrylamid', level=options.verbosity, colors=options.colors)

    env = Environment({'version': __version__, 'author': __author__, 'url': __url__})
    env['options'] = options

    # -- init -- #
    # TODO: acrylamid init --layout_dir=somedir to overwrite defaults
    if options.parser in ('init', ):
        defaults.init(options.dest if options.dest else '.', options.theme, options.engine, options.force)
        sys.exit(0)

    # -- teh real thing -- #
    conf = Bunch(defaults.conf)

    try:
        ns = dict([(k.upper(), v) for k, v in defaults.conf.iteritems()])
        execfile('conf.py', ns)
        conf.update(dict([(k.lower(), ns[k]) for k in ns if k.upper() == k]))
    except OSError:
        log.critical('no config file found: %s. Try "acrylamid init".', options.conf)
        sys.exit(1)
    except Exception, e:
        log.critical("%s in `conf.py`" % e.__class__.__name__)
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

    conf['output_dir'] = conf.get('output_dir', 'output/')
    conf['content_dir'] = conf.get('content_dir', 'content/')
    conf['layout_dir'] = conf.get('layout_dir', 'layouts/')

    assert defaults.check_conf(conf)
    conf.update(dict((k, v) for k, v in options.__dict__.iteritems() if v != None))

    # -- run -- #
    if options.parser in ('gen', 'generate', 'co', 'compile'):
        log.setLevel(options.verbosity)
        try:
            commands.compile(conf, env, **options.__dict__)
        except AcrylamidException as e:
            log.fatal(e.args[0])
            sys.exit(1)

    elif options.parser in ('new', 'create'):
        try:
            commands.new(conf, env, title=' '.join(options.title), prompt=log.level()<log.WARN)
        except AcrylamidException as e:
            log.fatal(e.args[0])
            sys.exit(1)

    elif options.parser in ('srv', 'serve', 'view'):
        from acrylamid.lib.httpd import Webserver
        ws = Webserver(options.port, conf['output_dir']); ws.start()
        log.info(' * Running on http://127.0.0.1:%i/' % options.port)

        try:
            while True:
                time.sleep(1)
        except (SystemExit, KeyboardInterrupt, Exception) as e:
            ws.kill_received = True
            sys.exit(0)

    elif options.parser in ('aco', 'autocompile'):
        from acrylamid.lib.httpd import Webserver
        # XXX compile on request _or_ use inotify/fsevent
        ws = Webserver(options.port, conf['output_dir']); ws.start()
        log.info(' * Running on http://127.0.0.1:%i/' % options.port)

        try:
            commands.autocompile(conf, env, **options.__dict__)
        except (SystemExit, KeyboardInterrupt, Exception) as e:
            ws.kill_received = True
            log.error(e.args[0])
            traceback.print_exc(file=sys.stdout)
            sys.exit(0)

    elif options.parser in ('import', ):
        try:
            commands.imprt(conf, env, options.src, **options.__dict__)
        except AcrylamidException as e:
            log.critical(e.args[0])
            sys.exit(1)

    elif options.parser in tasks.collected:
        try:
            tasks.collected[options.parser](conf, env, options)
        except AcrylamidException as e:
            log.critical(e.args[0])
            sys.exit(1)
    else:
        log.critical('No such command!')
        sys.exit(2)

    sys.exit(0)
