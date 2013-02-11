# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import math
import random

from os.path import isfile
from collections import defaultdict

from acrylamid.views import View
from acrylamid.helpers import union, joinurl, safeslug, event
from acrylamid.helpers import paginate, expand, link, hash


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
    for name in tags.keys()[:]:
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

        lst = sorted([(k, len(v)) for k, v in tags.iteritems()],
            key=lambda x: x[0])[:max_items]
        # stolen from pelican/generators.py:286
        max_count = max(lst, key=lambda k: k[1])[1] if lst else None
        self.lst = [(tag,
                        int(math.floor(steps - (steps - 1) * math.log(count)
                            / (math.log(max_count) or 1)))+start-1)
                    for tag, count in lst]

        if shuffle:
            random.shuffle(self.lst)

    def __iter__(self):
        for tag, step in self.lst:
            yield type('Tag', (), {'name': tag, 'step': step})

    def __hash__(self):
        return hash(*self.lst)


class Tag(View):
    """Same behaviour like Index except ``route`` that defaults to */tag/:name/* and
    ``pagination`` that defaults to */tag/:name/:num/* where :name is the current
    tag identifier.

    To create a tag cloud head over to :doc:`conf.py`.
    """


    def init(self, conf, env, template='main.html', items_per_page=10, pagination='/tag/:name/:num/'):
        self.template = template
        self.items_per_page = items_per_page
        self.pagination = pagination
        self.filters.append('relative')

    def populate_tags(self, request):

        tags = fetch(request['entrylist'] + request['translations'])
        self.tags = dict([(safeslug(k), v) for k, v in tags.iteritems()])
        return tags

    def context(self, conf, env, request):

        class Link:

            def __init__(self, title, href):
                self.title = title
                self.href = href if href.endswith('/') else href + '/'

        def tagify(tags):
            href = lambda t: expand(self.path, {'name': safeslug(t)})
            return [Link(t, href(t)) for t in tags]

        tags = self.populate_tags(request)
        env.engine.register('tagify', tagify)
        env.tag_cloud = Tagcloud(tags, conf['tag_cloud_steps'],
                                       conf['tag_cloud_max_items'],
                                       conf['tag_cloud_start_index'],
                                       conf['tag_cloud_shuffle'])

        return env

    def generate(self, conf, env, data):
        """Creates paged listing by tag."""

        ipp = self.items_per_page
        tt = env.engine.fromfile(self.template)

        for tag in self.tags:

            route = expand(self.path, {'name': tag}).rstrip('/')
            entrylist = [entry for entry in self.tags[tag]]
            paginator = paginate(entrylist, ipp, route, conf['default_orphans'])

            for (next, curr, prev), entries, modified in paginator:

                # e.g.: curr = /page/3, next = /page/2, prev = /page/4

                next = None if next is None \
                else link(u'Next', expand(self.path, {'name': tag}).rstrip('/')) if next == 1 \
                    else link(u'Next', expand(self.pagination, {'name': tag, 'num': next}))

                curr = link(curr, expand(self.path, {'name': tag})) if curr == 1 \
                    else link(expand(self.pagination, {'num': curr, 'name': tag}))

                prev = None if prev is None \
                    else link(u'Previous', expand(self.pagination, {'name': tag, 'num': prev}))

                path = joinurl(conf['output_dir'], curr)

                if isfile(path) and not (modified or tt.modified or env.modified or conf.modified):
                    event.skip('tag', path)
                    continue

                html = tt.render(conf=conf, env=union(env, entrylist=entries,
                                type='tag', prev=prev, curr=curr, next=next, tag=tag,
                                items_per_page=ipp, num_entries=len(entrylist), route=route))

                yield html, path
