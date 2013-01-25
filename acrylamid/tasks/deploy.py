# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import sys
import os
import argparse
import subprocess

from acrylamid import log
from acrylamid.tasks import argument, task
from acrylamid.errors import AcrylamidException

arguments = [
    argument("task", nargs="?"),
    argument("args", nargs=argparse.REMAINDER),
    argument("--list", dest="list", action="store_true", default=False,
        help="list available tasks")
]


@task(['deploy', 'dp'], arguments, help="run task")
def run(conf, env, options):
    """Subcommand: deploy -- run the shell command specified in
    DEPLOYMENT[task] using Popen. Each string value from :doc:`conf.py` is
    added to the execution environment. Every argument after ``acrylamid
    deploy task ARG1 ARG2`` is appended to cmd."""

    if options.list:
        for task in conf.get('deployment', {}).keys():
            print >>sys.stdout, task
        sys.exit(0)

    task, args = options.task or 'default', options.args
    cmd = conf.get('deployment', {}).get(task, None)

    if not cmd:
        raise AcrylamidException('no tasks named %r in conf.py' % task)

    # apply ARG1 ARG2 ... and -v --long-args to the command, e.g.:
    # $> acrylamid deploy task arg1 -b --foo
    cmd += ' ' + ' '.join(args)

    enc = sys.getfilesystemencoding()
    env = os.environ
    env.update(dict([(k.upper(), v.encode(enc, 'replace')) for k, v in conf.items() if isinstance(v, basestring)]))

    log.info('execute  %s', cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        output = p.stdout.read(1)
        if output == '' and p.poll() != None:
            break
        if output != '':
            sys.stdout.write(output)
            sys.stdout.flush()
