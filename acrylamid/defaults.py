#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import sys
import os
import logging
import hashlib

from os.path import exists, isfile, isdir, join, dirname

log = logging.getLogger('acrylamid.defaults')


def md5(fp):
    h = hashlib.md5()
    while True:
        chunks = fp.read(128)
        if chunks:
            h.update(chunks)
        else:
            break
    return h.digest()


def init(root='.', overwrite=False):

    global default

    default['output_dir'] = default.get('output_dir', 'output').rstrip('/')
    default['entries_dir'] = default.get('entries_dir', 'content').rstrip('/')
    default['layout_dir'] = default.get('layout_dir', 'layouts').rstrip('/')

    dirs = ['%(entries_dir)s/', '%(layout_dir)s/', '%(output_dir)s/']
    files = {'conf.py': confstring,
             '%(output_dir)s/blog.css' % default: css,
             '%(layout_dir)s/base.html' % default: base,
             '%(layout_dir)s/main.html' % default: main,
             '%(layout_dir)s/entry.html' % default: entry,
             '%(layout_dir)s/articles.html' % default: articles,
             '%(entries_dir)s/sample entry.txt' % default: kafka}

    # restore a given file from defaults
    # XXX works only for default sub-folders
    if root.replace('./', '') in files:
        if isfile(root):
            with open(root) as fp:
                old = md5(fp)
            content = files[root.replace('./', '')]
            if hashlib.md5(content).digest() != old:
                q = raw_input('re-initialize %r? [yn]: ' % root)
                if q == 'y':
                    with open(root, 'w') as fp:
                        fp.write(content)
                    log.info('re-initialized %s' % root)
            else:
                log.info('skip  %s is identical', root)
        else:
            q = raw_input('re-create %r? [yn]: ' % root)
            if q == 'y':
                if not isdir(dirname(root)):
                    try:
                        os.makedirs(dirname(root))
                    except OSError:
                        pass
                with open(root, 'w') as fp:
                    fp.write(files[root.replace('./', '')])
                log.info('create %s' % root)

        sys.exit(0)

    # YO DAWG I HERD U LIEK BLOGS SO WE PUT A BLOG IN UR BLOG -- ask user before
    if isfile('conf.py'):
        q = raw_input("Create blog inside a blog? [yn]: ")
        if q != 'y':
            sys.exit(1)

    if exists(root) and len(os.listdir(root)) > 0:
        q = raw_input("Destination directory not empty! Continue? [yn]: ")
        if q != 'y':
            sys.exit(1)

    if root != '.' and not exists(root):
        os.mkdir(root)

    for directory in dirs:
        directory = join(root, directory % default)
        if exists(directory) and not isdir(directory):
            log.critical('Unable to create %r. Please remove this file', directory)
            sys.exit(1)
        elif not exists(directory):
            os.mkdir(directory)

    for path, content in sorted(files.iteritems(), key=lambda k: k[0]):
        path = join(root, path % default)
        if exists(path) and not isfile(path):
            log.critical('%r must be a regular file' % path)
            sys.exit(1)
        elif not exists(path) or overwrite == True:
            with open(path, 'w') as fp:
                fp.write(content)
            log.info('create  %s', path)
        else:
            log.info('skip  %s already exists', path)
    log.info('Created your fresh new blog at %r. Enjoy!', root)


def check_conf(conf):
    """Rudimentary conf checking.  Currently every *_dir except
    `ext_dir` (it's a list of dirs) is checked wether it exists."""

    # directories
    for key, value in conf.iteritems():
        if key.endswith('_dir') and not key in ['ext_dir', ]:
            if os.path.exists(value):
                if os.path.isdir(value):
                    pass
                else:
                    log.error("'%s' must be a directory" % value)
                    sys.exit(1)
            else:
                os.mkdir(value)
                log.warning('%s created...' % value)

    return True


conf = default = {
    'sitename': 'A descriptive blog title',
    'author': 'Anonymous',
    'email': 'info@example.com',
    'lang': 'de_DE',
    'date_format': '%d.%m.%Y, %H:%M',
    'encoding': 'utf-8',
    'permalink_format': '/:year/:slug/',
    'output_ignore': ['blog.css', 'img/*', 'images/*'],

    'filters': ['markdown+codehilite(css_class=highlight)', 'hyphenate'],
    'views': {
        '/': {
            'view': 'index',
            'pagination': '/page/:num',
            'filters': ['summarize', 'h1'],
        },
        '/:year/:slug/': {
            'view': 'entry',
            'filters': ['h1'],
        },
        '/atom/index.html': {
            'view': 'atom',
            'filters': ['h2'],
        },
        '/rss/': {'filters': ['h2'], 'view': 'rss'},
        '/articles/': {'view': 'articles'}
    }
}


confstring = """
# -*- encoding: utf-8 -*-
# This is your config file.  Please write in a valid python syntax!
# See http://acrylamid.readthedocs.org/en/latest/conf.py.html

SITENAME = "A descriptive blog title"
WWW_ROOT = "http://example.com/"

AUTHOR = "Anonymous"
EMAIL = "info@example.org"

FILTERS = ["markdown+codehilite(css_class=highlight)", "hyphenate"]
VIEWS = {
    "/": {"filters": ["summarize", "h1"],
          "pagination": "/page/:num",
          "view": "index"},
    "/:year/:slug/": {"filters": ["h1"], "view": "entry"},
    "/atom/": {"filters": ["h2"], "view": "atom"},
    "/rss/": {"filters": ["h2"], "view": "rss"},
    "/articles/": {"view": "articles"},
    #"/atom/full": {"filters": ["h2"], "view": "atom", "num_entries": 1000},
    "/tag/:name/": {"filters": ["h1", "summarize"], "view":"tag",
                   "pagination": "/tag/:name/:num"},
    }

PERMALINK_FORMAT = "/:year/:slug/index.html"
DATE_FORMAT = "%d.%m.%Y, %H:%M"
""".strip()


css = '''
@import url(pygments.css);
body {
  background-color: white; }

#blogheader {
  margin-bottom: 10px;
  padding: 10px;
  font-family: Palatino, "Times New Roman", serif;
  text-decoration: none;
  text-align: center; }
  #blogheader #blogtitle h2 {
    padding-top: 1.5em; }
    #blogheader #blogtitle h2 a {
      color: black;
      text-decoration: none; }
  #blogheader #mainlinks {
    padding: 1em; }
    #blogheader #mainlinks li {
      display: inline-block;
      margin: 0 2em 0 2em; }
    #blogheader #mainlinks a {
      color: black;
      text-decoration: none;
      font-family: Palatino, "Times New Roman", serif; }
      #blogheader #mainlinks a:hover {
        text-shadow: #888888 0px 0px 1px; }

#blogbody {
  margin: 0 auto;
  width: 800px; }
  #blogbody .posting {
    padding: 1em;
    margin-top: 64px;
    margin-bottom: 64px; }
    #blogbody .posting .postheader .subject {
      margin-bottom: -0.7em; }
      #blogbody .posting .postheader .subject a {
        color: black;
        font: bold medium Palatino, "Times New Roman";
        text-decoration: none; }
        #blogbody .posting .postheader .subject a:hover {
          text-shadow: #aaaaaa 0px 0px 2px; }
    #blogbody .posting .postheader .date {
      font: 0.7em "Georgia";
      float: right; }
    #blogbody .posting .postbody {
      text-align: justify;
      padding: 1em;
      font-family: Palatino, "Times New Roman", serif;
      font-size: 11pt; }
      #blogbody .posting .postbody h2 {
        font: 12pt Palatino, "Times New Roman", serif;
        font-weight: bold;
        color: #888888;
        border-bottom: 1px dotted #888888; }
      #blogbody .posting .postbody h3, #blogbody .posting .postbody h4 {
        font: 12pt Palatino, "Times New Roman", serif;
        font-weight: bold;
        color: #888888;
        padding-left: 4px; }
      #blogbody .posting .postbody a {
        text-decoration: none;
        color: #cc0000; }
        #blogbody .posting .postbody a:visited {
          color: #aa0000; }
        #blogbody .posting .postbody a:hover {
          color: #ff190d;
          text-shadow: #ff6666 0px 0px 1px; }
      #blogbody .posting .postbody p {
        line-height: 1.3em; }
      #blogbody .posting .postbody dl {
        padding-left: 16px; }
        #blogbody .posting .postbody dl dt {
          font-weight: bold;
          color: #444444;
          padding: 6px 92px 3px 0;
          padding-top: 9px; }
      #blogbody .posting .postbody ul {
        padding: 10px 0 10px 40px;
        list-style-type: disc; }
      #blogbody .posting .postbody li {
        padding-top: 3px; }
      #blogbody .posting .postbody pre, #blogbody .posting .postbody code {
        font-family: Bitstream Vera Sans Mono, monospace;
        font-size: 13px; }
      #blogbody .posting .postbody blockquote {
        border-left: 3pt solid #aaaaaa;
        padding-left: 1em;
        padding-right: 1em;
        margin-left: 1em;
        font: italic small Verdana, Times, sans-serif;
        color: #222222; }
        #blogbody .posting .postbody blockquote em {
          font-weight: bold; }
      #blogbody .posting .postbody img {
        max-width: 700px;
        margin: 0em 20px;
        -moz-box-shadow: 0px 0px 9px black;
        -webkit-box-shadow: 0px 0px 9px black;
        box-shadow: 0px 0px 4px black; }
      #blogbody .posting .postbody .amp {
        color: #666666;
        font-family: "Warnock Pro", "Goudy Old Style", "Palatino", "Book Antiqua", serif;
        font-style: italic; }
      #blogbody .posting .postbody .caps {
        font-size: 0.92em; }
      #blogbody .posting .postbody .highlight {
        border: 1px solid #cccccc;
        padding-left: 1em;
        margin-bottom: 10px;
        margin-top: 10px;
        background: none repeat scroll 0 0 #f0f0f0;
        overflow: auto; }
    #blogbody .posting .postfooter p {
      margin: 0 0 0 0;
      font-style: italic; }
    #blogbody .posting .postfooter a {
      color: #111111;
      font-family: Palatino, "times new roman", serif;
      font-weight: bold;
      font-size: 0.9em;
      text-decoration: none; }
      #blogbody .posting .postfooter a:hover {
        color: #111111;
        text-shadow: #aaaaaa 0px 0px 1px; }
  #blogbody .page {
    margin-top: -20px;
    font: bold medium Palatino, "Times New Roman", serif;
    color: black;
    text-decoration: none;
    border-bottom: 1px dotted black; }
    #blogbody .page:hover {
      text-shadow: #aaaaaa 0px 0px 1px; }

#blogfooter {
  margin-top: 10px;
  padding: 10px;
  text-align: center;
  font: medium Palatino, "Times New Roman", serif; }
  #blogfooter a {
    font-weight: bold;
    text-decoration: none;
    border-bottom: 1px dotted black;
    color: #cc0000; }
    #blogfooter a:hover {
      text-shadow: #ee6688 0px 0px 1px;
      color: #ff190d; }

#disqus_thread {
  padding-top: 24px; }

object[type="application/x-shockwave-flash"] {
  -moz-box-shadow: 0px 0px 12px #777777;
  -webkit-box-shadow: 0px 0px 12px #777777;
  box-shadow: 0px 0px 12px #777777;
  margin-left: 15px;
  text-align: center; }

.shadow {
  -moz-box-shadow: 0px 0px 9px black;
  -webkit-box-shadow: 0px 0px 9px black;
  box-shadow: 0px 0px 4px black; }

.floatright {
  float: right; }

.floatleft {
  float: left; }
'''.strip()

base = r'''
<!DOCTYPE html
  PUBLIC "-//W3C//DTD XHTML 1.1 plus MathML 2.0//EN"
         "http://www.w3.org/Math/DTD/mathml2/xhtml-math11-f.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    {% block head -%}
    <title>{% block title %}{% endblock %}</title>
    <meta http-equiv="Content-Type" content="text/xhtml; charset=utf-8" />
    <meta http-equiv="content-language" content="de, en" />
    <link media="all" href="{{ path + '/blog.css' }}" type="text/css" rel="stylesheet" />
    <link href="/favicon.ico" rel="shortcut icon" />
    <link href="{{ path + '/' }}" rel="home" />
    <link href="{{ path + '/atom/' }}" type="application/atom+xml" rel="alternate" title="Atom-Feed" />
    <link href="{{ path + '/rss/' }}" type="application/rss+xml" rel="alternate" title="RSS-Feed" />
    {%- endblock %}
</head>
<body>
    <div id="blogheader">
        <div id="blogtitle">
            <h2><a href="{{ path + '/' }}" class="blogtitle">{{ sitename }}</a></h2>
        </div>
        <div id="mainlinks">
            <ul>
                <li><a href="{{ path + '/' }}">blog</a></li>
                <li><a href="{{ path + '/atom/' }}">atom</a></li>
                <li><a href="{{ path + '/rss/' }}">rss</a></li>
                <li><a href="{{ path + '/articles/' }}">articles</a></li>
            </ul>
        </div>
    </div>
    <div id="blogbody">
        {% block content -%}
        {%- endblock %}
    </div>
    <div id="blogfooter">
        {% block footer %}
        <p>written by <a href="mailto:{{ email }}">{{ author }}</a></p>
        <a href="http://creativecommons.org/licenses/by-nc-sa/2.0/de/" rel="copyright">
            <img src="/img/cc.png" alt="by-nc-sa" />
        </a>
        {% endblock %}
    </div>
 </body>
</html>'''.rstrip()

main = r'''
{% extends "base.html" %}

{% block title %}
    {%- if type != 'item' -%}
      {{ sitename }}
    {%- else -%}
      {{ title }}
    {%- endif -%}
{% endblock %}

{% block head %}
    {{- super() }}
    {%- if type == 'item' %}
    <meta name="description" content="{{ description }}" />
    <meta name="keywords" content="{{ tags | join(', ') }}" />
    {%- endif -%}
{% endblock %}

{% block content %}
    {{ entrylist }}
    {% if type in ['tag', 'page'] %}
        {% if prev %}
            <a href="{{ path + prev }}" class="page floatright">
            ältere Beiträge →
            </a>
        {% endif %}
        {% if next %}
            <a href="{{ path + next }}" class="page floatleft">
            ← neuere Beiträge
            </a>
        {% endif %}
    {%- endif  %}
{% endblock %}

{% block footer %}
    {{ super() }}
    {% if disqus_shortname and type == 'page' %}
        <script type="text/javascript">
            /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
            var disqus_shortname = '{{ disqus_shortname }}'; // required: replace example with your forum shortname

            /* * * DON'T EDIT BELOW THIS LINE * * */
            (function () {
                var s = document.createElement('script'); s.async = true;
                s.type = 'text/javascript';
                s.src = '{{ protocol }}://' + disqus_shortname + '.disqus.com/count.js';
                (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s);
            }());
        </script>
        {% endif %}
{% endblock %}
'''.strip()

entry = r'''
<div class="posting">
    <div class="postheader">
        <h1 class="subject">
            <a href="{{ path + permalink }}">{{ title }}</a>
        </h1>
        <span class="date">{{ date.strftime("%d.%m.%Y, %H:%M") }}</span>
    </div>
    <div class="postbody">
        {{ content }}
    </div>
    <div class="postfooter">
        {% if disqus_shortname and type == 'page' %}
            <a class="floatright" href="{{ www_root + permalink }}#disqus_thread">Kommentieren</a>
        {% endif %}
        {% if tags %}
            <p>verschlagwortet als
                {% for link in tags | tagify -%}
                    <a href="{{ path + link.href }}">{{ link.title }}</a>
                    {%- if loop.revindex > 2 -%}
                    ,
                    {%- elif loop.revindex == 2 %}
                    und
                    {% endif %}
                {% endfor %}
            </p>
        {% elif not draft %}
            <p>nicht verschlagwortet</p>
        {% endif %}
    </div>
    <div class="comments">
        {%- if disqus_shortname and type == 'item' and not draft %}
        <div id="disqus_thread"></div>
        <script type="text/javascript">
            var disqus_shortname = '{{ disqus_shortname }}'; // required: replace example with your forum shortname

            // The following are highly recommended additional parameters. Remove the slashes in front to use.
            var disqus_identifier = "{{ www_root + permalink }}";
            var disqus_url = "{{ www_root + permalink }}";

            /* * * DON'T EDIT BELOW THIS LINE * * */
            (function() {
                var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
                dsq.src = '{{ protocol }}://' + disqus_shortname + '.disqus.com/embed.js';
                (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
            })();
        </script>
        <noscript>
            <p>Please enable JavaScript to view the <a href="{{ protocol }}://disqus.com/?ref_noscript">comments powered by Disqus.</a></p>
        </noscript>
        <a href="{{ protocol }}://disqus.com" class="dsq-brlink">
            blog comments powered by <span class="logo-disqus">Disqus</span>
        </a>
        {% endif -%}
    </div>
</div>'''.strip()

articles = r'''
{% extends "base.html" %}

{% block title %}{{ sitename }} – Artikelübersicht{% endblock %}

{% block content %}
    <div class="posting">
        <div class="postheader">
            <span class="date">{{ num_entries }} Beiträge</span>
        </div>
        <div class="postbody">
            {% for year in articles|sort(reverse=True) %}
            <h2>{{ year }}</h2>
            <ul>
                {% for entry in articles[year] %}
                    <li>
                        <span>{{ entry[0].strftime('%d.%m.%Y: ') }}</span>
                        <a href="{{ entry[1]}}">{{ entry[2] | e }}</a>
                    </li>
                {% endfor %}
            </ul>
            {% endfor %}
        </div>
    </div>
{% endblock %}
'''.strip()

kafka = '''
---
title: Die Verwandlung
date: 13.12.2011, 23:42
tags: [Franz Kafka, Die Verwandlung]
---

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
Musterkollektion von Tuchwaren ausgebreitet war -- Samsa war Reisender --, hing
das Bild, das er vor kurzem aus einer illustrierten Zeitschrift ausgeschnitten
und in einem hübschen, vergoldeten Rahmen untergebracht hatte. Es stellte eine
Dame dar, die, mit einem Pelzhut und einer Pelzboa versehen, aufrecht dasaß
und einen schweren Pelzmuff, in dem ihr ganzer Unterarm verschwunden war, dem
Beschauer entgegenhob.'''.strip()
