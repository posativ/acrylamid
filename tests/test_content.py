# -*- coding: utf-8 -*-

import sys; reload(sys)
sys.setdefaultencoding('utf-8')

import unittest # NOQA
import tempfile
import shutil
import os

from os.path import join, isfile, isdir

from acrylamid import Environment, log
from acrylamid.commands import initialize, compile
from acrylamid.defaults import conf

# supress warnings
log.init('acrylamid', 40)
options = type('Options', (object, ), {'ignore': False})


def entry(**kw):

    L = [('title', 'Hänsel and Gretel!'),
         ('date', '12.02.2012 15:46')]

    res = ['---']

    for k, v in L:
        if k not in kw:
            res.append('%s: %s' % (k, v))
    for k, v in kw.iteritems():
        res.append('%s: %s' % (k, v))

    res.append('---')
    res.append('')
    res.append('# Test')
    res.append('')
    res.append('This is supercalifragilisticexpialidocious.')

    return '\n'.join(res)


class TestSingleEntry(unittest.TestCase):

    def setUp(self):

        self.path = tempfile.mkdtemp(dir='.')
        os.chdir(self.path)
        os.mkdir('content/')
        os.mkdir('layouts/')

        with open('layouts/main.html', 'wb') as fp:
            fp.write('{{ env.entrylist[0].content }}\n')

        self.conf = conf
        self.env = Environment({'options': options})

        self.conf['filters'] = ['HTML']
        self.conf['views'] = {'/:year/:slug/': {'view': 'entry'}}


    def test_auto_permalink(self):
        with open('content/bla.txt', 'wb') as fp:
            fp.write(entry())

        compile(self.conf, self.env, options)
        assert isfile(join('output/', '2012', 'haensel-and-gretel', 'index.html'))

    def test_custom_permalink(self):
        with open('content/bla.txt', 'wb') as fp:
            fp.write(entry(permalink='/about/me.asp'))

        compile(self.conf, self.env, options)
        assert isfile(join('output/', 'about', 'me.asp'))

    def test_custom_dir_permalink(self):
        with open('content/bla.txt', 'wb') as fp:
            fp.write(entry(permalink='/about/me/'))

        compile(self.conf, self.env, options)
        assert isfile(join('output/', 'about', 'me', 'index.html'))

    def test_content_plain(self):
        with open('content/bla.txt', 'wb') as fp:
            fp.write(entry(permalink='/'))

        compile(self.conf, self.env, options)

        expected = '# Test\n\nThis is supercalifragilisticexpialidocious.'
        self.assertEqual(open('output/index.html').read(), expected)

    def test_content_minimal(self):
        with open('content/bla.txt', 'wb') as fp:
            fp.write(entry(permalink='/', filter='[Markdown]'))

        compile(self.conf, self.env, options)

        expected = '<h1>Test</h1>\n<p>This is supercalifragilisticexpialidocious.</p>'
        self.assertEqual(open('output/index.html').read(), expected)

    def test_content_full(self):
        with open('content/bla.txt', 'wb') as fp:
            fp.write(entry(permalink='/', filter='[Markdown, h1, hyphenate]', lang='en'))

        compile(self.conf, self.env, options)

        expected = ('<h2>Test</h2>\n<p>This is su&shy;per&shy;cal&shy;ifrag&shy;'
                    'ilis&shy;tic&shy;ex&shy;pi&shy;ali&shy;do&shy;cious.</p>')
        self.assertEqual(open('output/index.html').read(), expected)

    def tearDown(self):
        os.chdir('../')
        shutil.rmtree(self.path)


class TestMultipleEntries(unittest.TestCase):

    def setUp(self):

        self.path = tempfile.mkdtemp(dir='.')
        os.chdir(self.path)
        os.mkdir('content/')
        os.mkdir('layouts/')

        with open('layouts/main.html', 'wb') as fp:
            fp.write('{{ env.entrylist[0].content }}\n')

        with open('layouts/atom.xml', 'wb') as fp:
            fp.write("{% for entry in env.entrylist %}\n{{ entry.content ~ '\n' }}\n{% endfor %}")

        self.conf = conf
        self.env = Environment({'options': options})

        self.conf['filters'] = ['Markdown', 'h1']
        self.conf['views'] = {'/:year/:slug/': {'view': 'entry'},
                              '/atom.xml': {'view': 'Atom', 'filters': ['h2', 'summarize+2']}}

    def test_simple_markdown(self):
        with open('content/foo.txt', 'wb') as fp:
            fp.write(entry(title='Foo'))
        with open('content/bar.txt', 'wb') as fp:
            fp.write(entry(title='Bar'))

        compile(self.conf, self.env, options)

        expected = '<h2>Test</h2>\n<p>This is supercalifragilisticexpialidocious.</p>'
        self.assertEqual(open('output/2012/foo/index.html').read(), expected)
        self.assertEqual(open('output/2012/bar/index.html').read(), expected)

    def tearDown(self):
        os.chdir('../')
        shutil.rmtree(self.path)
