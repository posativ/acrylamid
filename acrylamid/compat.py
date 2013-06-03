# -*- encoding: utf-8 -*-
#
# Copyright 2013 Armin Ronacher <armin.ronacher@active-4.com>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.
#
# http://lucumr.pocoo.org/2013/5/21/porting-to-python-3-redux/

import sys
PY2K = sys.version_info[0] == 2

if not PY2K:

    unichr = chr
    text_type = str
    string_types = (str, )
    implements_to_string = lambda x: x

    map, zip, filter = map, zip, filter

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())

else:

    unichr = unichr
    text_type = unicode
    string_types = (str, unicode)

    from itertools import imap, izip, ifilter
    map, zip, filter = imap, izip, ifilter

    def implements_to_string(cls):

        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode('utf-8')
        return cls

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()


def metaclass(meta, *bases):

    class Meta(meta):

        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)

    return Meta('temporary_class', None, {})
