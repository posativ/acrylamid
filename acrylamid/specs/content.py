# -*- coding: utf-8 -*-

import os
import attest

from os.path import join, isfile

from acrylamid import core, log, utils, helpers
from acrylamid.commands import compile
from acrylamid.defaults import conf

# supress warnings
log.init('acrylamid', 40)
options = type('Options', (object, ), {
    'ignore': False, 'force': False, 'dryrun': False, 'parser': 'compile'})


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


class SingleEntry(attest.TestBase):

    @classmethod
    def __context__(self):
        with attest.tempdir() as path:

            self.path = path
            os.chdir(self.path)
            os.mkdir('content/')
            os.mkdir('layouts/')

            with open('layouts/main.html', 'w') as fp:
                fp.write('{{ env.entrylist[0].content }}\n')

            self.conf = core.Configuration(conf)
            self.env = core.Environment({'options': options, 'globals': utils.Struct()})

            self.conf['filters'] = ['HTML']
            self.conf['views'] = {'/:year/:slug/': {'view': 'entry'}}
            yield

    @attest.test_if(helpers.translitcodec is not None)
    def exists_at_permalink(self):
        with open('content/bla.txt', 'w') as fp:
            fp.write(entry())

        compile(self.conf, self.env)
        assert isfile(join('output/', '2012', 'haensel-and-gretel', 'index.html'))

    @attest.test
    def renders_custom_permalink(self):
        with open('content/bla.txt', 'w') as fp:
            fp.write(entry(permalink='/about/me.asp'))

        compile(self.conf, self.env)
        assert isfile(join('output/', 'about', 'me.asp'))

    @attest.test
    def appends_index(self):
        with open('content/bla.txt', 'w') as fp:
            fp.write(entry(permalink='/about/me/'))

        compile(self.conf, self.env)
        assert isfile(join('output/', 'about', 'me', 'index.html'))

    @attest.test
    def plaintext(self):
        with open('content/bla.txt', 'w') as fp:
            fp.write(entry(permalink='/'))

        compile(self.conf, self.env)

        expected = '# Test\n\nThis is supercalifragilisticexpialidocious.'
        assert open('output/index.html').read() == expected

    @attest.test
    def markdown(self):
        with open('content/bla.txt', 'w') as fp:
            fp.write(entry(permalink='/', filter='[Markdown]'))

        compile(self.conf, self.env)

        expected = '<h1>Test</h1>\n<p>This is supercalifragilisticexpialidocious.</p>'
        assert open('output/index.html').read() == expected

    @attest.test
    def fullchain(self):
        with open('content/bla.txt', 'w') as fp:
            fp.write(entry(permalink='/', filter='[Markdown, h1, hyphenate]', lang='en'))

        compile(self.conf, self.env)

        expected = ('<h2>Test</h2>\n<p>This is su&shy;per&shy;cal&shy;ifrag&shy;'
                    'ilis&shy;tic&shy;ex&shy;pi&shy;ali&shy;do&shy;cious.</p>')
        assert open('output/index.html').read() == expected


class MultipleEntries(attest.TestBase):

    @classmethod
    def __context__(self):
        with attest.tempdir() as path:
            self.path = path

            os.chdir(self.path)
            os.mkdir('content/')
            os.mkdir('layouts/')

            with open('layouts/main.html', 'w') as fp:
                fp.write('{{ env.entrylist[0].content }}\n')

            with open('layouts/atom.xml', 'w') as fp:
                fp.write("{% for entry in env.entrylist %}\n{{ entry.content ~ '\n' }}\n{% endfor %}")

            self.conf = core.Configuration(conf)
            self.env = core.Environment({'options': options, 'globals': utils.Struct()})

            self.conf['filters'] = ['Markdown', 'h1']
            self.conf['views'] = {'/:year/:slug/': {'view': 'entry'},
                                  '/atom.xml': {'view': 'Atom', 'filters': ['h2', 'summarize+2']}}
            yield

    @attest.test
    def markdown(self):
        with open('content/foo.txt', 'w') as fp:
            fp.write(entry(title='Foo'))
        with open('content/bar.txt', 'w') as fp:
            fp.write(entry(title='Bar'))

        compile(self.conf, self.env)

        expected = '<h2>Test</h2>\n<p>This is supercalifragilisticexpialidocious.</p>'
        assert open('output/2012/foo/index.html').read() == expected
        assert open('output/2012/bar/index.html').read() == expected
