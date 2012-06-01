# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py


class ANSIString(object):

    style = 0
    color = 0

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
        return unicode(self).decode('utf-8')

    def __add__(self, other):
        return unicode.__add__(unicode(self), other)


normal = lambda obj: ANSIString(obj, style=0)
bold   = lambda obj: ANSIString(obj, style=1)
underline = lambda obj: ANSIString(obj, style=2)

black  = lambda obj: ANSIString(obj, color=30)
red    = lambda obj: ANSIString(obj, color=31)
green  = lambda obj: ANSIString(obj, color=32)
yellow = lambda obj: ANSIString(obj, color=33)
blue   = lambda obj: ANSIString(obj, color=34)
magenta= lambda obj: ANSIString(obj, color=35)
cyan   = lambda obj: ANSIString(obj, color=36)
white  = lambda obj: ANSIString(obj, color=37)
