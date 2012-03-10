#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import os
import re
import tempfile
import subprocess

from base64 import b64encode
from datetime import datetime
from urllib2 import urlopen, Request, HTTPError
from urlparse import urlsplit

from xml.etree import ElementTree
from htmlentitydefs import name2codepoint

from email.utils import parsedate_tz, mktime_tz
from os.path import join, dirname, getmtime, isfile

from acrylamid import log
from acrylamid.utils import FileEntry, event, escapes
from acrylamid.errors import AcrylamidException


class ParseException(Exception):
    pass


def _unescape(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint),
            lambda m: unichr(name2codepoint[m.group(1)]), s)


def _convert(data, fmt='markdown'):
    """Reconversion of HTML to Markdown or reStructuredText.  Defaults to Markdown,
    but can be in fact every format pandoc supports. If pandoc is not available, try
    some specific conversion tools like html2text and html2rest.

    :param html: raw content to convert to
    :param html: format to reconvert to"""

    if fmt in ('Markdown', 'markdown', 'mkdown', 'md', 'mkd'):
        cmds = ['html2text']
        fmt = 'markdown'
    elif fmt in ('rst', 'restructuredtext', 'rest'):
        cmds = ['html2rest']
        fmt = 'rst'
    else:
        cmds = []

    # XXX: cleaner, but does not work within my virtualenv setup.
    #('pandoc', '-f html', '-t', fmt, '--strict')
    #cmds.insert(0, 'pandoc -f html -t %s --strict' % fmt,)
    cmds.insert(0, ['pandoc', '-f', 'html', '-t', fmt, '--strict'])

    if fmt == 'html':
        return data, 'html'

    for cmd in cmds:
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result, err = p.communicate(str(data.decode('utf-8')))
            retcode = p.wait()
            if retcode == 0 and not err:
                return result, fmt.lower()
            log.warn(err.strip())
        except OSError:
            pass
    else:
        return data, 'html'


def _rss20(content):

    def parse_date_time(stamp):
        ts = parsedate_tz(stamp)
        ts = mktime_tz(ts)
        return datetime.fromtimestamp(ts)

    try:
        tree = ElementTree.fromstring(content)
    except ElementTree.ParseError:
        raise AcrylamidException('no well-formed XML')
    if tree.tag != 'rss':
        raise ParseException('no RSS 2.0 feed')

    # --- site settings --- #

    defaults = {}
    channel = tree.getchildren()[0]

    for k, v in {'title': 'sitename', 'link': 'www_root', 'language': 'lang'}.iteritems():
        try:
            defaults[v] = channel.find(k).text
        except AttributeError:
            pass

    # --- individual posts --- #

    items = []
    for item in channel.findall('item'):

        entry = {}
        for k, v in {'title': 'title', 'date': 'pubDate', 'link': 'link',
                     'content': 'description'}.iteritems():
            try:
                entry[k] = item.find(v).text if k != 'content' \
                                             else _unescape(item.find(v).text)
            except AttributeError:
                pass

        try:
            entry['content'] = [_.text for _ in item.getchildren() if _.tag.endswith('encoded')][0]
        except (AttributeError, IndexError) as e:
            pass

        if filter(lambda k: not k in entry, ['title', 'date', 'link', 'content']):
            raise ParseException('invalid RSS 2.0 feed: provide at least a title, '
                                 + 'link, content and pubDate!')

        items.append({
            'title': entry['title'],
            'content': entry['content'],
            'date': parse_date_time(entry['date']),
            'link': entry['link']
            })

    return defaults, items


def fetch(url, auth=None):
    """Fetch URL, optional with HTTP Basic Authentication."""

    if not (url.startswith('http://') or url.startswith('https://')):
        try:
            with open(url, 'r') as fp:
                content = fp.read()
            return content
        except OSError as e:
            raise AcrylamidException(e.message)

    req = Request(url)
    if auth:
        request.add_header('Authorization', 'Basic ' + b64encode(auth))

    try:
        r = urlopen(req)
    except HTTPError as e:
        raise AcrylamidException(e.msg)
    if r.getcode() != 200:
        raise AcrylamidException('invalid status code %i, aborting.' % r.getcode())
    return r.read()


def parse(content):

    for method in (_rss20,):
        try:
            return method(content)
        except ValueError as e:
            raise AcrylamidException(e.message)
        except ParseException:
            pass
    else:
        raise AcrylamidException('unable to parse feed.')


def build(conf, env, defaults, items, fmt, keep=False):

    def create(title, date, content, permalink=None):
        fd, tmp = tempfile.mkstemp(suffix='.txt', dir='.cache/')
        title = escapes(title)

        with os.fdopen(fd, 'wb') as f:
            f.write('---\n')
            f.write('title: %s\n' % title)
            f.write('date: %s\n' % date.strftime(conf['date_format']))
            f.write('filter: [%s, ]\n' % fmt)
            if permalink:
                f.write('permalink: %s\n' % permalink)
            f.write('---\n\n')
            f.write(content[0])

        entry = FileEntry(tmp, conf)
        p = join(conf['entries_dir'], dirname(entry.permalink)[1:])

        try:
            os.makedirs(p.rsplit('/', 1)[0])
        except OSError:
            pass

        filepath = p + '.txt'
        if isfile(filepath):
            raise AcrylamidException('Entry already exists %r' % filepath)
        os.rename(tmp, filepath)
        event.create(title, filepath)

    for item in items:

        if keep:
            m = urlsplit(item['link'])
            permalink = m.path if m.path != '/' else None

        create(item['title'], item['date'], _convert(item['content'], fmt),
               permalink=permalink if keep else None)
