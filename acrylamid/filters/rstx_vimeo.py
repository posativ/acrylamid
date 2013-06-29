# -*- encoding: utf-8 -*-
#
# Copyright 2012 the_metalgamer <the_metalgamer@hackerspace.lu>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from docutils import nodes
from docutils.parsers.rst import Directive, directives

import re

color_pattern = re.compile("([a-f]|[A-F]|[0-9]){3}(([a-f]|[A-F]|[0-9]){3})")

match = ['vimeo']


def align(argument):
    return directives.choice(argument, ('left', 'center', 'right'))

def color(argument):
    match = color_pattern.match(argument)
    if match:
        return argument
    else:
        raise ValueError('argument must be an hexadecimal color number')


class Vimeo(Directive):
    """Vimeo directive for easy embedding (`:options:` are optional).

    .. code-block:: rst

        .. vimeo:: 6455561
           :align: center
           :height: 1280
           :width: 720
           :border: 1px
           :color: ffffff
           :nobyline:
           :noportrait:
           :nobyline:
           :notitle:
           :autoplay:
           :loop:
    """

    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        'height': directives.length_or_unitless,
        'width': directives.length_or_unitless,
        'align': align,
        'border': directives.length_or_unitless,
        'color': color,
        'noportrait': directives.flag,
        'notitle': directives.flag,
        'nobyline': directives.flag,
        'autoplay': directives.flag,
        'loop': directives.flag,
    }
    has_content = False

    def run(self):

        alignments = {
            'left': '0',
            'center': '0 auto',
            'right': '0 0 0 auto',
        }

        self.options.setdefault('color', 'ffffff')

        uri = ("http://player.vimeo.com/video/" + self.arguments[0]
               + ( "?color=" + self.options['color'] + "&" ) \
               + ( "title=0&" if 'notitle' in self.options else "") \
               + ( "portrait=0&" if 'noportrait' in self.options else "") \
               + ( "byline=0&" if 'nobyline' in self.options else "") \
               + ( "autoplay=1&" if 'autoplay' in self.options else "") \
               + ( "loop=1" if 'loop' in self.options else "" )
                )
        self.options['uri'] = uri
        self.options['align'] = alignments[self.options.get('align', 'center')]
        self.options.setdefault('width', '500px')
        self.options.setdefault('height', '281px')
        self.options.setdefault('border', '0')

        VI_EMBED = """<iframe width="%(width)s" height="%(height)s" src="%(uri)s" \
                      frameborder="%(border)s" style="display: block; margin: %(align)s;" \
                      class="video" webkitAllowFullScreen mozallowfullscreen allowfullscreen></iframe>"""
        return [nodes.raw('', VI_EMBED % self.options, format='html')]

def register(roles, directives):
    directives.register_directive('vimeo', Vimeo)
