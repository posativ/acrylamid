# -*- coding: utf-8 -*-

import sys; reload(sys)
sys.setdefaultencoding('utf-8')

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA

import tempfile
from datetime import datetime

from acrylamid import log, errors
from acrylamid.helpers import FileEntry, escape
from acrylamid.defaults import conf

log.init('acrylamid', level=40)


def create(path, **kwargs):

    with open(path, 'w') as fp:
        fp.write('---\n')
        for k, v in kwargs.iteritems():
            if isinstance(v, basestring):
                v = escape(v)
            fp.write('%s: %s\n' % (k, v))
        fp.write('---\n')


class TestFileEntry(unittest.TestCase):

    def setUp(self):
        fd, path = tempfile.mkstemp(suffix='.txt')
        self.path = path

    def test_date1(self):

        create(self.path, date='13.02.2011, 15:36')
        date = FileEntry(self.path, conf).date

        self.assertEquals(date.year, 2011)
        self.assertEquals(date.month, 2)
        self.assertEquals(date.day, 13)
        self.assertEquals(date, datetime(year=2011, month=2, day=13, hour=15, minute=36))

    def test_date2(self):

        create(self.path, date='1.2.2034')
        date = FileEntry(self.path, conf).date

        self.assertEquals(date.year, 2034)
        self.assertEquals(date.month, 2)
        self.assertEquals(date.day, 1)
        self.assertEquals(date, datetime(year=2034, month=2, day=1))

    def test_date3(self):

        create(self.path, date='unparsable')

        with self.assertRaises(errors.AcrylamidException):
            date = FileEntry(self.path, conf).date

    def test_permalink(self):

        create(self.path, title='foo')
        entry = FileEntry(self.path, conf)

        self.assertEquals(entry.permalink, '/2012/foo/')

        create(self.path, title='foo', permalink='/hello/world/')
        entry = FileEntry(self.path, conf)

        self.assertEquals(entry.permalink, '/hello/world/')

        create(self.path, title='foo', permalink_format='/:year/:slug/index.html')
        entry = FileEntry(self.path, conf)

        self.assertEquals(entry.permalink, '/2012/foo/')

    def test_tags(self):

        create(self.path, title='foo', tags='Foo')
        self.assertEquals(FileEntry(self.path, conf).tags, ['Foo'])

        create(self.path, title='foo', tags='[Foo, Bar]')
        self.assertEquals(FileEntry(self.path, conf).tags, ['Foo', 'Bar'])

    def test_mapping(self):

        create(self.path, title='foo', tag=None, filter=None)
        entry = FileEntry(self.path, conf)

        self.assertTrue('tags' in entry)
        self.assertTrue('filters' in entry)

    def test_fallback(self):

        create(self.path)
        entry = FileEntry(self.path, conf)

        self.assertEquals(entry.title, 'No Title!')
        self.assertEquals(entry.draft, False)
        self.assertEquals(entry.email, 'info@example.com')
        self.assertEquals(entry.author, 'Anonymous')
        self.assertEquals(entry.extension, 'txt')
        self.assertEquals(entry.year, datetime.now().year)
        self.assertEquals(entry.month, datetime.now().month)
        self.assertEquals(entry.day, datetime.now().day)
