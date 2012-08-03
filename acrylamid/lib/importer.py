# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os
import io
import re
import shutil
import tempfile
import getpass

from base64 import b64encode
from datetime import datetime
from urllib2 import urlopen, Request, HTTPError
from urlparse import urlsplit

from xml.etree import ElementTree
from htmlentitydefs import name2codepoint

from email.utils import parsedate_tz, mktime_tz
from os.path import join, dirname, isfile

from acrylamid import log
from acrylamid.errors import AcrylamidException

from acrylamid.readers import Entry
from acrylamid.helpers import event, escape, system

# no joke
USED_WORDPRESS = False


class InvalidSource(Exception):
    pass


def unescape(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint),
            lambda m: unichr(name2codepoint[m.group(1)]), s)


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
    cmds.insert(0, p) if pandoc else cmds.append(p)

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


def rss20(xml):

    def parse_date_time(stamp):
        ts = parsedate_tz(stamp)
        ts = mktime_tz(ts)
        return datetime.fromtimestamp(ts)

    try:
        tree = ElementTree.fromstring(xml.encode('utf-8'))
    except ElementTree.ParseError:
        raise InvalidSource('no well-formed XML')
    if tree.tag != 'rss' or tree.attrib.get('version') != '2.0':
        raise InvalidSource('no RSS 2.0 feed')

    # --- site settings --- #
    defaults = {'author': None}
    channel = tree.getchildren()[0]

    for k, v in {'title': 'sitename', 'link': 'www_root',
                 'language': 'lang', 'author': 'author'}.iteritems():
        try:
            defaults[v] = channel.find(k).text
        except AttributeError:
            pass

    yield defaults

    # --- individual posts --- #
    for item in channel.findall('item'):

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

        yield {'title': entry['title'],
               'content': entry['content'],
               'date': parse_date_time(entry['date']),
               'link': entry['link']}


def atom(xml):

    def parse_date_time(stamp):
        ts = parsedate_tz(stamp)
        ts = mktime_tz(ts)
        return datetime.fromtimestamp(ts)

    try:
        tree = ElementTree.fromstring(xml.encode('utf-8'))
    except ElementTree.ParseError:
        raise InvalidSource('no well-formed XML')

    if not tree.tag.endswith('/2005/Atom}feed'):
        raise InvalidSource('no Atom feed')

    # --- site settings --- #
    ns = '{http://www.w3.org/2005/Atom}'  # etree Y U have stupid namespace handling?
    defaults = {}

    defaults['title'] = tree.find(ns + 'title').text
    defaults['www_root'] = tree.find(ns + 'id').text
    defaults['author'] = tree.find(ns + 'author').find(ns + 'name').text

    yield defaults

    # --- individual posts --- #
    for item in tree.findall(ns + 'entry'):
        entry = {}

        try:
            entry['title'] = item.find(ns + 'title').text
            entry['date'] = item.find(ns + 'updated').text
            entry['link'] = item.find(ns + 'link').text
            entry['content'] = item.find(ns + 'content').text
        except (AttributeError, TypeError):
            pass

        if item.find(ns + 'content').get('type', 'text') == 'html':
            entry['content'] = unescape(entry['content'])

        if filter(lambda k: not k in entry, ['title', 'date', 'link', 'content']):
            raise AcrylamidException('invalid Atom feed: provide at least title, '
                                     + 'link, content and updated!')

        yield {'title': entry['title'],
               'content': entry['content'],
               'date': datetime.strptime(entry['date'], "%Y-%m-%dT%H:%M:%SZ"),
               'link': entry['link']}


def wp(xml):
    """WordPress to Acrylamid, stolen from pelican-import.py, thank you Alexis.
    -- https://github.com/ametaireau/pelican/blob/master/pelican/tools/pelican_import.py
    """

    global USED_WORDPRESS
    USED_WORDPRESS = True

    from BeautifulSoup import BeautifulStoneSoup
    soup = BeautifulStoneSoup(xml)

    try:
        items = soup.rss.channel.findAll('item')
    except AttributeError:
        raise InvalidSource("no such attribute 'channel'")

    # --- site settings --- #
    title = soup.rss.channel.fetch('title')[0].contents[0]
    www_root = soup.rss.channel.fetch('link')[0].contents[0]

    yield {'title': title, 'www_root': www_root}

    # --- individual posts --- #
    for item in items:
        if item.fetch('wp:status')[0].contents[0] == "publish":

            title = item.title.contents[0]
            link = item.fetch('link')[0].contents[0]

            content = item.fetch('content:encoded')[0].contents[0]
            content = content.replace('\n', '<br />\n')

            raw_date = item.fetch('wp:post_date')[0].contents[0]
            date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")

            author = item.fetch('dc:creator')[0].contents[0].title()
            tags = [tag.contents[0] for tag in item.fetch(domain='post_tag')]

            yield {'title': title, 'content': content, 'date': date, 'author': author,
                   'tags': tags, 'link': link}


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

    failed = []
    for method in (wp, rss20, atom):
        try:
            res = method(content)
            return next(res), res
        except ImportError:
            log.info('notice  BeautifulSoup is required for WordPress import')
        except InvalidSource as e:
            failed.append(e.args[0])
    else:
        raise AcrylamidException('unable to parse source')


def build(conf, env, defaults, items, fmt, keep=False, force=False, pandoc=False, **kw):

    def create(defaults, title, date, author, content, fmt, permalink=None, tags=None):

        global USED_WORDPRESS

        fd, tmp = tempfile.mkstemp(suffix='.txt')
        title = escape(title)

        with io.open(fd, 'w') as f:
            f.write(u'---\n')
            f.write(u'title: %s\n' % title)
            if author != defaults.get('author', None):
                f.write(u'author: %s\n' % author)
            f.write(u'date: %s\n' % date.strftime(conf['date_format']))
            f.write(u'filter: [%s, ]\n' % fmt)
            if tags:
                f.write(u'tags: [%s]\n' % ', '.join(tags))
            if permalink:
                f.write(u'permalink: %s\n' % permalink)
            f.write(u'---\n\n')

            # this are fixes for WordPress because they don't save HTML but a
            # stupid mixed-in form of HTML making it very difficult to get either HTML
            # or reStructuredText/Markdown
            if USED_WORDPRESS and fmt == 'markdown':
                content = content.replace("\n ", "  \n")
            elif USED_WORDPRESS and fmt == 'rst':
                content = content.replace('\n ', '\n\n')
            f.write(content+u'\n')

        entry = Entry(tmp, conf)
        p = join(conf['content_dir'], dirname(entry.permalink)[1:])

        try:
            os.makedirs(p.rsplit('/', 1)[0])
        except OSError:
            pass

        filepath = p + '.txt'
        if isfile(filepath) and not force:
            raise AcrylamidException('Entry already exists %r' % filepath)
        shutil.move(tmp, filepath)
        event.create(filepath)

    for item in items:

        if keep:
            m = urlsplit(item['link'])
            permalink = m.path if m.path != '/' else None

        content, fmt = convert(item.get('content', ''), fmt, pandoc)
        create(defaults, item['title'], item['date'], item.get('author'), content, fmt,
               tags=item.get('tags', None), permalink=permalink if keep else None)

    print "\nImport was successful. Edit your conf.py with these new settings:"
    for key, value in defaults.iteritems():
        print "    %s = '%s'" % (key.upper(), value)


__all__ = ['fetch', 'parse', 'build']
