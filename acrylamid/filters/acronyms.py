# -*- encoding: utf-8 -*-
#
# Copyright (c) 2010, 2011 Will Kahn-Greene
#
# Pyblosxom is distributed under the MIT license.  See the file
# LICENSE for distribution details.
#
# -- http://pyblosxom.bluesock.org/
#
# This is a port of PyBlosxom's acronyms plugin as acrylamid
# filter. All credits go to Pyblosxom's and blosxom's authors.

import io
import re

from acrylamid import log
from acrylamid.filters import Filter

from acrylamid.lib.html import HTMLParser, HTMLParseError


class Acrynomify(HTMLParser):

    def __init__(self, html, abbr, repl):
        self.abbr = abbr
        self.repl = repl

        HTMLParser.__init__(self, html)

    def handle_data(self, data):
        if any(filter(lambda i: i in self.stack, ['pre', 'code', 'math', 'script'])):
            pass
        else:
            data = self.abbr.sub(self.repl, data)
        self.result.append(data)


class Acronyms(Filter):

    match = [re.compile('^Acronyms?$', re.I), 'abbr', 'Abbr']
    version = '1.0.1'

    # after Typography, so CAPS is around ABBR
    priority = 20.0

    def init(self, conf, env):

        if conf.get('acronyms_file', None):
            with io.open(conf['acronyms_file'], 'r') as fp:
                data = fp.readlines()
        else:
            global ACRONYMS
            data = ACRONYMS.split('\n')

        acronyms = {}
        for line in data:
            line = line.split("=", 1)
            firstpart = line[0].strip()

            secondpart = line[1].strip()
            secondpart = secondpart.replace("\"", "&quot;")

            if secondpart.startswith("abbr|"):
                secondpart = secondpart[5:]
            elif secondpart.startswith("acronym|"):
                secondpart = secondpart[8:]

            acronyms[re.compile(firstpart)] = secondpart

        self.acronyms = acronyms

    def transform(self, text, entry, *args):

        acros = self.acronyms
        if len(args) > 0:
            acros = dict(filter(lambda k: any(k[0] == v for v in args), acros.items()))

        try:
            abbr = re.compile(r'\b(%s)\b' % '|'.join((pat.pattern for pat in acros)))
        except re.error as e:
            log.warn("acronyms: %s", e.args[0])

        def repl(match):

            abbr = match.group(0)
            desc = acros.get(abbr, None)

            if desc is None:
                for pat in acros:
                    if pat.match(abbr):
                        desc = acros.get(pat)
                        break
            return '<abbr title="%s">%s</abbr>' % (desc, abbr)

        try:
            return ''.join(Acrynomify(text, abbr, repl).result)
        except HTMLParseError as e:
            log.warn('%s: %s in %s' % (e.__class__.__name__, e.msg, entry.filename))
            return text


ACRONYMS = r"""
ASCII=American Standard Code for Information Interchange
BGP=Border Gateway Protocol
BSD=Berkeley System Distribution
CGI=Common Gateway Interface
CLI=Command Line Interface
CLUE=Command Line User Environment
CSS=Cascading Stylesheets
CVS=Concurrent Versioning System
DSL=Digital Subscriber Line
EFF=Electronic Frontier Foundation
ELF=Executable and Linking Format
FAQ=Frequently asked question(s)
FFII=Foundation for a Free Information Infrastructure / F&ouml;rderverein f&uuml;r eine Freie Informationelle Infrastruktur
FIFO=First In, First Out
FLOSS=Free, Libre and Open Source Software
FOSS=Free and Open Source Software
FSF=Free Software Foundation
FSFE=Free Software Foundation Europe
GNOME=GNU Network Object Model Environment
GPL=GNU General Public License
GPRS=General Packet Radio Service
GSM=Global System for Mobile Communications
GUI=Graphical User Interface
HTML=Hypertext Markup Language
HTTP=Hypertext Transport Protocol
IMD[Bb]=Internet Movie Database
IRC=Internet Relay Chat
ISBN=International Standard Book Number
ISDN=Integrated Services Digital Network
ISO=International Organization for Standardization; also short for a image of an ISO9660 (CD-ROM) file system
ISSN=International Standard Serial Number
KDE=K-Desktop Environment; Kolorful Diskfilling Environment
KISS=Keep it simple, stupid
LIFO=Last In, First Out
LUG=Linux User Group
MCSE=Minesweeper Consultant and Solitaire Expert (User Friendly)
MMS=Multimedia Messaging Service
MMX=Multimedia Extension
MP3=MPEG (Moving Picture Experts Group) 1 Audio Layer 3
MPEG=Moving Picture Experts Group
MSIE=Microsoft Internet Explorer
NSFW=Not Safe For Work
OOP=Object-Oriented Programming
OS=Operating System; Open Source
OSI=Open Source Initiative; Open Systems Interconnection
OSS=Open Source Software
PHP[2345]?=Programmers Hate PHP ;-)
QA=Quality Assurance
RAM=Random Access Memory
ROM=Read Only Memory
SMD=Surface Mounted Devices
SMS=Short Message Service
SMTP=Simple Mail Transfer Protocol
SPF=Sender Policy Framework, formerly Sender Permitted From
SSI=Server-Side Includes
TLA=Three Letter Acronym
UI=User Interface
UMTS=Universal Mobile Telecommunications System
URI=Uniform Resource Indicator
URL=Uniform Resource Locator
USB=Universal Serial Bus
VM=Virtual Machine
VoIP=Voice over IP
WYSIWYG=What you see is what you get
XHTML=Extensible Hypertext Markup Language
XML=Extensible Markup Language
""".strip()
