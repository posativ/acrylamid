# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see lilith.py
#
# TODO:
# - anyway to keep &shy; in atom?

import tools, os, cgi
from datetime import datetime

from shpaml import convert_text
from jinja2 import Template

ATOM_BODY = '''
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{{ lang.replace('_', '-') }}">
    <author>
        <name>{{ author }}</name>
        <uri>{{ website }}</uri>
        <email>{{ email }}</email>
    </author>
    <title>{{ blog_title }}</title>
    <id>{{ website }}</id>
    <link rel="alternate" type="text/html" href="{{ website }}" />
    <link rel="self" type="application/atom+xml" href="{{ website.strip('/')+'/atom/' }}" />
    <updated>{{ date.strftime('%Y-%m-%dT%H:%M:%SZ') }}</updated>
    <generator uri="https://posativ.org/lilith/" version="{{ lilith_version }}">{{ lilith_name }}</generator>

    {{ entry_list }}
</feed>
'''.strip()

ATOM_ENTRY = '''
<entry>
    <title>{{ title }}</title>
    <link rel="alternate" type="text/html" href="{{ url }}" />
    <id>{{ id }}</id>
    <updated>{{ date.strftime('%Y-%m-%dT%H:%M:%SZ') }}</updated>
    <author>
        <name>{{ author }}</name>
        <uri>{{ website }}</uri>
        <email>{{ email }}</email>
    </author>
    <content type="html">{{ body }}</content>
</entry>
'''.strip()

RSS_BODY = '''
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>{{ blog_title }}</title>
        <link>{{ website }}</link>
        <description>{{ description }}</description>
        <language>{{ lang }}</language>
        <pubDate>{{ date.strftime('%a, %d %b %Y %H:%M:%S GMT') }}</pubDate>
        <docs>{{ website.strip('/')+'/atom/' }}</docs>
        <generator>{{ lilith_name }} {{ lilith_version }}</generator>
        <atom:link href="{{ website.strip('/')+'/atom/' }}" rel="self" type="application/rss+xml" />
        {{ entry_list }}
    </channel>
</rss>
'''.strip()

RSS_ENTRY = '''
<item>
    <title>{{ title }}</title>
    <link>{{ url }}</link>
    <description>{{ body }}</description>
    <pubDate>{{ date.strftime('%a, %d %b %Y %H:%M:%S GMT') }}</pubDate>
    <guid isPermaLink="false">{{ id }}</guid>
</item>
'''.strip()

def cb_end(request):
    
    tt_atom_entry = Template(ATOM_ENTRY)
    tt_atom_body = Template(ATOM_BODY)
    tt_rss_entry = Template(RSS_ENTRY)
    tt_rss_body = Template(RSS_BODY)
    conf = request._config
    data = request._data
    
    data['type'] = 'feed'
    num = 25
    UTC_OFFSET = datetime.now() - datetime.utcnow()
    
    conf = request._config
    data = request._data
    
    """it seems, relative urls in feeds is not wideley implemented"""
    for i, entry in enumerate(data['entry_list']):
        url = conf['www_root'] + '/' + str(entry.date.year) + \
              '/' + tools.safe_title(entry['title']) + '/'
        data['entry_list'][i]['url'] = url
    
    # last preparations
    request = tools.run_callback(
            'prepare',
            request)
    
    dict = request._config
    rss_list = []
    atom_list = []
    for entry in data['entry_list'][:num]:
        entry['body'] = cgi.escape(entry['body'].replace('&shy;', ''))
        entrydict = dict.copy()
        entrydict.update(entry)
        entrydict['date'] = entrydict['date'] - UTC_OFFSET
        atom_list.append(tt_atom_entry.render( entrydict ))
        rss_list.append(tt_rss_entry.render( entrydict ))
    
    # atom
    dict.update( {'entry_list': '\n'.join(atom_list),
                  'date': data['entry_list'][0].date - UTC_OFFSET} )
    xml = tt_atom_body.render( dict )
    directory = os.path.join(conf['output_dir'], 'atom')
    path = os.path.join(directory, 'index.xml')
    tools.mk_file(xml, {'title': 'atom/index.xml'}, path)
    
    # rss
    dict.update( {'entry_list': '\n'.join(rss_list),
                  'date': data['entry_list'][0].date - UTC_OFFSET} )
    xml = tt_rss_body.render( dict )
    directory = os.path.join(conf['output_dir'], 'rss')
    path = os.path.join(directory, 'index.xml')
    tools.mk_file(xml, {'title': 'rss/index.xml'}, path)
    
    return request
    