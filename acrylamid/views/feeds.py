# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py
# -*- encoding: utf-8 -*-

import os, cgi
from datetime import datetime, timedelta

from acrylamid.views import View
from acrylamid.utils import expand, render, mkfile, joinurl

from jinja2 import Environment

filters = []
enabled = True

class Feed(View):
        
    num_entries = 25
    env = Environment()
    
    def __call__(self, request):
        
        conf = request['conf']
        env = request['env']
        entrylist = request['entrylist']
        
        result = []
        for entry in entrylist[:self.num_entries]:
            _id = 'tag:' + conf.get('www_root', '').replace(env['protocol']+'://', '') \
                         + ',' + entry.date.strftime('%Y-%m-%d') + ':' \
                         + entry.permalink
            result.append(render(self.tt_entry, env, conf, entry, id=_id))
        
        xml = render(self.tt_body, env, conf, {'entrylist': '\n'.join(result),
                      'updated': entrylist[0].date if entrylist else datetime.now()},
                      atom=atom, rss=rss)
        
        p = joinurl(conf['output_dir'], self.path , 'index.html')
        mkfile(xml, {'title': joinurl(self.path, 'index.html')}, p)

        
class atom(Feed):
    
    __view__ = True
    path = '/atom/'

    def __init__(self, conf, env):
        self.tt_entry = self.env.from_string(ATOM_ENTRY)
        self.tt_body = self.env.from_string(ATOM_BODY)


class rss(Feed):

    __view__ = True
    path = '/rss/'

    def __init__(self, conf, env):      
        
        from wsgiref.handlers import format_date_time
        from time import mktime
        
        self.env.filters['rfc822'] = lambda x: format_date_time(mktime(x.timetuple()))
        self.tt_entry = self.env.from_string(RSS_ENTRY)
        self.tt_body = self.env.from_string(RSS_BODY)


ATOM_BODY = r'''
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{{ lang[0].replace('_', '-') }}">
    <author>
        <name>{{ author }}</name>
        <uri>{{ website }}</uri>
        <email>{{ email }}</email>
    </author>
    <title>{{ blog_title | escape }}</title>
    <id>{{ website }}</id>
    <link rel="alternate" type="text/html" href="{{ website }}" />
    <link rel="self" type="application/atom+xml" href="{{ www_root+atom.path }}" />
    <updated>{{ updated.strftime('%Y-%m-%dT%H:%M:%SZ') }}</updated>
    <generator uri="https://posativ.org/acrylamid/" version="{{ acrylamid_version }}">{{ acrylamid_name }}</generator>
    {{ entrylist }}
</feed>
'''.strip()

ATOM_ENTRY = r'''
<entry>
    <title>{{ title | escape }}</title>
    <link rel="alternate" type="text/html" href="{{ www_root + permalink }}" />
    <id>{{ id.rstrip('/') }}</id>
    <updated>{{ date.strftime('%Y-%m-%dT%H:%M:%SZ') }}</updated>
    <author>
        <name>{{ author }}</name>
        <uri>{{ website }}</uri>
        <email>{{ email }}</email>
    </author>
    <content type="html">{{ content | escape }}</content>
</entry>
'''.strip()

RSS_BODY = r'''
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>{{ blog_title | escape }}</title>
        <link>{{ website }}</link>
        <description>{{ description }}</description>
        <language>{{ lang[0].replace('_', '-').lower() }}</language>
        <pubDate>{{ updated | rfc822 }}</pubDate>
        <docs>{{ www_root+rss.path }}</docs>
        <generator>{{ acrylamid_name }} {{ acrylamid_version }}</generator>
        <atom:link href="{{ www_root+atom.path }}" rel="self" type="application/rss+xml" />
        {{ entrylist }}
    </channel>
</rss>
'''.strip()

RSS_ENTRY = r'''
<item>
    <title>{{ title | escape }}</title>
    <link>{{ www_root + permalink }}</link>
    <description>{{ content | escape }}</description>
    <pubDate>{{ date | rfc822 }}</pubDate>
    <guid isPermaLink="false">{{ id.rstrip('/') }}</guid>
</item>
'''.strip()
