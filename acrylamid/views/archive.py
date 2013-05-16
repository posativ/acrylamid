# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from os.path import isfile

from acrylamid.utils import neighborhood, groupby
from acrylamid.views import View
from acrylamid.helpers import union, joinurl, event, expand, memoize, hash, link
from acrylamid.readers import Date


class Day(object):

    def __init__(self, name, items=[]):
        self.name = name
        self.items = items

    @property
    def abbr(self):
        return Date(2001, 1, self.name).strftime('%a')

    @property
    def full(self):
        return Date(2001, 1, self.name).strftime('%A')

    def __str__(self):
        return '%02i' % self.name


class Month(Day):

    yields = Day
    keyfunc = lambda self, d: d.iday

    def __iter__(self):
        for k, group in groupby(self.items, self.keyfunc):
            yield self.yields(k, list(group))

    def __len__(self):
        return len(self.items)

    @property
    def abbr(self):
        return Date(2001, self.name, 1).strftime('%b')

    @property
    def full(self):
        return Date(2001, self.name, 1).strftime('%B')


class Year(Month):

    yields = Month
    keyfunc = lambda self, m: m.imonth


class Archive(View):
    """A view that lists all posts per year/month/day -- usually found in
    WordPress blogs. Configuration syntax:

    .. code-block:: python

        '/:year/': {'view': 'archive'},
        '/:year/:month/': {'view': 'archive'},
        '/:year/:month/:day/': {'view': 'archive'}

    During templating you can access the current archive year/month/day via
    ``env.archive`` which basically holds the year, month and day, although
    the latter two may be ``None`` in case of a route without month or day.
    To determine the current archive name, you can use the following snippet:

    .. code-block:: html+jinja

        {% set archivesname = env.archive.year
                            ~ (('/' ~ env.archive.month) if env.archive.month else '')
                            ~ (('/' ~ env.archive.day) if env.archive.day else '')  %}


    Rendering a list of entries is the same like in other views:

    .. code-block:: html+jinja

        {% for entry in env.entrylist %}
        <a href="{{ entry.permalink }}">{{ entry.title | e }}</a>
        {% endfor %}

    To link to the archive pages, you can either link the entry date as there
    is at least one entry in that timerange: the entry itself. But you can also
    generate a complete archive listing as you may know from WordPress. This
    does only includes years, months and/or days where you have at least a
    single post.

    .. code-block:: html+jinja

        {% for year in env.globals.entrylist | archivesfor %}
        <h2>{{ year ~ ' (' ~ year | count ~ ')' }}</h2>
        <ul>
            {% for month in year %}
            <li>
                <a href="{{ env.path ~ '/' ~ year ~ '/' ~ month ~ '/'  }}">{{ month.full }}</a>
                ({{  month | count }})
            </li>
            {% endfor %}
        </ul>
        {% endfor %}

    This generates a listing that shows the amount of postings during the
    period. You can also iterate over each month to get to the days.
    :class:`Year`, :class:`Month` and :class:`Day` objects always evaluate to
    a zero-padded date unit such as 2012 (year) or 01 (January). In addition,
    Month and Day objects have ``full`` and ``abbr`` attributes to access the
    fullname or abbreviation in your current location.

    You can retrieve the posts from the :class:`Year`, :class:`Month` and
    :class:`Day` via the ``.items`` attribute.

    .. code-block:: html+jinja

        {% for year in env.globals.entrylist | archivesfor %}
            <h2>{{ year ~ ' (' ~ year | count ~ ')' }}</h2>
            {% for entry in year.items %}
                <a href="{{ entry.permalink }}">{{ entry.title }}</a>
            {% endfor %}
        {% endfor %}
    """

    priority = 80.0

    def init(self, conf, env, template='listing.html'):
        self.template = template

    def context(self, conf, env, data):

        env.engine.register('archivesfor', lambda entrylist:
            [Year(k, list(group)) for k, group in groupby(entrylist, lambda e: e.year)])

        return env

    def generate(self, conf, env, data):

        tt = env.engine.fromfile(env, self.template)
        keyfunc = lambda k: ( )

        if '/:year' in self.path:
            keyfunc = lambda k: (k.year, )
        if '/:month' in self.path:
            keyfunc = lambda k: (k.year, k.imonth)
        if '/:day' in self.path:
            keyfunc = lambda k: (k.year, k.imonth, k.iday)

        for next, curr, prev in neighborhood(groupby(data['entrylist'], keyfunc)):

            salt, group = '-'.join(str(i) for i in curr[0]), list(curr[1])
            modified = memoize('archive-' + salt, hash(*group)) or any(e.modified for e in group)

            if prev:
                prev = link(u'/'.join('%02i' % i for i in prev[0]), expand(self.path, prev[1][0]))
            if next:
                next = link(u'/'.join('%02i' % i for i in next[0]), expand(self.path, next[1][0]))

            route = expand(self.path, group[0])
            path = joinurl(conf['output_dir'], route)

            # an object storing year, zero-padded month and day as attributes (may be None)
            key = type('Archive', (object, ), dict(zip(('year', 'month', 'day'),
                map(lambda x: '%02i' % x if x else None, keyfunc(group[0]))
            )))()

            if isfile(path) and not (modified or tt.modified or env.modified or conf.modified):
                event.skip('archive', path)
                continue

            html = tt.render(conf=conf, env=union(env, entrylist=group,
                type='archive', prev=prev, curr=link(route), next=next,
                num_entries=len(group), route=route, archive=key))

            yield html, path
