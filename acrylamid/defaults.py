#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import sys
import os
import logging
import yaml

from os.path import exists, isfile, isdir, join

log = logging.getLogger('acrylamid.defaults')

def init(root='.', overwrite=False):
    
    dirs = ['%(entries_dir)s/', '%(layout_dir)s/',
            '%(output_dir)s/', 'extensions/', ]
    files = {'conf.yaml': conf,
             '%(output_dir)s/blog.css': css,
             '%(layout_dir)s/main.html': main,
             '%(layout_dir)s/entry.html': entry,
             '%(entries_dir)s/sample entry.txt': kafka}
             
    default = yaml.load(conf)
    default['output_dir'] = default.get('output_dir', 'output/').rstrip('/')
    default['entries_dir'] = default.get('entries_dir', 'content/').rstrip('/')
    default['layout_dir'] = default.get('layout_dir', 'layouts/').rstrip('/')
    
    if root != '.' and not exists(root):
        os.mkdir(root)
                
    for directory in dirs:
        directory = join(root, directory % default)
        if exists(directory) and not isdir(directory):
            log.critical('Unable to create %s. Please remove this file', directory)
            sys.exit(1)
        elif not exists(directory):
            os.mkdir(directory)
            log.info('create  %s', directory)
        else:
            log.info('skip  %s already exists', directory)
    
    for path, content in files.iteritems():
        path = join(root, path % default)
        if exists(path) and not isfile(path):
            log.critical('%s must be a regular file' % path)
            sys.exit(1)
        elif not exists(path) or overwrite == True:
            f = open(path, 'w')
            f.write(content)
            f.close()
            log.info('create  %s', path)
        else:
            log.info('skip  %s already exists', path)


conf =  '''
blog_title: A descriptive blog title

author: anonymous
website: http://example.org/
email: info@example.org

www_root: http://example.org/
lang: de_DE
strptime: "%d.%m.%Y, %H:%M"

disqus_shortname: yourname

views.filters: ['markdown+codehilite(css_class=highlight)', 'typo', 'hyph']

views.index.filters: ['summarize', 'h1']
views.entry.filters: ['h1']
views.feeds.filters: ['h2']
'''.strip()

css = '''
@import url('pygments.css');

body {
    background-color: #ffffff;
}

a img {
    border: none;
}


img {
/*     padding: 5px; */
    border: none;
}

blockquote {
    padding-left: 24px;
    padding-right: 24px;
    font: italic small Verdana, Times, sans-serif;
    color: #222;
}

blockquote em {
    font-weight: bold;
}

ul {list-style-type: none; padding-top: 4px; padding-bottom: 4px; padding-left: 6px;}
li {padding-top: 3px;}
ol {padding-top: 4px; padding-bottom: 4px; padding-left: 36px;}
pre {font-size: 12px; font-family: "Courier New", "DejaVu Sans Mono", monospace;}
code {font-family: "Courier New", "DejaVu Sans Mono", monospace;}

#blogheader {
    margin-bottom: 10px;
    font-family: "Times New Roman";
    padding: 10px;
    text-align: center;
}


#blogtitle h2,h3 {
    text-align: center;
    padding-top: 1.5em;
    color: #000;
    text-decoration: none;
}



#blogheader #blogtitle a.blogtitle {
    text-align: center;
    color: #000;
    text-decoration: none;
    border-bottom: none;
}

#blogheader a {
    text-decoration: none;
    color: #778;
    border-bottom: 1px dotted #000;
    font-weight: bold;
}

#blogheader a:hover {
    color: #555;
    text-shadow: #bbb 0px 0px 1px;
}

#blogbody {
    margin: 0 auto;
    width: 750px;
}

/*#blogbody a.floatright:hover, #blogbody a.floatleft:hover {
    text-shadow: #000 0px 0px 1px;
}*/

#blogbody .page {
    font: bold medium "Times New Roman";
    color: #000000;
    text-decoration: none;
}

#blogbody .page:hover {
    text-shadow: #aaa 0px 0px 2px;
}

#blogfooter {
    margin-top: 10px;
    padding: 10px;
    text-align: center;
    font: medium "Times New Roman";
}

#blogfooter a {
/*     font-size: 8pt; */
    font-weight: bold;
    text-decoration: none;
    border-bottom: 1px dotted #000;
    color: #a24;
}

#blogfooter a:hover {
    text-shadow: #e68 0px 0px 1px;
}

#mainlinks ul {
  left: 50%;
  clear: left;
  float: left;
  position: relative;
  text-align: center;
  list-style: none;
  margin: 0;
  padding: 0;
}

#mainlinks li {
    float: left;
    display: block;
    position: relative;
    right: 50%;
    margin: 0 2em 0 2em;
}

#mainlinks {
    padding: 2em;
    margin: 2em 20% 2em 20%;
    font: medium "Times New Roman";
    text-decoration: none;
}


#mainlinks #previous {
    float: left;
}

#mainlinks #next {
    float: right;
}

/* posting */

.posting {
    padding: 1em;
    margin-top: 4em;
    margin-bottom: 5em;
}

/* postheader */

.postheader {
    margin-bottom: 2em;
}

.postheader .sort {
    font: medium "Times New Roman";
    color: #000000;
    float: left;
}

.postheader .sort a {
    padding-left: 1em;
}

.postheader .subject {
    font-size: medium;
    color: #000000;
    margin-bottom: -1.3em;
/*     float: left; */
}

.postheader .subject a, .postheader .sort a {
    color: #000000;
    font: bold medium "Times New Roman";
    text-decoration: none;
    border: none;
}

.postheader .subject a:hover, .postheader .sort a:hover {
    text-shadow: #aaa 0px 0px 2px;
}

.postheader .date {
    font: 0.70em "Georgia";
    float: right;
}

/* postfooter */

/*.postfooter {
    margin-top: 1em;
}*/

.postfooter .tags {
    float: left;
}

.postfooter a {
    color: #777;
    font-family: Palatino, "times new roman", serif;
    font-weight: bold;
    font-size: 0.9em;
    text-decoration: none;
    float: right;
}

.postfooter a:hover {
    color: #555;
    text-shadow: #bbb 0px 0px 1px;
}

/* postbody */

.postbody {
    text-align: justify;
    padding-left: 1em;
    font-family: Palatino,"times new roman",serif;
    font-size: 11pt;
    overflow: auto;
}

.postbody h2 {
    font: 12pt "Times New Roman";
/*     font-family: "DejaVu Sans", Verdana, sans-serif; */
    font-weight: bold;
    color: #888;
    border-bottom: 1px dotted #888;
    /*border-bottom: solid;
    border-color: #888;
    border-width: 1px;*/
}

.postbody h3, h4 {
    font: 12pt "Times New Roman";
    text-align: left;
    padding-left: 4px;
    font-weight: bold;
    color: #888;
    }

.postbody a {
    text-decoration: none;
    color: #c00;
}

.postbody a:visited {color: #a00;}
.postbody a:hover {
    color: #ff190d;
    text-shadow: #f66 0px 0px 1px;
}


.postbody p {
    padding-left: 12px;
    line-height: 1.3em;
}

.postbody ul {
    padding-left: 40px;
    padding-top: 10px;
    padding-bottom: 10px;
    list-style-type: disc;
}

.postbody dl {
    padding-left: 16px;
}

.postbody dl  dt {
    font-weight: bold;
    color: #444;
    padding: 6px 92px 3px 0;
    line-height: 1.1em;
    padding-top: 9px;
    }

.postbody dl dd {
    padding-left: 12px; padding-top: 0px;
    margin-left: 4px;
    border-left: solid;
    border-width: 1px;
    border-color: #444;
    color: #333;
}

.postbody dl p {padding-left: 0; padding-top: 0px; padding-bottom: 4px;}

.postbody hr {
    color: #DCDCDC;
    width: 320px;
    border-top-style:solid;
    border-right-style:none;
    border-bottom-style:none;
    border-left-style:none;
    margin: 12px 0 4px 235px;
}

.postbody .continue {
    font: normal small "DejaVu Sans", Verdana, sans-serif;
}

.postbody pre, .postbody code, .postbody tt {
    text-align: left;
}

.postbody img {
    max-width: 760px;
    -moz-box-shadow: 0px 0px 9px #000;
    -webkit-box-shadow: 0px 0px 9px #000;
    box-shadow: 0px 0px 4px #000;    
    }

.divider {
    margin: 2em 0;
    text-align: center;
}


/*other stuff*/

.floatright {
    float: right;
    margin-left: 12px;
}
.floatleft {
    float: left;
    margin-right: 12px;
}

.left {margin-left: 1em;}
.down {margin-bottom: 1em;}
.right {margin-right: 1em;}

li blockquote {
    font: normal 1em Verdana, Times, sans-serif;
    color: #555;
    margin-top: 0px;
    margin-bottom: 0px;
    margin-left: 12px;
    padding-left: 2px;
    border-left: 3px solid #ccc;
    }

.highlight {
    border: 1pt dashed black;
    padding: 1em 1em 1em 1em;
    overflow: auto;
}

/* .section pre {margin-left: 12px;} */

.shadow {
   -moz-box-shadow: 0px 0px 9px #000;
   -webkit-box-shadow: 0px 0px 9px #000;
   box-shadow: 0px 0px 4px #000;
}

.light {
   -moz-box-shadow: 0px 0px 12px #eee;
   -webkit-box-shadow: 0px 0px 12px #eee;
   box-shadow: 0px 0px 12px #eee;
}

#disqus_thread {padding-top: 24px;}

/*youtube Player..*/
object[type="application/x-shockwave-flash"] {
    -moz-box-shadow: 0px 0px 12px #777;
    -webkit-box-shadow: 0px 0px 12px #777;
    box-shadow: 0px 0px 12px #777;
    /*position: relative;
    left: 5%;
    margin: 0 auto;*/
    margin-left: 15px;
    text-align: center;
}

/* sort by date */

.date li a {
    padding-left: 0.2em;
}

/* sort by category */

.category h1 a, .category h2 a, .category h1 a:visited, .category h2 a:visited {
    text-decoration: none;
    font: 12pt Verdana, sans-serif;
    font-weight: bold;
    color: #888;
}


.caps {
    font-size: 0.9em;
    letter-spacing: 0.1em;
}

.textile {
    text-align: left;
}'''.strip()

main = r'''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <title>
   {{ blog_title }}
  </title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="content-language" content="de, en" />
  <meta content="{{ content }}" name="description" />
  <meta content="{{ keywords }}" name="keywords" />
  <link media="all" href="/blog.css" type="text/css" rel="stylesheet" />
  <link href="/favicon.ico" rel="shortcut icon" />
  <link href="/" rel="home" />
  <link href="/atom" type="application/atom+xml" rel="alternate" title="Atom-Feed" />
  <link href="/rss" type="application/rss+xml" rel="alternate" title="RSS-Feed" />
 </head>
 <body>
    <div id="blogheader">
        <div id="blogtitle">
            <h2>
                <a href="/" class="blogtitle">{{ blog_title }}</a>
            </h2>
        </div>
        <div id="mainlinks">
            <ul>
                <li>
                    <a href="/">blog</a>
                </li>
                <li>
                    <a href="/atom/">atom</a>
                </li>
                <li>
                    <a href="/rss/">rss</a>
                </li>
                <li>
                    <a href="/articles/">articles</a>
                </li>
            </ul>
        </div>
    </div>
    <div id="blogbody">
        {{ entrylist }}
        {% if page and page > 2 %}
            <a href="/page/{{ page-1 }}/" class="page floatleft">
            ← neuere Beiträge
            </a>
        {%- endif %}
        {% if page and page == 2 %}
            <a href="/" class="page floatleft">
            ← neuere Beiträge
            </a>
        {%- endif %}
        {% if page and page < num_entries/items_per_page %}
            <a href="/page/{{ page+1 }}/" class="page floatright">
            ältere Beiträge →
            </a>
        {%- endif  %}
    </div>
    <div id="blogfooter">
        <p>
            written by <a href="mailto:{{ email }}">{{ author }}</a>
        </p>
        <a href="http://creativecommons.org/licenses/by-nc-sa/2.0/de/">
            <img src="/img/cc.png" alt="by-nc-sa" />
        </a>
    </div>
    {% if 'disqus' in extensions and type == 'page' %}
        {{ include: disqus_script }}
    {% endif %}
 </body>
</html>'''.strip()

entry = r'''
<div class="posting">
    <div class="postheader">
        <h1 class="subject">
            <a href="{{ url }}">{{ title }}</a>
        </h1>
        <span class="date">{{ date.strftime("%d.%m.%Y, %H:%M") }}</span>
    </div>
    <div class="postbody">        
        {{ content }}
    </div>
    <div class="postfooter">
        {% if 'disqus' in extensions and type == 'page' %}
            <a href="{{ url }}#disqus_thread">Kommentieren</a>
        {% endif %}
    </div>
    <div class="comments">
        {% if 'disqus' in extensions and type == 'item' %}
            {{ include: disqus_thread }}
        {% endif %}
    </div>
</div>'''.strip()

kafka = '''
---
title: Die Verwandlung
author: Franz Kafka
identifier: kafka
---

Und er kam - und das schon zu spät - und traute seinen Augen nicht mehr.

Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in
seinem Bett zu einem ungeheueren Ungeziefer verwandelt. Er lag auf seinem
panzerartig harten Rücken und sah, wenn er den Kopf ein wenig hob, seinen
gewölbten, braunen, von bogenförmigen Versteifungen geteilten Bauch, auf
dessen Höhe sich die Bettdecke, zum gänzlichen Niedergleiten bereit, kaum noch
erhalten konnte. Seine vielen, im Vergleich zu seinem sonstigen Umfang
kläglich dünnen Beine flimmerten ihm hilflos vor den Augen.

»Was ist mit mir geschehen?« dachte er. Es war kein Traum, sein Zimmer, ein
richtiges, nur etwas zu kleines Menschenzimmer, lag ruhig zwischen den vier
wohlbekannten Wänden, über dem Tisch, auf dem eine auseinandergepackte
Musterkollektion von Tuchwaren ausgebreitet war - Samsa war Reisender -, hing
das Bild, das er vor kurzem aus einer illustrierten Zeitschrift ausgeschnitten
und in einem hübschen, vergoldeten Rahmen untergebracht hatte. Es stellte eine
Dame dar, die, mit einem Pelzhut und einer Pelzboa versehen, aufrecht dasaß
und einen schweren Pelzmuff, in dem ihr ganzer Unterarm verschwunden war, dem
Beschauer entgegenhob.'''.strip()