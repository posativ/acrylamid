#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# TODO:
# - anyway to keep &shy; in atom?

import tools, os, cgi

from shpaml import convert_text
from jinja2 import Template

ATOM_BODY = '''
<?xml version="1.0" encoding="utf-8"?>
feed xmlns=http://www.w3.org/2005/Atom xml:lang={{lang}}
    author
        name | posativ
        uri | http://posativ.org/
        email | info@posativ.org
    title | {{ blog_title }}
    id | {{ website }}
    > link rel=alternate type=text/html href={{website}}
    > link rel=self type=application/atom+xml href={{website.strip('/')+'/atom/'}}
    updated | {{ _date.strftime('%Y-%m-%dT%H:%M:%SZ') }}
    generator uri=./index.py version={{lilith_version}} | {{ lilith_name }}

    {{ entry_list }}
'''.strip()

ATOM_ENTRY = '''
entry
    title | {{ title }}
    > link rel=alternate type=text/html href={{url}}
    id | {{ id }}
    updated | {{ _date.strftime('%Y-%m-%dT%H:%M:%SZ') }}
    author
        name | {{ author }}
        uri | {{ website }}
        email | {{ email }}
    content type=html | {{ body }}
'''.strip()

RSS_BODY = '''
rss version=2.0 xmlns:atom=http://www.w3.org/2005/Atom
    channel
        title | {{ blog_title }}
        link | {{ website }}
        description | {{ description }}
        language | {{ lang }}
        pubDate | {{ _date.strftime('%a, %d %b %Y %H:%M:%S GMT') }}
        docs | {{ website.strip('/')+'/atom/' }}
        generator | {{ lilith_name }} {{ lilith_version }}
        > atom:link href={{website.strip('/')+'/atom/'}} rel=self type=application/rss+xml
        {{ entry_list }}
'''.strip()

RSS_ENTRY = '''
item
    title | {{ title }}
    link | {{ url }}
    description | {{ body }}
    pubDate | {{ _date.strftime('%a, %d %b %Y %H:%M:%S GMT') }}
    guid isPermaLink=false | {{ id }}
'''.strip()

def cb_feed(request):
    
    tt_atom_entry = Template(convert_text(ATOM_ENTRY))
    tt_atom_body = Template(convert_text(ATOM_BODY))
    tt_rss_entry = Template(convert_text(RSS_ENTRY))
    tt_rss_body = Template(convert_text(RSS_BODY))
    config = request._config
    data = request._data
    
    data['type'] = 'feed'
    count = 25
    
    # last preparations
    request = tools.run_callback(
            'prepare',
            request)
    
    dict = request._config
    rss_list = []
    atom_list = []
    for entry in data['entry_list'][:25]:
        entry['body'] = cgi.escape(entry['body'].replace('&shy;', ''))
        entrydict = dict.copy()
        entrydict.update(entry)
        atom_list.append(tt_atom_entry.render( entrydict ))
        rss_list.append(tt_rss_entry.render( entrydict ))
    
    # atom
    dict.update( {'entry_list': '\n'.join(atom_list),
                  '_date': data['entry_list'][0]._date } )
    xml = tt_atom_body.render( dict )
    directory = os.path.join(config.get('output_dir', 'out'), 'feed', 'atom')
    path = os.path.join(directory, 'index.xml')
    tools.mk_file(xml, {'title': 'atom/index.xml'}, path)
    
    # rss
    dict.update( {'entry_list': '\n'.join(rss_list),
                  '_date': data['entry_list'][0]._date } )
    xml = tt_rss_body.render( dict )
    directory = os.path.join(config.get('output_dir', 'out'), 'feed', 'rss')
    path = os.path.join(directory, 'index.xml')
    tools.mk_file(xml, {'title': 'rss/index.xml'}, path)
    