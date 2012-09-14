# -*- encoding: utf-8 -*-

from acrylamid.defaults import copy

def rollout(engine):

    return 'shadowplay', {
        'conf.py': 'conf.py',
        'content/': [
            'content/about.txt', 'content/lorem.txt',
            'content/ipsum.txt', 'content/shadowplay.txt'
        ],
        'shadowplay/': [
            'shadowplay.css',
            'base.html', 'main.html', 'entry.html', 'articles.html',
            copy('jinja2/atom.xml'),
            copy('jinja2/rss.xml')
        ],
        'shadowplay/img/': [
            'img/arrow.png', 'img/back.png', 'img/link.png', 'img/logo.png'
        ]
    }
