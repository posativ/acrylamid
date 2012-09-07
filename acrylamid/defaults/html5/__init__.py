# -*- encoding: utf-8 -*-

from acrylamid.defaults import copy


def rollout(engine):

    return 'theme', {
        'content/sample-entry.txt': copy('sample-entry.txt'),
        'theme/': [
            'base.html',
            'main.html',
            'entry.html',
            'articles.html',
            copy(engine + '/atom.xml'),
            copy(engine + '/rss.xml'),
            copy('html5/style.css')],
    }
