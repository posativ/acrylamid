# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os
import abc

from os.path import isfile
from collections import defaultdict

from acrylamid.views import View
from acrylamid.helpers import expand, union, joinurl, event, link, memoize, md5
from acrylamid.errors import AcrylamidException


class Base(View):

    __metaclass__ = abc.ABCMeta

    priority = 75.0

    @abc.abstractproperty
    def type(self):
        return None

    def init(self, template='main.html'):
        self.template = template

    def next(self, entrylist, i):
        return None

    def prev(self, entrylist, i):
        return None

    def has_changed(self, entrylist, salt):
        return False

    def generate(self, request):

        tt = self.env.engine.fromfile(self.template)
        pathes = set()

        nondrafts, drafts = [], []
        for entry in request[self.type]:
            if not entry.draft:
                nondrafts.append(entry)
            else:
                drafts.append(entry)

        for isdraft, entrylist in enumerate([nondrafts, drafts]):
            has_changed = self.has_changed(entrylist, 'draft' if isdraft else 'entry')

            for i, entry in enumerate(entrylist):

                if entry.hasproperty('permalink'):
                    path = joinurl(self.conf['output_dir'], entry.permalink)
                else:
                    path = joinurl(self.conf['output_dir'], expand(self.path, entry))

                if path.endswith('/'):
                    path = joinurl(path, 'index.html')

                if isfile(path) and path in pathes:
                    try:
                        os.remove(path)
                    finally:
                        f = lambda e: e is not entry and e.permalink == entry.permalink
                        raise AcrylamidException("title collision %r in %r with %r." %
                            (entry.permalink, entry.filename, filter(f, entrylist)[0].filename))

                pathes.add(path)
                next = self.next(entrylist, i) if not isdraft else None
                prev = self.prev(entrylist, i) if not isdraft else None

                if isfile(path) and not any([has_changed, entry.has_changed, tt.has_changed]):
                    event.skip(path)
                    continue

                route = expand(self.path, entry)
                html = tt.render(conf=self.conf, entry=entry, env=union(self.env,
                                 entrylist=[entry], type=self.__class__.__name__.lower(),
                                 prev=prev, next=next, route=route))

                yield html, path


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

    def has_changed(self, entrylist, salt):
        # detect changes in prev and next
        hv = md5(*entrylist, attr=lambda e: e.permalink)

        if memoize(salt + '-permalinks') != hv:
            memoize(salt +'-permalinks', hv)
            return True
        return False

    def next(self, entrylist, i):
        return None if i == 0 else link(u"« " + entrylist[i-1].title,
            entrylist[i-1].permalink.rstrip('/'), entrylist[i-1])

    def prev(self, entrylist, i):
        return None if i == len(entrylist) - 1 else link(entrylist[i+1].title + u" »",
            entrylist[i+1].permalink.rstrip('/'), entrylist[i+1])


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

    def context(self, env, request):

        translations = defaultdict(list)
        for entry in request['entrylist'][:]:

            if entry.hasproperty('identifier'):
                translations[entry.identifier].append(entry)

                if entry.lang != self.conf.lang:
                    entry.props['entry_permalink'] = self.path

                    # remove from original entrylist
                    request['entrylist'].remove(entry)
                    request['translations'].append(entry)

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
