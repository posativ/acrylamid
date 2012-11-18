# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys


class ANSIString(object):

    style = 0
    color = 30

    def __init__(self, obj, style=None, color=None):

        if isinstance(obj, ANSIString):
            if style is None:
                style = obj.style
            if color is None:
                color = obj.color
            obj = obj.obj
        elif not isinstance(obj, basestring):
            obj = unicode(obj)

        self.obj = obj
        if style:
            self.style = style
        if color:
            self.color = color

    def __unicode__(self):
        return '\033[%i;%im' % (self.style, self.color) + self.obj + '\033[0m'

    def __str__(self):
        if sys.version_info < (3, 0):
            return unicode(self).encode('utf-8')
        return self.__unicode__()

    def __add__(self, other):
        return unicode.__add__(unicode(self), other)

    def __radd__(self, other):
        return other + unicode(self)

    def encode(self, encoding):
        return unicode(self).encode(encoding)


normal, bold, underline = [lambda obj, x=x: ANSIString(obj, style=x)
    for x in 0, 1, 4]

black, red, green, yellow, blue, \
magenta, cyan, white = [lambda obj, y=y: ANSIString(obj, color=y)
    for y in range(30, 38)]
