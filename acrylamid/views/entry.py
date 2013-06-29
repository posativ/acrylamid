# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import os
import abc
import io

from os.path import isfile, dirname, basename, getmtime, join
from collections import defaultdict

from acrylamid import refs, log
from acrylamid.errors import AcrylamidException
from acrylamid.compat import metaclass, filter
from acrylamid.helpers import expand, union, joinurl, event, link, mkfile

from acrylamid.refs import modified, references
from acrylamid.views import View


class Base(metaclass(abc.ABCMeta, View)):

    priority = 75.0

    @abc.abstractproperty
    def type(self):
        return None

    def init(self, conf, env, template='main.html'):
        self.template = template

    def next(self, entrylist, i):
        return None

    def prev(self, entrylist, i):
        return None

    def generate(self, conf, env, data):

        pathes, entrylist = set(), data[self.type]
        unmodified = not env.modified and not conf.modified

        for i, entry in enumerate(entrylist):

            if entry.hasproperty('permalink'):
                path = joinurl(conf['output_dir'], entry.permalink)
            else:
                path = joinurl(conf['output_dir'], expand(self.path, entry))

            if isfile(path) and path in pathes:
                try:
                    os.remove(path)
                finally:
                    other = [e.filename for e in entrylist
                        if e is not entry and e.permalink == entry.permalink][0]
                    log.error("title collision %s caused by %s and %s",
                              entry.permalink, entry.filename, other)
                    raise SystemExit

            pathes.add(path)
            next, prev = self.next(entrylist, i), self.prev(entrylist, i)

            # per-entry template
            tt = env.engine.fromfile(env, entry.props.get('layout', self.template))

            if all([isfile(path), unmodified, not tt.modified, not entry.modified,
            not modified(*references(entry))]):
                event.skip(self.name, path)
            else:
                html = tt.render(conf=conf, entry=entry, env=union(env,
                                 entrylist=[entry], type=self.__class__.__name__.lower(),
                                 prev=prev, next=next, route=expand(self.path, entry)))
                yield html, path

            # check if any resources need to be moved
            if entry.hasproperty('copy'):
                for res_src in entry.resources:
                    res_dest = join(dirname(path), basename(res_src))
                    # Note, presence of res_src check in FileReader.getresources
                    if isfile(res_dest) and getmtime(res_dest) > getmtime(res_src):
                        event.skip(self.name, res_dest)
                        continue
                    try:
                        fp = io.open(res_src, 'rb')
                        # use mkfile rather than yield so different ns can be specified (and filtered by sitemap)
                        mkfile(fp, res_dest, ns='resource', force=env.options.force, dryrun=env.options.dryrun)
                    except IOError as e:
                        log.warn("Failed to copy resource '%s' whilst processing '%s' (%s)" % (res_src, entry.filename, e.strerror))


class Entry(Base):

    @property
    def type(self):
        return 'entrylist'

    def next(self, entrylist, i):

        if i == 0:
            return None

        refs.append(entrylist[i], entrylist[i - 1])
        return link(entrylist[i-1].title, entrylist[i-1].permalink)

    def prev(self, entrylist, i):

        if i == len(entrylist) - 1:
            return None

        refs.append(entrylist[i], entrylist[i + 1])
        return link(entrylist[i+1].title, entrylist[i+1].permalink)


class Page(Base):

    @property
    def type(self):
        return 'pages'


class Translation(Base):

    @property
    def type(self):
        return 'translations'

    def context(self, conf, env, data):

        translations = defaultdict(list)
        for entry in data['entrylist'][:]:

            if entry.hasproperty('identifier'):
                translations[entry.identifier].append(entry)

                if entry.lang != conf.lang:
                    entry.props['entry_permalink'] = self.path

                    # remove from original entrylist
                    data['entrylist'].remove(entry)
                    data['translations'].append(entry)

        @refs.track
        def translationsfor(entry):

            try:
                entries = translations[entry.identifier]
            except (KeyError, AttributeError):
                raise StopIteration

            for translation in entries:
                if translation != entry:
                    yield translation

        env.translationsfor = translationsfor

        return env


class Draft(Base):
    """Create an drafted post that is not linked by the articles overview or
    regular posts."""

    @property
    def type(self):
        return 'drafts'
