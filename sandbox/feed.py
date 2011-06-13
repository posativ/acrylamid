# -*- coding: utf-8 -*-
# ATOM/RSS body.xml|entry.xml generator. Usage: python feed.py atom|rss

from shpaml import convert_text

ATOM_LAYOUT = '''
<?xml version="1.0" encoding="utf-8"?>
feed xmlns=http://www.w3.org/2005/Atom xml:lang={{lang}}
    author
    author
        name | posativ
        uri | http://posativ.org/
        email | info@posativ.org
    title | {{ title }}
    id | {{ domain }}
    > link rel=alternate type=text/html href={{domain}}
    > link rel=self type=application/atom+xml href={{feedurl}}
    updated | {{date}}
    generator uri=./index.py version={{lilith_version}} | ${{ lilith_name }}

    {{entry_list}}
'''

#print convert_text(ATOM_LAYOUT)

ATOM_ENTRY = '''
entry
    title | {{ title }}
    > link rel=alternate type=text/html href={{link}}
    id | {{ link }}
    updated | {{date}}
    author
        name | {{ author }}
        uri | {{ website }}
        email | {{ email }}
    content type=html | {{ content }}
'''

#print convert_text(ATOM_ENTRY)

RSS_LAYOUT = '''
rss version=2.0 xmlns:atom=http://www.w3.org/2005/Atom
    channel
        title | {{ title }}
        link | {{ domain }}
        description | {{ description }}
        language | {{ lang }}
        pubDate | {{ date }}
        docs | {{ feedurl }}
        generator | {{ lilith_name }} {{ lilith_version }}
        > atom:link href={{feedurl}} rel=self type=application/rss+xml
        {{entry_list}}
'''

#print convert_text(RSS_LAYOUT)

RSS_ENTRY = '''
item
    title | {{ title }}
    link | {{ link }}
    description | {{ content }}
    pubDate | {{ date }}
    guid | {{ link }}
'''

if __name__ == '__main__':
    from sys import argv
    
    def write(path, text):
        f = open(path, 'w')
        f.write(text)
        f.close()
    
    if len(argv) > 1:
        
        if argv[1] == 'rss':
            write('entry.xml', convert_text(RSS_ENTRY))
            print '... entry.xml written'
            write('body.xml', convert_text(RSS_LAYOUT))
            print '... body.xml written'
        else:
            write('entry.xml', convert_text(ATOM_ENTRY))
            print '... entry.xml written'
            write('body.xml', convert_text(ATOM_LAYOUT))
            print '... body.xml written'