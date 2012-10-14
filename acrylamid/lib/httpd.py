# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

"""
Internal Webserver
~~~~~~~~~~~~~~~~~~

Launch a dumb webserver as thread."""

import os
import time
import urllib
import posixpath

from threading import Thread
from SocketServer import TCPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

from acrylamid.helpers import joinurl


class ReuseAddressServer(TCPServer):
    """avoids socket.error: [Errno 48] Address already in use"""
    allow_reuse_address = True

    def serve_forever(self):
        """Handle one request at a time until doomsday."""
        while not self.kill_received:
            if not self.wait:
                self.handle_request()
            else:
                time.sleep(0.1)


class RequestHandler(SimpleHTTPRequestHandler):
    """This is a modified version of python's -m SimpleHTTPServer to
    serve on a specific sub directory of :func:`os.getcwd`."""

    www_root = '.'

    def do_GET(self):
        self.path = joinurl(self.www_root, self.path)
        SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        self.wfile.write('Cache-Control: max-age=0, must-revalidate\r\n')
        SimpleHTTPRequestHandler.end_headers(self)


class Webserver(Thread):
    """A single-threaded webserver to serve while generation.

    :param port: port to listen on
    :param root: serve this directory under /"""

    def __init__(self, port=8000, root='.'):
        Thread.__init__(self)
        Handler = RequestHandler
        Handler.www_root = root
        Handler.log_error = lambda x, *y: None
        Handler.log_message = lambda x, *y: None

        self.httpd = ReuseAddressServer(("", port), Handler)
        self.httpd.wait = False
        self.httpd.kill_received = False

    def setwait(self, value):
        self.httpd.wait = value
    wait = property(lambda self: self.httpd.wait, setwait)

    def run(self):
        self.httpd.serve_forever()
        self.join(1)

    def shutdown(self):
        """"Sets kill_recieved and closes the server socket."""
        self.httpd.kill_received = True
        self.httpd.socket.close()
