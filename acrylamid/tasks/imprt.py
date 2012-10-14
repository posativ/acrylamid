# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os
import io
import re
import sys
import shutil
import tempfile
import getpass

from base64 import b64encode
from datetime import datetime
from urllib2 import urlopen, Request, HTTPError
from urlparse import urlsplit

from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

from email.utils import parsedate_tz, mktime_tz
from os.path import join, dirname, isfile

from acrylamid import log, commands
from acrylamid.tasks import task, argument
from acrylamid.errors import AcrylamidException

from acrylamid.readers import Entry
from acrylamid.helpers import event, safe, system
from acrylamid.lib.html import unescape

arguments = [
    argument("src", metavar="FILE|URL"),
    argument("-f", "--force", dest="force", action="store_true",
        help="overwrite existing entries", default=False),
    argument("-m", dest="fmt", default="Markdown",
        help="reconvert HTML to FMT"),
    argument("-k", "--keep-links", dest="keep", action="store_true",
        help="keep permanent links", default=False),
    argument("-p", "--pandoc", dest="pandoc", action="store_true",
        help="use pandoc first", default=False),
    argument("-a", dest="args", nargs="+", action="store", type=str,
    help="add argument to header section", default=[]),
]

if sys.version_info < (2, 7):
    setattr(ElementTree, 'ParseError', ExpatError)

# no joke
USED_WORDPRESS = False


class InputError(Exception):
    pass


def convert(data, fmt='markdown', pandoc=False):
    """Reconversion of HTML to Markdown or reStructuredText.  Defaults to Markdown,
    but can be in fact every format pandoc supports. If pandoc is not available, try
    some specific conversion tools like html2text and html2rest.

    :param html: raw content to convert to
    :param html: format to reconvert to"""

    if fmt in ('Markdown', 'markdown', 'mkdown', 'md', 'mkd'):
        cmds = ['html2text']
        fmt = 'markdown'
    elif fmt in ('rst', 'restructuredtext', 'rest', 'reStructuredText'):
        cmds = ['html2rest']
        fmt = 'rst'
    else:
        cmds = []

    p = ['pandoc', '--normalize', '-f', 'html', '-t', fmt, '--strict', '--no-wrap']
    cmds.insert(0, p) if pandoc or fmt == 'rst' else cmds.append(p)

    if fmt == 'html':
        return data, 'html'

    #  - item.find(foo).text returns None if no CDATA
    #  - pandoc waits for input if a zero-length string is given
    if data is None or data is '':
        return '', fmt

    for cmd in cmds:
        try:
            return system(cmd, stdin=data), fmt.lower()
        except AcrylamidException as e:
            log.warn(e.args[0])
        except OSError:
            pass
    else:
        return data, 'html'


def rss(xml):

    if 'xmlns:wp' in xml:
        raise InputError('WordPress dump')

    def parse_date_time(stamp):
        ts = parsedate_tz(stamp)
        ts = mktime_tz(ts)
        return datetime.fromtimestamp(ts)

    def generate(item):

        entry = {}
        for k, v in {'title': 'title', 'date': 'pubDate', 'link': 'link',
                     'content': 'description'}.iteritems():
            try:
                entry[k] = item.find(v).text if k != 'content' \
                                             else unescape(item.find(v).text)
            except (AttributeError, TypeError):
                pass

        if filter(lambda k: not k in entry, ['title', 'date', 'link', 'content']):
            raise AcrylamidException('invalid RSS 2.0 feed: provide at least title, ' \
                                     + 'link, content and pubDate!')

        return {'title': entry['title'],
               'content': entry['content'],
               'date': parse_date_time(entry['date']),
               'link': entry['link'],
               'tags': [cat.text for cat in item.findall('category')]}

    try:
        tree = ElementTree.fromstring(xml.encode('utf-8'))
    except ElementTree.ParseError:
        raise InputError('no well-formed XML')
    if tree.tag != 'rss' or tree.attrib.get('version') != '2.0':
        raise InputError('no RSS 2.0 feed')

    defaults = {'author': None}
    channel = tree.getchildren()[0]

    for k, v in {'title': 'sitename', 'link': 'www_root',
                 'language': 'lang', 'author': 'author'}.iteritems():
        try:
            defaults[v] = channel.find(k).text
        except AttributeError:
            pass

    return defaults, map(generate, channel.findall('item'))

    try:
        tree = ElementTree.fromstring(xml.encode('utf-8'))
    except ElementTree.ParseError:
        raise InputError('no well-formed XML')
    if tree.tag != 'rss' or tree.attrib.get('version') != '2.0':
        raise InputError('no RSS 2.0 feed')

    defaults = {'author': None}
    channel = tree.getchildren()[0]

    for k, v in {'title': 'sitename', 'link': 'www_root',
                 'language': 'lang', 'author': 'author'}.iteritems():
        try:
            defaults[v] = channel.find(k).text
        except AttributeError:
            pass

    return defaults, map(generate, channel.findall('item'))


def atom(xml):

    def parse_date_time(stamp):
        ts = parsedate_tz(stamp)
        ts = mktime_tz(ts)
        return datetime.fromtimestamp(ts)

    def generate(item):

        entry = {}

        try:
            entry['title'] = item.find(ns + 'title').text
            entry['date'] = item.find(ns + 'updated').text
            entry['link'] = item.find(ns + 'link').text
            entry['content'] = item.find(ns + 'content').text
        except (AttributeError, TypeError):
            raise AcrylamidException('invalid Atom feed: provide at least title, '
                                     + 'link, content and updated!')

        if item.find(ns + 'content').get('type', 'text') == 'html':
            entry['content'] = unescape(entry['content'])

        return {'title': entry['title'],
               'content': entry['content'],
               'date': datetime.strptime(entry['date'], "%Y-%m-%dT%H:%M:%SZ"),
               'link': entry['link'],
               'tags': [x.get('term') for x in item.findall(ns + 'category')]}

    try:
        tree = ElementTree.fromstring(xml.encode('utf-8'))
    except ElementTree.ParseError:
        raise InputError('no well-formed XML')

    if not tree.tag.endswith('/2005/Atom}feed'):
        raise InputError('no Atom feed')

    ns = '{http://www.w3.org/2005/Atom}'  # etree Y U have stupid namespace handling?
    defaults = {}

    defaults['sitename'] = tree.find(ns + 'title').text
    defaults['author'] = tree.find(ns + 'author').find(ns + 'name').text

    www_root = [a for a in tree.findall(ns + 'link')
        if a.attrib.get('rel', 'alternate') == 'alternate']
    if www_root:
         defaults['www_root'] = www_root[0].attrib.get('href')

    return defaults, map(generate, tree.findall(ns + 'entry'))


def wordpress(xml):
    """WordPress to Acrylamid, inspired by the Astraeus project."""

    if 'xmlns:wp' not in xml:
        raise InputError('not a WP dump')

    global USED_WORDPRESS
    USED_WORDPRESS = True

    def generate(item):

        entry = {
            'title': item.find('title').text,
            'link': item.find('link').text,

            'content': item.find('%sencoded' % cons).text.replace('\n', '<br />\n'),
            'date': datetime.strptime(item.find('%spost_date' % wpns).text,
                "%Y-%m-%d %H:%M:%S"),

            'author': item.find('%screator' % dcns).text,
            'tags': [tag.text for tag in item.findall('category')]
        }

        if item.find('%spost_type' % wpns).text == 'page':
            entry['type'] = 'page'

        if item.find('%sstatus' % wpns).text != 'publish':
            entry['draft'] = True

        return entry

    try:
        tree = ElementTree.fromstring(xml.encode('utf-8'))
    except ElementTree.ParseError:
        raise InputError('no well-formed XML')

    # wordpress name spaces
    wpns = '{http://wordpress.org/export/1.1/}'
    dcns = '{http://purl.org/dc/elements/1.1/}'
    cons = '{http://purl.org/rss/1.0/modules/content/}'

    defaults = {
        'title': tree.find('channel/title').text,
        'www_root': tree.find('channel/link').text
    }

    return defaults, map(generate, tree.findall('channel/item'))


def fetch(url, auth=None):
    """Fetch URL, optional with HTTP Basic Authentication."""

    if not (url.startswith('http://') or url.startswith('https://')):
        try:
            with io.open(url, 'r', encoding='utf-8', errors='replace') as fp:
                return u''.join(fp.readlines())
        except OSError as e:
            raise AcrylamidException(e.args[0])

    req = Request(url)
    if auth:
        req.add_header('Authorization', 'Basic ' + b64encode(auth))

    try:
        r = urlopen(req)
    except HTTPError as e:
        raise AcrylamidException(e.msg)

    if r.getcode() == 401:
        user = raw_input('Username: ')
        passwd = getpass.getpass()
        fetch(url, user + ':' + passwd)
    elif r.getcode() == 200:
        try:
            enc = re.search('charset=(.+);?', r.headers.get('Content-Type', '')).group(1)
        except AttributeError:
            enc = 'utf-8'
        return u'' + r.read().decode(enc)

    raise AcrylamidException('invalid status code %i, aborting.' % r.getcode())


def parse(content):

    for method in (atom, rss, wordpress):
        try:
            return method(content)
        except InputError:
            pass
    else:
        raise AcrylamidException('unable to parse source')


def build(conf, env, defaults, items, options):

    def create(defaults, item):

        global USED_WORDPRESS
        fd, tmp = tempfile.mkstemp(suffix='.txt')

        with io.open(fd, 'w') as f:
            f.write(u'---\n')
            f.write(u'title: %s\n' % safe(item['title']))
            if item.get('author') != defaults.get('author'):
                f.write(u'author: %s\n' % (item.get('author') or defaults.get('author')))
            f.write(u'date: %s\n' % item['date'].strftime(conf['date_format']))
            f.write(u'filter: %s\n' % item['filter'])
            if 'tags' in item:
                f.write(u'tags: [%s]\n' % ', '.join(item['tags']))
            if 'permalink' in item:
                f.write(u'permalink: %s\n' % item['permalink'])
            for arg in options.args:
                f.write(arg.strip() + u'\n')
            f.write(u'---\n\n')

            # this are fixes for WordPress because they don't save HTML but a
            # stupid mixed-in form of HTML making it very difficult to get either HTML
            # or reStructuredText/Markdown
            if USED_WORDPRESS and item['filter'] == 'markdown':
                item['content'] = item['content'].replace("\n ", "  \n")
            elif USED_WORDPRESS and item['filter'] == 'rst':
                item['content'] = item['content'].replace('\n ', '\n\n')
            f.write(item['content']+u'\n')

        entry = Entry(tmp, conf)
        p = join(conf['content_dir'], dirname(entry.permalink)[1:])

        try:
            os.makedirs(p.rsplit('/', 1)[0])
        except OSError:
            pass

        filepath = p + '.txt'
        if isfile(filepath) and not options.force:
            raise AcrylamidException('Entry already exists %r' % filepath)
        shutil.move(tmp, filepath)
        event.create(filepath)

    for item in filter(lambda x: x, items):

        if options.keep:
            m = urlsplit(item['link'])
            item['permalink'] = m.path if m.path != '/' else None

        item['content'], item['filter'] = convert(item.get('content', ''),
            options.fmt, options.pandoc)

        create(defaults, item)

    print "\nImport was successful. Edit your conf.py with these new settings:"
    for key, value in defaults.iteritems():
        if value is None:
            continue
        print "    %s = '%s'" % (key.upper(), value)


@task("import", arguments, "import content from URL or FILE")
def run(conf, env, options):
    """Subcommand: import -- import entries and settings from an existing RSS/Atom
    feed or WordPress dump.  ``acrylamid import http://example.com/feed/`` or any
    local FILE is fine.

    By default we use ``html2text`` (if available) to re-convert to Markdown, with
    ``-m rst`` you can also re-convert to reST if you have ``html2rest`` installed.
    As fallback there we have ``pandoc`` but you can use pandoc as first choice with
    the ``-p`` flag.

    If you don't like any reconversion, simply use ``-m html``. This command supports
    the force flag to override already existing files. Use with care!"""

    # we need the actual defaults values for permalink format
    commands.initialize(conf, env)

    content = fetch(options.src, auth=options.__dict__.get('auth', None))
    defaults, items = parse(content)
    build(conf, env, defaults, items, options)
