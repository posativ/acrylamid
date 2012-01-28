#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
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

VERSION = "0.3.0-dev"
VERSION_SPLIT = tuple(VERSION.split('-')[0].split('.'))

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import time
import traceback
import signal

from optparse import OptionParser, make_option, OptionGroup
from acrylamid import defaults, log, commands, utils
from acrylamid.errors import AcrylamidException

signal.signal(signal.SIGINT, signal.SIG_DFL)
sys.path.insert(0, os.path.dirname(__package__))


class Acryl:
    """Main class for acrylamid functionality.  It handles initialization,
    defines default behavior, and also pushes the request through all
    steps until the output is rendered and we're complete."""

    def __init__(self, conf=None):
        """Sets configuration and environment and creates the Request
        object"""

        usage = "usage: %prog [options] init\n" + '\n' \
                + "init         - initializes base structure\n" \
                + "compile      - render blog\n" \
                + "autocompile  - serving on port -p (8000) with auto-compile\n" \
                + "clean        - remove orphans or all from output_dir\n" \
                + "serve        - builtin webserver on port -p (8000)\n"

        options = [
            make_option("-v", "--verbose", action="store_const", dest="verbosity",
                              help="more verbose", const=log.SKIP),
            make_option("-q", "--quit", action="store_const", dest="verbosity",
                              help="be silent", const=log.WARN,
                              default=log.INFO),
            make_option("-c", "--conf", dest="cfile", help="alternate conf.py",
                              default="conf.py"),

            # --- gen params --- #
            make_option("-f", "--force", action="store_true", dest="force",
                              help="force re-render", default=False),
            make_option("-n", "--dry-run", dest="dryrun", action='store_true',
                               default=False, help="show what would have been deleted"),

            # --- webserver params --- #
            make_option("-p", "--port", dest="port", type=int, default=8000,
                        help="webserver port"),

            make_option("--version", action="store_true", dest="version",
                               help="print version details", default=False),
            ]

        parser = OptionParser(option_list=options, usage=usage)
        ext_group = OptionGroup(parser, "conf.py override")

        # update --help with default values, XXX: show full help only when --help or --help -v
        for key, value in defaults.conf.iteritems():
            if key in ['views', 'filters']:
                continue
            ext_group.add_option('--' + key.replace('_', '-'), action="store",
                            dest=key, metavar=value, type=type(value) if type(value) != list else str)

        parser.add_option_group(ext_group)
        (options, args) = parser.parse_args()

        # initialize colored logger
        log.init('acrylamid', level=options.verbosity)

        env = {'VERSION': VERSION, 'VERSION_SPLIT': VERSION_SPLIT}
        if options.version:
            print "acrylamid" + ' ' + env['VERSION']
            sys.exit(0)

        if len(args) < 1:
            parser.print_usage()
            sys.exit(1)

        # -- init -- #
        # TODO: acrylamid init --layout_dir=somedir to overwrite defaults

        if 'init' in args:
            if len(args) == 2:
                defaults.init(args[1], options.force)
            else:
                defaults.init(overwrite=options.force)
            sys.exit(0)

        # -- teh real thing -- #
        conf = defaults.conf

        try:
            ns = {}
            execfile(options.cfile, ns)
            conf.update(dict([(k.lower(), ns[k]) for k in ns if k.upper() == k]))
        except OSError:
            log.critical('no config file found: %s. Try "acrylamid init".', options.conf)
            sys.exit(1)
        except Exception, e:
            log.critical("%s in `conf.py`" % e.__class__.__name__)
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)

        conf['acrylamid_name'] = "acrylamid"
        conf['acrylamid_version'] = env['VERSION']

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

        elif args[0] in ('new', ):
            commands.new(conf, env, title=' '.join(args[1:]))

        elif args[0] in ('clean', 'rm'):
            try:
                log.setLevel(options.verbosity+5)
                commands.compile(conf, env, dryrun=True, force=False)
                log.setLevel(options.verbosity)
                utils.clean(conf, everything=options.force, **options.__dict__)
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
                sys.exit(0)
