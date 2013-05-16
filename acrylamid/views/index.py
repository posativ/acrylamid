# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from acrylamid.views import View, Paginator


class Index(View, Paginator):
    """Creates nicely paged listing of your posts. First page renders to ``route``
    (defaults to */*) with a recent list of your (e.g. summarized) articles. Other
    pages enumerate to the variable ``pagination`` (*/page/:num/* per default).

    .. code-block:: python

        '/' : {
            'view': 'index',
            'template': 'main.html',
            'pagination': '/page/:num/',
            'items_per_page': 10
        }
    """

    export = ['prev', 'curr', 'next', 'items_per_page', 'entrylist']
    template = 'main.html'

    def init(self, *args, **kwargs):
        View.init(self, *args, **kwargs)
        Paginator.init(self, *args, **kwargs)
        self.filters.append('relative')
