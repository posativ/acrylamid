# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see lilith.py
# -*- encoding: utf-8 -*-

import os, cgi
from datetime import datetime, timedelta

from lilith.views import View
from lilith.utils import expand, render, mkfile, joinurl

from jinja2 import Template

filters = []


class Feed(View):
        
    num_entries = 25
    
    def __call__(self, request):

        conf = request['conf']
        env = request['env']
        entrylist = request['entrylist']

        tt_entry = Template(self.tt_entry)
        tt_body = Template(self.tt_body)

#        utc_offset = timedelta(hours=2)

        result = []
        for entry in entrylist[:self.num_entries]:
            _id = 'tag:' + conf.get('www_root', '').replace(env['protocol']+'://', '') \
                         + ',' + entry.date.strftime('%Y-%m-%d') + ':' \
                         + entry.permalink
            result.append(render(tt_entry, env, conf, entry, id=_id))
        
        xml = render(tt_body, env, conf, {'entrylist': '\n'.join(result),
                      'updated': entrylist[0].date if entrylist else datetime.now()},
                      atom=atom, rss=rss)
        
        p = joinurl(conf['output_dir'], self.path , 'index.html')
        mkfile(xml, {'title': joinurl(self.path, 'index.html')}, p)

        
class atom(Feed):
    
    __view__ = True
    path = '/atom/'

    def __init__(self, conf, env):
        self.tt_entry = ATOM_ENTRY
        self.tt_body = ATOM_BODY


class rss(Feed):

    __view__ = True
    path = '/rss/'

    def __init__(self, conf, env):
        self.tt_entry = RSS_ENTRY
        self.tt_body = RSS_BODY


ATOM_BODY = r'''
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{{ lang.replace('_', '-') }}">
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
    <generator uri="https://posativ.org/lilith/" version="{{ lilith_version }}">{{ lilith_name }}</generator>
    {{ entrylist }}
</feed>
'''.strip()

ATOM_ENTRY = r'''
<entry>
    <title>{{ title | escape }}</title>
    <link rel="alternate" type="text/html" href="{{ www_root+permalink }}" />
    <id>{{ id }}</id>
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
        <language>{{ lang }}</language>
        <pubDate>{{ updated.strftime('%a, %d %b %Y %H:%M:%S GMT') }}</pubDate>
        <docs>{{ www_root+rss.path }}</docs>
        <generator>{{ lilith_name }} {{ lilith_version }}</generator>
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
    <pubDate>{{ date.strftime('%a, %d %b %Y %H:%M:%S GMT') }}</pubDate>
    <guid isPermaLink="false">{{ id }}</guid>
</item>
'''.strip()
