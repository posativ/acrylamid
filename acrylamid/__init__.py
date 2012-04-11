#!/usr/bin/env python
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

__version__ = "0.3.1"
__author__ = 'posativ <info@posativ.org>'
__url__ = 'https://github.com/posativ/acrylamid/'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import time
import traceback
import signal

from optparse import OptionParser, make_option, SUPPRESS_HELP
from textwrap import fill
from acrylamid import defaults, log, commands
from acrylamid.errors import AcrylamidException

signal.signal(signal.SIGINT, signal.SIG_DFL)
sys.path.insert(0, os.path.dirname(__package__))


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


class Acryl:
    """Main class for acrylamid functionality.  It handles initialization,
    defines default behavior, and also pushes the request through all
    steps until the output is rendered and we're complete."""

    def __init__(self, conf=None):
        """Sets configuration and environment and creates the Request
        object"""

        global sys

        usage = "usage: %prog <subcommand> [options] [args]"
        epilog = None

        options, constants = [], [
            make_option("-h", "--help", action="store_true", help=SUPPRESS_HELP),
            make_option("-v", "--verbose", action="store_const", dest="verbosity",
                        help=SUPPRESS_HELP, const=log.SKIP),
            make_option("-q", "--quit", action="store_const", dest="verbosity",
                        help=SUPPRESS_HELP, const=log.WARN, default=log.INFO),
            make_option("-C", "--no-color", action="store_false", dest="colors",
                        default=True, help=SUPPRESS_HELP),
            make_option("--version", action="store_true", dest="version",
                            help=SUPPRESS_HELP, default=False)
            ]

        # reorder `prog help foo` and `prog --help foo`
        if len(sys.argv) > 2 and sys.argv[1] in ('--help', 'help'):
            sys.argv[1], sys.argv[2] = sys.argv[2], '--help'

        if len(sys.argv) <= 1 or sys.argv[1] in ('-h', '--help', 'help'):
            options, constants = [], [
                make_option("-q", "--quiet", action="store_const", dest="verbosity",
                        help="less verbose", const=log.WARN, default=log.INFO),
                make_option("-v", "--verbose", action="store_const", dest="verbosity",
                            help="more verbose", const=log.SKIP),
                make_option("-C", "--no-color", action="store_false", dest="colors",
                            default=True, help="disable color"),
                make_option("-h", "--help", action="store_true",
                            help="show this help message and exit"),
                make_option("--version", action="store_true", dest="version",
                            help="print version details", default=False)
            ]
            epilog = ("Commands:\n"
                      "  init           initializes base structure in DIR\n"
                      "  create  (new)  creates a new entry\n"
                      "  compile (co)   compile blog\n"
                      "  view           fire up built-in webserver\n"
                      "  autocompile    automatic compilation and serving (short aco)\n"
                      "  clean   (rm)   remove abandoned files\n"
                      "  import         import content from URL\n"
                      "  deploy         run a given TASK\n"
                      "\nAll subcommands except `init` require a conf.py file.\n")

        # --- init params --- #
        elif sys.argv[1] in ('init', 'initialize'):
            usage = "%prog " + sys.argv[1] + " [DEST|FILE] [-p]"
            options = [
                make_option("-f", "--force", action="store_true", dest="force",
                        help="don't ask, just overwrite", default=False),
                make_option("--xhtml", action="store_const", dest="theme", const="xhtml",
                            help="use XHTML theme", default="html5"),
                make_option("--html5", action="store_const", dest="theme", const="html5",
                            help="use HTML5 theme")
                ]
        # --- init params --- #
        elif sys.argv[1] in ('new',):
            usage = "%prog " + sys.argv[1] + " [args]"
            epilog = ("Takes all leading [args] as title or prompt if none given. creates "
                      "a new entry based on your PERMALINK_FORMAT and opens it with your "
                      "favourite EDITOR.")
            epilog = fill(epilog)+'\n'
        # --- gen params --- #
        elif sys.argv[1] in ('compile', 'co', 'generate', 'gen'):
            usage = "%prog " + sys.argv[1] + " [-fn]"
            options = [
                make_option("-f", "--force", action="store_true", dest="force",
                            help="clear cache before compilation", default=False),
                make_option("-n", "--dry-run", dest="dryrun", action='store_true',
                            default=False, help="show what would have been compiled"),
                make_option("-i", "--ignore", dest="ignore", action="store_true",
                            default=False, help="ignore critical errors")
            ]
        # --- webserver params --- #
        elif sys.argv[1] in ('view', 'serve', 'srv'):
            usage = "%prog " + sys.argv[1] + " [-p]"
            options = [
                make_option("-p", "--port", dest="port", type=int, default=8000,
                            help="webserver port"),
            ]
        # --- autocompile params --- #
        elif sys.argv[1] in ('autocompile', 'aco'):
            usage = "%prog " + sys.argv[1] + " [-pf]"
            options = [
                make_option("-f", "--force", action="store_true", dest="force",
                            help="clear cache before compilation", default=False),
                make_option("-i", "--ignore", dest="ignore", action="store_true",
                            default=False, help="ignore critical errors"),
                make_option("-p", "--port", dest="port", type=int, default=8000,
                            help="webserver port"),
            ]
        # --- clean params --- #
        elif sys.argv[1] in ('clean', 'rm'):
            usage = "%prog " + sys.argv[1] + " [-fn]"
            options = [
                make_option("-f", "--force", action="store_true", dest="force",
                            help="remove all files generated by Acrylamid", default=False),
                make_option("-n", "--dry-run", dest="dryrun", action='store_true',
                            default=False, help="show what would have been deleted"),
            ]
        # --- import params --- #
        elif sys.argv[1] in ('import', ):
            usage = "%prog " + sys.argv[1] + " [-mk]"
            options = [
                make_option("-m", dest="import_fmt", default="Markdown",
                            help="reconvert HTML to MARKUP"),
                make_option("-k", "--keep-links", dest="keep_links", action="store_true",
                            help="keep permanent links"),
            ]

        class AcrylParser(OptionParser):
            # -- http://stackoverflow.com/q/1857346
            def format_epilog(self, formatter):
                if epilog is None:
                    return ''
                return '\n' + self.epilog

        parser = AcrylParser(option_list=options+constants, usage=usage,
                              add_help_option=False, epilog=epilog)
        (options, args) = parser.parse_args()

        if len(sys.argv) <= 1 or sys.argv[1] == 'help' or options.help:
            parser.print_help()
            sys.exit(0)

        # initialize colored logger
        log.init('acrylamid', level=options.verbosity, colors=options.colors)

        env = Environment({'version': __version__, 'author': __author__, 'url': __url__})
        env['options'] = options

        if options.version:
            print 'acrylamid ' + env.version
            sys.exit(0)

        # -- init -- #
        # TODO: acrylamid init --layout_dir=somedir to overwrite defaults

        if 'init' in args:
            if len(args) == 2:
                defaults.init(args[1], options.theme, options.force)
            else:
                defaults.init('.', options.theme, options.force)
            sys.exit(0)

        # -- teh real thing -- #
        conf = defaults.conf

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
        conf['entries_dir'] = conf.get('entries_dir', 'content/')
        conf['layout_dir'] = conf.get('layout_dir', 'layouts/')

        assert defaults.check_conf(conf)
        conf.update(dict((k, v) for k, v in options.__dict__.iteritems() if v != None))

        # -- run -- #

        if args[0] in ('gen', 'generate', 'co', 'compile'):
            log.setLevel(options.verbosity-5)
            try:
                commands.compile(conf, env, **options.__dict__)
            except AcrylamidException as e:
                log.fatal(e.message)
                sys.exit(1)

        elif args[0] in ('new', 'create'):
            try:
                commands.new(conf, env, title=' '.join(args[1:]), prompt=log.level()<log.WARN)
            except AcrylamidException as e:
                log.fatal(e.message)
                sys.exit(1)

        elif args[0] in ('clean', 'rm'):
            try:
                log.setLevel(options.verbosity+5)
                options.ignore = True  # we don't bother the user here
                commands.compile(conf, env, dryrun=True, force=False)
                log.setLevel(options.verbosity)
                commands.clean(conf, everything=options.force, **options.__dict__)
            except AcrylamidException as e:
                log.fatal(e.message)
                sys.exit(1)

        elif args[0] in ('srv', 'serve', 'view'):
            from acrylamid.lib.httpd import Webserver
            ws = Webserver(options.port, conf['output_dir']); ws.start()
            log.info(' * Running on http://127.0.0.1:%i/' % options.port)

            try:
                while True:
                    time.sleep(1)
            except (SystemExit, KeyboardInterrupt, Exception) as e:
                ws.kill_received = True
                sys.exit(0)

        elif args[0] in ('aco', 'autocompile'):
            from acrylamid.lib.httpd import Webserver
            # XXX compile on request _or_ use inotify/fsevent
            ws = Webserver(options.port, conf['output_dir']); ws.start()
            log.info(' * Running on http://127.0.0.1:%i/' % options.port)

            try:
                commands.autocompile(conf, env, **options.__dict__)
            except (SystemExit, KeyboardInterrupt, Exception) as e:
                ws.kill_received = True
                log.error(e.message)
                traceback.print_exc(file=sys.stdout)
                sys.exit(0)

        elif args[0] in ('import', ):
            if len(args) <= 1:
                log.fatal('import requires a valid URL')
                sys.exit(1)
            try:
                commands.importer(conf, env, args[1], **options.__dict__)
            except AcrylamidException as e:
                log.critical(e.message)
                sys.exit(1)
        elif args[0] in ('deploy', 'dp', 'task'):
            if len(args) <= 1:
                log.fatal('deploy requires a build TASK')
                sys.exit(1)
            try:
                commands.deploy(conf, env, args[1], *args[2:])
            except AcrylamidException as e:
                log.critical(e.message)
                sys.exit(1)
        else:
            log.critical('No such command!')
            sys.exit(2)
