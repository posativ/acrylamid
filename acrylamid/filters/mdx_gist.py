# -*- encoding: utf-8 -*-
#
# Markdown Gist, similar to rstx_gist.py 
#

import re
import markdown

from acrylamid.lib.requests import get, HTTPError, URLError
from acrylamid import log

match = ['gist', 'gistraw']

GIST_RE = r'\[gist:\s*(?P<gistID>\d+)(?:\s*(?P<filename>.+?))?\]'
GISTRAW_RE = r'\[gistraw:\s*(?P<gistID>\d+)(?:\s*(?P<filename>.+?))?\]'

class GistExtension(markdown.Extension):
    """Add [gist:] and [gistraw:] to Pyton-Markdown Extensions"""

    def extendMarkdown(self, md, md_globals):
        self.md = md
        md.inlinePatterns.add('gist', GistPattern(GIST_RE), '_begin')
        md.inlinePatterns.add('gistraw', GistPattern(GISTRAW_RE), '_begin')

class GistPattern(markdown.inlinepatterns.Pattern):
    """Replace [gist: id filename] with embedded Gist script. Filename is optional
       [gistraw: id filename] will return the raw text wrapped in a <pre> block (no embedded javascript)
       Add filters: [Markdown+gist] to your Markdown metadata"""

    def get_raw_gist_with_filename(self, gistID, filename):
        url = "https://raw.github.com/gist/%s/%s" % (gistID, filename)
        try:
            return get(url).read()
        except (URLError, HTTPError) as e:
            log.exception('Failed to access URL %s : %s' % (url, e))
        return ''

    def get_raw_gist(self, gistID):
        url = "https://raw.github.com/gist/%s" % (gistID)
        try:
            return get(url).read()
        except (URLError, HTTPError) as e:
            log.exception('Failed to access URL %s : %s' % (url, e))
        return ''

    def handleMatch(self, m):

        if markdown.version_info < (2, 1, 0):
            mdutils = markdown
        else:
            mdutils = markdown.util

        gistID = m.group('gistID')
        gistFilename = m.group('filename')

        if gistFilename:
            embeddedJS = "https://gist.github.com/%s.js?file=%s" % (gistID, gistFilename)
            rawGist = (self.get_raw_gist_with_filename(gistID, gistFilename))
        else:
            embeddedJS = "https://gist.github.com/%s.js" % (gistID)
            rawGist = (self.get_raw_gist(gistID))

        if self.pattern == GIST_RE:
            el = mdutils.etree.Element('div')
            el.set('class', 'gist')
            script = mdutils.etree.SubElement(el, 'script')
            script.set('src', embeddedJS)
            
            # NoScript alternative in <pre> block
            noscript = mdutils.etree.SubElement(el, 'noscript')
            pre = mdutils.etree.SubElement(noscript, 'pre')
            pre.set('class', 'literal-block')
            pre.text = mdutils.AtomicString(rawGist)
        else:
            # No javascript, just output gist as <pre> wrapped text
            el = mdutils.etree.Element('pre')
            el.set('class', 'literal-block gist-raw')
            el.text = mdutils.AtomicString(rawGist)

        return el


def makeExtension(configs=None):
    return GistExtension(configs=configs)
