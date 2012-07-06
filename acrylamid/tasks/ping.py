# -*- encoding: utf-8 -*-
#
# Copyrights:
#    - PingBack: Иван Сагалаев (Ivan Sagalaew) <maniac@softwaremaniacs.org>
#    - Other: posativ <info@posativ.org>
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import sys
import re
import os
import urlparse
import xmlrpclib

from urlparse import urlparse

from acrylamid.tasks import task, argument
from acrylamid.errors import AcrylamidException

from acrylamid import readers, helpers, colors
from acrylamid.tasks.info import option
from acrylamid.lib.requests import head, URLError, HTTPError
from acrylamid.lib.async import Threadpool

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

            print "Pingback", colors.blue(urlparse(server_url).netloc),
            print "from", colors.green(''.join(urlparse(src)[1:3])) + "."

            if not dryrun:
                server = xmlrpclib.ServerProxy(server_url)
                server.pingback.ping(src, dest)

    except xmlrpclib.ProtocolError as e:
        raise AcrylamidException(e.args[0])


def twitter():

    import twitter

    CONSUMER_KEY = 'ShUqv0JkccHF2abLvWWzXg'
    CONSUMER_SECRET = '6k1GaHkeBzFUCIozKjjKS0IgtKItO7cH5ii7BsM0jPg'
    TWITTER_CREDS = os.path.expanduser('.twitter_oauth')
    if not os.path.exists(TWITTER_CREDS):
        twitter.oauth_dance("Acrylamid", CONSUMER_KEY, CONSUMER_SECRET,
                    TWITTER_CREDS)

    oauth_token, oauth_token_secret = twitter.read_token_file(TWITTER_CREDS)

    try:
        t = twitter.Twitter(auth=twitter.OAuth(
            oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET))

        tags = [x.replace(u' ', u'_') for x in entry.tags]
        tags = u"#" + u" #".join(tags)
        tweet = u"New Blog Post: {0} {1}{2} {3}".format(entry.title, kw['conf']['www_root'], entry.permalink, tags)
        t.statuses.update(status=tweet.encode('utf8'))
        print(tweet.encode('utf8'))
    except Exception as e:
        print(e)


@task('ping', arguments, "notify ressources")
def run(conf, env, options):
    """Subcommand: ping -- notify external ressources via Pingback etc."""

    entrylist = [entry for entry in readers.load(conf) if not entry.draft]

    if options.file:
        try:
            entrylist = [filter(lambda e: e.filename == options.file, entrylist)[0]]
        except IndexError:
            raise AcrylamidException("no such post!")

    # XXX we should search for actual hrefs not random grepping, but this
    # requires access to the cache at non-runtime which is unfortunately
    # not possible yet.

    patterns = [
        re.compile(r'(?<=\n)\[.*?\]:\s?([a-z0-9].+)'),  # markdown
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
