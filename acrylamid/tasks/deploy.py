# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import os
import warnings
import subprocess

from acrylamid import log
from acrylamid.errors import AcrylamidException

aliases = ('deploy', 'dp')
usage = "%prog " + sys.argv[1] + " [TASK]"
options = []

def run(conf, env, args, **options):
    """Subcommand: deploy -- run the shell command specified in
    DEPLOYMENT[task] using Popen. Each string value from :doc:`conf.py` is
    added to the execution environment. Every argument after ``acrylamid
    deploy task ARG1 ARG2`` is appended to cmd."""

    if len(args) < 1:
        for task in conf.get('deployment', {}).keys():
            print >>sys.stdout, task
        sys.exit(0)

    task, args = args[0], args[1:]
    cmd = conf.get('deployment', {}).get(task, None)

    if not cmd:
        raise AcrylamidException('no tasks named %r in conf.py' % task)

    # apply ARG1 ARG2 ... and -v --long-args to the command, e.g.:
    # $> acrylamid deploy task arg1 -- -b --foo
    cmd += ' ' + ' '.join(args)

    if '%s' in cmd:
        warnings.warn('replace substitution variable with $OUTPUT_DIR',
                      category=DeprecationWarning)
        cmd = cmd.replace('%s', '$OUTPUT_DIR')

    env = os.environ
    env.update(dict([(k.upper(), v) for k, v in conf.items() if isinstance(v, basestring)]))

    log.info('execute %s', cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        output = p.stdout.read(1)
        if output == '' and p.poll() != None:
            break
        if output != '':
            sys.stdout.write(output)
            sys.stdout.flush()
