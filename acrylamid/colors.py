# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

def colorize(obj, m, n):
    if not isinstance(obj, basestring):
        obj = unicode(obj)
    return '\033[%i;%im' % (m, n) + obj + '\033[0m'


red    = lambda obj: colorize(obj, 0, 31)
green  = lambda obj: colorize(obj, 0, 32)
yellow = lambda obj: colorize(obj, 0, 33)
blue   = lambda obj: colorize(obj, 0, 34)
white  = lambda obj: colorize(obj, 0, 37)
