# -*- encoding: utf-8 -*-#
#
# License: This document has been placed in the public domain
# Author: Brian Hsu

from docutils.parsers.rst import Directive, directives
from docutils import nodes

from acrylamid.lib.requests import get, HTTPError, URLError
from acrylamid import log

class Gist(Directive):
    """`GitHub:Gist <https://gist.github.com/>`__ embedding (file is optional).

  .. code-block:: rst

      .. gist:: 4145152
         :file: transmission.rb
    """

    required_arguments = 1
    optional_arguments = 1
    option_spec = {'file': directives.unchanged}
    final_argument_whitespace = True
    has_content = False

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

    def run(self):

        gistID = self.arguments[0].strip()

        if 'file' in self.options:
            filename = self.options['file']
            rawGist = (self.get_raw_gist_with_filename(gistID, filename))
            embedHTML = '<script src="https://gist.github.com/%s.js?file=%s"></script>' % \
                (gistID, filename)
        else:
            rawGist = (self.get_raw_gist(gistID))
            embedHTML = '<script src="https://gist.github.com/%s.js"></script>' % gistID

        return [nodes.raw('', embedHTML, format='html'),
                nodes.raw('', '<noscript>', format='html'),
                nodes.literal_block('', rawGist),
                nodes.raw('', '</noscript>', format='html')]


def register(roles, directives):
    directives.register_directive('gist', Gist)
