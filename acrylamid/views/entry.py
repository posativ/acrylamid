# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import os
import abc
import io

from os.path import isfile, dirname, basename, getmtime, join
from collections import defaultdict

from acrylamid import refs, log, locale
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

    def render(self, tt, conf, env, entry, **kwargs):
        return tt.render(conf=conf, env=union(env,
            type=self.__class__.__name__.lower(),
            entrylist=[entry], **kwargs))

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
                html = self.render(tt, conf, env, entry,
                    prev=prev, next=next, route=expand(self.path, entry))
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
    """Creates single full-length entry
    (`Example <http://blog.posativ.org/2012/nginx/>`_).

    To enable Entry view, add this to your :doc:`conf.py`:

    .. code-block:: python

        '/:year/:slug/': {
            'view': 'entry',
            'template': 'main.html'  # default, includes entry.html
        }

    The entry view renders an post to a unique location and should be used as
    permalink URL. The url is user configurable, but may be overwritten by
    setting ``ENTRY_PERMALINK`` explicitly to a URL in your configuration.

    This view takes no other arguments and uses *main.html* and *entry.html* as
    template."""

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
    """Creates a static page

    To enable Entry view, add this to your :doc:`conf.py`:

    .. code-block:: python

        '/:year/:slug/': {
            'view': 'page',
            'template': 'main.html'  # default, includes entry.html
        }

    The page view renders an post to a unique location withouth any references
    to other blog entries. The url is user configurable, but may be overwritten by
    setting ``PAGE_PERMALINK`` explicitly to a URL in your configuration.

    This view takes no other arguments and uses *main.html* and *entry.html* as
    template."""

    @property
    def type(self):
        return 'pages'


class Translation(Base):
    """Creates translation of a single full-length entry.  To enable the
    Translation view, add this to your :doc:`conf.py`:

    .. code-block:: python

        '/:year/:slug/:lang/': {
            'view': 'translation',
            'template': 'main.html',  # default, includes entry.html
        }

    Translations are posts with the same `identifier` and a different `lang` attribute.
    An example:

    The English article::

        ---
        title: Foobar is not dead
        identifier: foobar-is-not-dead
        ---

        That's true, foobar is still alive!

    And the French version::

        ---
        title: Foobar n'est pas mort !
        identifier: foobar-is-not-dead
        lang: fr
        ---

        Oui oui, foobar est toujours vivant !

    If the blog language is ``"en"`` then the english article will be included into
    the default listing but the french version not. You can link to the translated
    versions via:

    .. code-block:: html+jinja

        {% if 'translation' in env.views and env.translationsfor(entry) %}
        <ul>
            {% for tr in env.translationsfor(entry) %}
                <li><strong>{{ tr.lang }}:</strong>
                    <a href="{{ env.path ~ tr.permalink }}">{{ tr.title }}</a>
                </li>
            {% endfor %}
        </ul>
        {% endif %}"""

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

    def render(self, tt, conf, env, entry, **kwargs):
        with locale.context(entry.lang):
            return super(Translation, self).render(tt, conf, env, entry, **kwargs)


class Draft(Base):
    """Create an drafted post that is not linked by the articles overview or
    regular posts."""

    @property
    def type(self):
        return 'drafts'
