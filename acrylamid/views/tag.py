# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import math
import random

from collections import defaultdict

from acrylamid.compat import iteritems
from acrylamid.helpers import expand, safeslug, hash
from acrylamid.views.index import Index, Paginator


def fetch(entrylist):
    """Fetch tags from list of entries and map tags to most common tag name
    """
    tags = defaultdict(list)
    tmap = defaultdict(int)

    for e in entrylist:
        for tag in e.tags:
            tags[tag.lower()].append(e)
            tmap[tag] += 1

    # map tags to the most counted tag name
    for name in list(tags.keys()):
        key = max([(tmap[key], key) for key in tmap
                   if key.lower() == name])[1]
        rv = tags.pop(key.lower())
        tags[key] = rv

    return tags


class Tagcloud(object):
    """Tagcloud helper class similar (almost identical) to pelican's tagcloud helper object.
    Takes a bunch of tags and produces a logarithm-based partition and returns a iterable
    object yielding a Tag-object with two attributes: name and step where step is the
    calculated step size (== font size) and reaches from 0 to steps-1.

    :param tags: a dictionary of tags, e.g. {'name', [list of entries]}
    :param steps: maximum steps
    :param max_items: maximum items shown in tagcloud
    :param start: start index of steps resulting in start to steps+start-1 steps."""

    def __init__(self, tags, steps=4, max_items=100, start=0, shuffle=False):

        lst = sorted([(k, len(v)) for k, v in iteritems(tags)],
            key=lambda x: x[0])[:max_items]
        # stolen from pelican/generators.py:286
        max_count = max(lst, key=lambda k: k[1])[1] if lst else None
        self.lst = [(tag, count, 
                        int(math.floor(steps - (steps - 1) * math.log(count)
                            / (math.log(max_count) or 1)))+start-1)
                    for tag, count in lst]

        if shuffle:
            random.shuffle(self.lst)

        self.tags = tags

    def __iter__(self):
        for tag, count, step in self.lst:
            yield type('Tag', (), {'name': tag, 'step': step, 'count': count})

    def __hash__(self):
        return hash(*self.lst)

    def __getitem__(self, tag):
        return self.tags[tag.name]


class Tag(Index):
    """Same behaviour like Index except ``route`` that defaults to */tag/:name/* and
    ``pagination`` that defaults to */tag/:name/:num/* where :name is the current
    tag identifier.

    To create a tag cloud head over to :doc:`conf.py`.
    """

    export = ['prev', 'curr', 'next', 'items_per_page', 'tag', 'entrylist']
    template = 'main.html'

    def populate_tags(self, request):

        tags = fetch(request['entrylist'])
        self.tags = tags
        return tags

    def context(self, conf, env, request):

        class Link:

            def __init__(self, title, href):
                self.title = title
                self.href = href

        def tagify(tags):
            href = lambda t: expand(self.path, {'name': safeslug(t)})
            return [Link(t, href(t)) for t in tags] if isinstance(tags, (list, tuple)) \
                else Link(tags, href(tags))

        tags = self.populate_tags(request)
        env.engine.register('tagify', tagify)
        env.tag_cloud = Tagcloud(tags, conf['tag_cloud_steps'],
                                       conf['tag_cloud_max_items'],
                                       conf['tag_cloud_start_index'],
                                       conf['tag_cloud_shuffle'])

        return env

    def generate(self, conf, env, data):
        """Creates paged listing by tag."""

        for tag in self.tags:

            data['entrylist'] = [entry for entry in self.tags[tag]]
            for res in Paginator.generate(self, conf, env, data, tag=tag, name=safeslug(tag)):
                yield res
