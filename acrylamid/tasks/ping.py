# -*- encoding: utf-8 -*-
#
# Copyrights:
#    - PingBack: Иван Сагалаев (Ivan Sagalaew) <maniac@softwaremaniacs.org>
#    - Other: posativ <info@posativ.org>
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import re
from urlparse import urlparse

from acrylamid.tasks import task, argument

from acrylamid.utils import filelist
from acrylamid.errors import AcrylamidException
from acrylamid.readers import Entry
from acrylamid.helpers import memoize, joinurl
from acrylamid.commands import initialize

from acrylamid.lib.requests import head, URLError, HTTPError

arguments = [
    argument("-", "--all", dest="all", action="store_true", default=False,
        help="ping all entries (default: only new)"),
]


def pingback(src, dest):
    """Makes a pingback request to dest on behalf of src, i.e. effectively
    saying to dest that "the page at src is linking to you"."""

    def search_link(content):
        match = re.search(r'<link rel="pingback" href="([^"]+)" ?/?>', content)
        return match and match.group(1)

    request_url = 'http:%s' % dest if dest.startswith('//') else dest

    try:
        info = head(request_url).info()
    except (URLError, HTTPError) as e:
        raise AcrylamidException(e.args[0])

    try:
        server_url = info.get('X-Pingback', '') or search_link(f.read(512 * 1024))
        if server_url:
            server = xmlrpclib.ServerProxy(server_url)
            server.pingback.ping(src, dest)
    except xmlrpclib.ProtocolError as e:
        raise AcrylamidException(e.args[0])


@task('ping', arguments, "notify ressources")
def run(conf, env, options):
    """Subcommand: ping -- notify external ressources via Pingback etc."""

    initialize(conf, env)  # we access the cache, so we must initialize first

    entrylist = sorted([Entry(e, conf) for e in filelist(conf['content_dir'],
        conf.get('entries_ignore', []))], key=lambda k: k.date, reverse=True)
    entrylist = [entry for entry in entrylist if not entry.draft]

    print joinurl(conf['www_root'], entrylist[0].permalink)

    links = re.findall('https?://[^ ]+', entrylist[0].source)
    print links
    # if not options.all:

    # last = memoize('ping-last')
    # if last is None:
    #   if raw_
