# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py
#
# -*- encoding: utf-8 -*-

import math
import random

from os.path import exists
from collections import defaultdict

from acrylamid.views import View
from acrylamid.utils import union, joinurl, safeslug, event, paginate, expand


class Tagcloud:
    """Tagcloud helper class similar (almost identical) to pelican's tagcloud helper object.
    Takes a bunch of tags and produces a logarithm-based partition and returns a iterable
    object yielding a Tag-object with two attributes: name and step where step is the
    calculated step size (== font size) and reaches from 0 to steps-1.

    :param tags: a dictionary of tags, e.g. {'name', [list of entries]}
    :param steps: maximum steps
    :param max_items: maximum items shown in tagcloud
    :param start: start index of steps resulting in start to steps+start-1 steps."""

    def __init__(self, tags, steps=4, max_items=100, start=0, shuffle=False):

        lst = sorted([(k, len(v)) for k, v in tags.iteritems()], key=lambda k: k[1],
                  reverse=True)[:max_items]
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


class Tag(View):

    def init(self, items_per_page=25, pagination='/tag/:name/:num/'):
        self.items_per_page = items_per_page
        self.pagination = pagination

    def context(self, env, request):

        class Link:

            def __init__(self, title, href):
                self.title = title
                self.href = href if href.endswith('/') else href + '/'

        def tagify(tags):
            href = lambda t: expand(self.path, {'name': safeslug(t)})
            return [Link(t, href(t)) for t in tags]

        tags = defaultdict(list)
        for e in request['entrylist']:
            for tag in e.tags:
                tags[tag].append(e)

        env['tag_cloud'] = Tagcloud(tags, self.conf['tag_cloud_steps'],
                                          self.conf['tag_cloud_max_items'],
                                          self.conf['tag_cloud_start_index'],
                                          self.conf.get('tag_cloud_shuffle', False))
        self.env['tt_env'].filters['safeslug'] = safeslug
        self.env['tt_env'].filters['tagify'] = tagify

        self.tags = {}
        for k, v in tags.iteritems():
            self.tags[safeslug(k)] = v

        return env

    def generate(self, request):
        """Creates paged listing by tag."""

        entrylist = request['entrylist']
        ipp = self.items_per_page

        tt_entry = self.env['tt_env'].get_template('entry.html')
        tt_main = self.env['tt_env'].get_template('main.html')

        for tag in self.tags:
            entrylist = [entry for entry in self.tags[tag]]
            for i, entries, has_changed in paginate(entrylist, ipp, lambda e: not e.draft, salt=tag):
                # e.g.: curr = /page/3, next = /page/2, prev = /page/4
                if i == 0:
                    next = None
                    curr = expand(self.path, {'name': tag})
                else:
                    curr = expand(self.pagination, {'num': str(i+1), 'name': tag})
                    next = expand(self.path, {'name': tag}) if i==1 \
                             else expand(self.pagination, {'name': tag, 'num': str(i)})

                prev = None if i >= len(list(entries))-1 \
                            else expand(self.pagination, {'name': tag, 'num': str(i+2)})
                p = joinurl(self.conf['output_dir'], curr, 'index.html')

                if exists(p) and not  bool(filter(lambda e: e.has_changed, entries)):
                    if not (tt_entry.has_changed or tt_main.has_changed):
                        event.skip(curr, path=p)
                        continue

                html = tt_main.render(conf=self.conf, env=union(self.env, entrylist=entries,
                                      type='tag', prev=prev, curr=curr, next=next,
                                      items_per_page=ipp, num_entries=len(entrylist)))

                yield html, p, curr
