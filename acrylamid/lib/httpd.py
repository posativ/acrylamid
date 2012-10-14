# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

"""
Internal Webserver
~~~~~~~~~~~~~~~~~~

Launch a dumb webserver as thread."""

from threading import Thread
import os
import SimpleHTTPServer
import SocketServer
import posixpath
import urllib


class ReuseAddressServer(SocketServer.TCPServer):
    """avoids socket.error: [Errno 48] Address already in use"""
    allow_reuse_address = True

    def serve_forever(self):
        """Handle one request at a time until doomsday."""
        while not self.kill_received:
            print self.wait
            if not self.wait:
                print self.wait
                self.handle_request()



class AcrylServe(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """This is a modified version of python's -m SimpleHTTPServer to
    serve on a specific sub directory of :func:`os.getcwd`."""

    www_root = '.'

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored. (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.path.join(os.getcwd(), self.www_root)
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path


class Webserver(Thread):
    """A single-threaded webserver to serve while generation.

    :param port: port to listen on
    :param root: serve this directory under /"""

    def __init__(self, port=8000, root='.'):
        Thread.__init__(self)
        Handler = AcrylServe
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
