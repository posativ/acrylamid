# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

"""
Requests
~~~~~~~~

A simple wrapper around urllib2.

.. function:: head(url, **hdrs)

    Sends a HEAD request to given url but does not catch any exception.

    :param url: url to send the request to
    :param hdrs: a key-value pair that is send within the HTTP header

.. function:: get(url, **hdrs)

    Same like :func:`head` but for GET."""

from urllib2 import Request, urlopen, HTTPError, URLError


def proto(method, url, **hdrs):

    headers = {'User-Agent': "Mozilla/5.0 Gecko/20120427 Firefox/15.0"}
    headers.update(hdrs)

    req = Request(url, headers=headers)
    req.get_method = lambda : method

    return urlopen(req, timeout=10)


head = lambda url, **hdrs: proto('HEAD', url, **hdrs)
get = lambda url, **hdrs: proto('GET', url, **hdrs)


__all__ = ['head', 'get', 'HTTPError', 'URLError']
