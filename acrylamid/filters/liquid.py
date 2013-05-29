# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import io
import re
import json
import pickle

from os.path import join
from functools import partial

from acrylamid import core, utils, lib
from acrylamid.compat import PY2K, iteritems, text_type as str

from acrylamid.core import cache
from acrylamid.utils import Struct
from acrylamid.filters import Filter

from acrylamid.lib import requests

if PY2K:
    from urllib import urlencode
    from urlparse import urlparse, parse_qs
    import cPickle as pickle
else:
    from urllib.parse import urlencode
    from urllib.parse import urlparse, parse_qs

__img_re = r'(?P<class>\S.*\s+)?(?P<src>(?:https?:\/\/|\/|\S+\/)\S+)(?:\s+(?P<width>\d+))?(?:\s+(?P<height>\d+))?(?P<title>\s+.+)?'
__img_re_title = r'(?:"|\')(?P<title>[^"\']+)?(?:"|\')\s+(?:"|\')(?P<alt>[^"\']+)?(?:"|\')'


def blockquote(header, body):
    """Mimic Octopress's blockquote plugin. See
    http://octopress.org/docs/plugins/blockquote/ for examples."""

    # TODO: use python-titlecase if available or use this implementation:
    #       https://github.com/imathis/octopress/blob/master/plugins/titlecase.rb

    def paragraphize(text):
        return '<p>' + text.strip().replace('\n\n', '</p><p>').replace('\n', '<br/>') + '</p>'

    by, source, title = None, None, None

    m = re.match(r'(\S.*)\s+(https?:\/\/)(\S+)\s+(.+)', header, flags=re.I)
    if m:
        by = m.group(1)
        source = m.group(2) + m.group(3)
        title = m.group(4)  # titlecase
    else:
        m = re.match(r'(\S.*)\s+(https?:\/\/)(\S+)', header, re.I)
        if m:
            by = m.group(1)
            source = m.group(2) + m.group(3)
        else:
            m = re.match(r'([^,]+),([^,]+)', header)
            if m:
                by = m.group(1)
                title = m.group(2)  # titlecase
            else:
                m = re.match(r'(.+)', header)
                if m:
                    by = m.group(1)

    quote = paragraphize(body)
    author = '<strong>%s</strong>' % (by.strip() or '')

    if source:
        url = re.match(r'https?:\/\/(.+)', source).group(1)
        parts = []
        for part in url.split('/'):
            if not part or len('/'.join(parts + [part])) >= 32:
                break
            parts.append(part)
        else:
            parts.append('&hellip;')

        href = '/'.join(parts)

    if source:
        cite = ' <cite><a href="%s">%s</a></cite>' % (source, (title or href))
    elif title:
        cite = ' <cite>%s</cite>' % title

    if not author:
        blockquote = quote
    elif cite:
        blockquote = quote + "<footer>%s</footer>" % (author + cite)
    else:
        blockquote = quote + "<footer>%s</footer>" % author

    return "<blockquote>%s</blockquote>" % blockquote


def img(header, body=None):
    """Alternate to Markdown's image tag. See
    http://octopress.org/docs/plugins/image-tag/ for usage."""

    attrs = re.match(__img_re, header).groupdict()
    m = re.match(__img_re_title, attrs['title'])

    if m:
        attrs['title'] = m.groupdict()['title']
        attrs['alt'] = m.groupdict()['alt']
    elif 'title' in attrs:
        attrs['alt'] = attrs['title'].replace('"', '&#34')

    if 'class' in attrs:
        attrs['class'] = attrs['class'].replace('"', '')

    if attrs:
        return '<img ' + ' '.join('%s="%s"' % (k, v) for k, v in iteritems(attrs) if v) + ' />'
    return ("Error processing input, expected syntax: "
            "{% img [class name(s)] [http[s]:/]/path/to/image [width [height]] "
            "[title text | \"title text\" [\"alt text\"]] %}")


def youtube(header, body=None):

    # TODO add options similar to rstx_youtube directive

    if header.startswith(('http://', 'https://')):
        header = parse_qs(urlparse(header).query)['v'][0]

    return '<div class="video">' + \
                '<iframe src="http://www.youtube.com/embed/%s"></iframe>' % header + \
           '</div>'


def pullquote(header, body):
    """Semantic pullquote using CSS only. Defaults to right alignment. See
    http://octopress.org/docs/plugins/pullquote/ for details."""

    # TODO support a markup language somehow

    align = 'left' if 'left' in header.lower() else 'right'
    m = re.search(r'{"\s*(.+?)\s*"}', body, re.MULTILINE | re.DOTALL)

    if m:
        return '<span class="pullquote-{0}" data-pullquote="{1}">{2}</span>'.format(
            align, m.group(1), re.sub(r'\{"\s*|\s*"\}', '', body))
    return "Surround your pullquote like this {\" text to be quoted \"}"


def tweet(header, body=None):
    """Easy embedding of Tweets. The Twitter oEmbed API is rate-limited,
    hence we are caching the response per configuration to `.cache/`."""

    oembed = 'https://api.twitter.com/1/statuses/oembed.json'
    args = list(map(str.strip, re.split(r'\s+', header)))

    params = Struct(url=args.pop(0))
    for arg in args:
        k, v = list(map(str.strip, arg.split('=')))
        if k and v:
            v = v.strip('\'')
        params[k] = v

    try:
        with io.open(join(core.cache.cache_dir, 'tweets'), 'rb') as fp:
            cache = pickle.load(fp)
    except (IOError, pickle.PickleError):
        cache = {}

    if params in cache:
        body = cache[params]
    else:
        try:
            body = json.loads(requests.get(oembed + '?' + urlencode(params)).read())['html']
        except (requests.HTTPError, requests.URLError):
            log.exception('unable to fetch tweet')
            body = "Tweet could not be fetched"
        except (ValueError, KeyError):
            log.exception('could not parse response')
            body = "Tweet could not be processed"
        else:
            cache[params] = body

    try:
        with io.open(join(core.cache.cache_dir, 'tweets'), 'wb') as fp:
            pickle.dump(cache, fp, pickle.HIGHEST_PROTOCOL)
    except (IOError, pickle.PickleError):
        log.exception('uncaught exception during pickle.dump')

    return "<div class='embed tweet'>%s</div>" % body


class Liquid(Filter):

    match = [re.compile('^(liquid|octopress)$', re.I)]
    priority = 80.0

    directives = {
        'blockquote': blockquote, 'pullquote': pullquote,
        'img': img, 'tweet': tweet,
        'youtube': youtube
    }

    def block(self, tag):
        return re.compile(''.join([
            r'{%% %s (.*?) ?%%}' % tag,
            '(?:',
                '\n(.+?)\n',
                r'{%% end%s %%}' % tag,
            ')?']), re.MULTILINE | re.DOTALL)

    def transform(self, text, entry, *args):

        for tag, func in iteritems(self.directives):
            text = re.sub(self.block(tag), lambda m: func(*m.groups()), text)

        return text
