# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# via http://code.activestate.com/recipes/577187-python-thread-pool/

"""
Asynchronous Tasks
~~~~~~~~~~~~~~~~~~

A simple thread pool implementation, that can be used for parallel I/O.

Example usage::

    >>> def takes(long=10):
    ...     sleep(long)
    ...
    >>> pool = ThreadPool(5)
    >>> for x in range(10):
    ...     pool.add_task(takes, x)
    >>> pool.wait_completion()

You can't retrieve the return values, just wait until they finish."""

from Queue import Queue
from threading import Thread

from acrylamid import log


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                log.warn('%s: %s' % (e.__class__.__name__, unicode(e)))
            self.tasks.task_done()


class Threadpool:
    """Initialize pool with number of workers, that run a function with
    given arguments and catch all exceptions."""

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
