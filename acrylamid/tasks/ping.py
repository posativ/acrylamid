# -*- encoding: utf-8 -*-
#
# Copyrights:
#    - PingBack: Иван Сагалаев (Ivan Sagalaew) <maniac@softwaremaniacs.org>
#    - Other: posativ <info@posativ.org>
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import re
import os
import json
import xmlrpclib

from textwrap import wrap
from urlparse import urlparse

from acrylamid.tasks import task, argument
from acrylamid.errors import AcrylamidException
from acrylamid.colors import blue, green, bold

from acrylamid import readers, commands, helpers, log
from acrylamid.tasks.info import option
from acrylamid.lib.requests import head, URLError, HTTPError
from acrylamid.lib.async import Threadpool

try:
    import twitter
except ImportError:
    twitter = None  # NOQA

arguments = [
    argument("service", nargs="?", type=str, choices=["twitter", "back"],
        default="back", help="ping service (default: back)"),

    argument("-a", "--all", dest="all", action="store_true", default=False,
        help="ping all entries (default: only the newest)"),
    argument("-p", dest="file", type=str, default=None, help="ping specific article"),

    argument("-n", "--dry-run", dest="dryrun", action='store_true',
             help="show what would have been pingbacked", default=False),
    argument("-j", "--jobs", dest="jobs", type=int, default=10, help="N parallel requests"),
] + [option(i) for i in range(10)]


def pingback(src, dest, dryrun=False):
    """Makes a pingback request to dest on behalf of src, i.e. effectively
    saying to dest that "the page at src is linking to you"."""

    def search_link(content):
        match = re.search(r'<link rel="pingback" href="([^"]+)" ?/?>', content)
        return match and match.group(1)

    try:
        r = head(dest)
    except (URLError, HTTPError) as e:
        return

    try:
        server_url = r.info().get('X-Pingback', '') or search_link(r.read(512 * 1024))
        if server_url:

            print "Pingback", blue(urlparse(server_url).netloc),
            print "from", green(''.join(urlparse(src)[1:3])) + "."

            if not dryrun:
                server = xmlrpclib.ServerProxy(server_url)
                server.pingback.ping(src, dest)

    except xmlrpclib.ProtocolError as e:
        raise AcrylamidException(e.args[0])


def tweet(entry, conf, dryrun=False):
    """Send a tweet with the title, link and tags from an entry. The first time you
    need to authorize Acrylamid but than it works without any interaction."""

    key = "6k00FRe6w4SZfqEzzzyZVA"
    secret = "fzRfQcqQX4gcZziyLeoI5wSbnFb7GGj2oEh10hnjPUo"

    creds = os.path.expanduser('~/.twitter_oauth')
    if not os.path.exists(creds):
        twitter.oauth_dance("Acrylamid", key, secret, creds)

    oauth_token, oauth_token_secret = twitter.read_token_file(creds)
    t = twitter.Twitter(auth=twitter.OAuth(oauth_token, oauth_token_secret, key, secret))

    tweet = u"New Blog Entry: {0} {1} {2}".format(entry.title,
        helpers.joinurl(conf['www_root'], entry.permalink),
        ' '.join([u'#' + helpers.safeslug(tag) for tag in entry.tags]))

    print '     ', bold(blue("tweet ")),
    print '\n'.join(wrap(tweet.encode('utf8'), subsequent_indent=' '*13))

    if not dryrun:
        try:
            t.statuses.update(status=tweet.encode('utf8'))
        except twitter.api.TwitterError as e:
            try:
                log.warn("%s" % json.loads(e.response_data)['error'])
            except (ValueError, TypeError):
                log.warn("Twitter: something went wrong...")


@task('ping', arguments, "notify ressources")
def run(conf, env, options):
    """Subcommand: ping -- notify external ressources via Pingback etc."""

    commands.initialize(conf, env)
    entrylist = [entry for entry in readers.load(conf)[0] if not entry.draft]

    if options.file:
        try:
            entrylist = [filter(lambda e: e.filename == options.file, entrylist)[0]]
        except IndexError:
            raise AcrylamidException("no such post!")

    if options.service == 'twitter':

        if twitter is None:
            raise AcrylamidException("'twitter' egg not found")

        for entry in entrylist if options.all else entrylist[:options.max or 1]:
            tweet(entry, conf, options.dryrun)

        return

    # XXX we should search for actual hrefs not random grepping, but this
    # requires access to the cache at non-runtime which is unfortunately
    # not possible yet.

    patterns = [
        re.compile(r'(?<=\n)\[.*?\]:\s?(https?://.+)$'),  # markdown
        re.compile(r'(?<=\n)\.\.\s+[^:]+:\s+(https?://.+)$'),  # docutils
    ]

    pool = Threadpool(options.jobs)
    ping = lambda src, dest: pingback(helpers.joinurl(conf['www_root'], src), dest, options.dryrun)

    for entry in entrylist if options.all else entrylist[:options.max or 1]:

        for href in sum([re.findall(pat, entry.source) for pat in patterns], []):
            pool.add_task(ping, *[entry.permalink, href])

        try:
            pool.wait_completion()
        except KeyboardInterrupt:
            sys.exit(1)
