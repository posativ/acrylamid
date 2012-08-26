# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import tempfile

from datetime import datetime

from acrylamid import log, errors
from acrylamid.errors import AcrylamidException

from acrylamid.readers import Entry
from acrylamid.helpers import safe
from acrylamid.defaults import conf

log.init('acrylamid', level=40)

def create(path, **kwargs):

    with open(path, 'w') as fp:
        fp.write('---\n')
        for k, v in kwargs.iteritems():
            if isinstance(v, basestring):
                v = safe(v)
            fp.write('%s: %s\n' % (k, v))
        fp.write('---\n')


class TestEntry(unittest.TestCase):

    @classmethod
    def setup_class(self):
        fd, path = tempfile.mkstemp(suffix='.txt')
        self.path = path

    def test_dates(self):

        create(self.path, date='13.02.2011, 15:36', title='bla')
        date = Entry(self.path, conf).date

        assert date.year == 2011
        assert date.month == 2
        assert date.day == 13
        assert date == datetime(year=2011, month=2, day=13, hour=15, minute=36)

    def test_alternate_dates(self):

        create(self.path, date='1.2.2034', title='bla')
        date = Entry(self.path, conf).date

        assert date.year == 2034
        assert date.month == 2
        assert date.day == 1
        assert date == datetime(year=2034, month=2, day=1)

    def test_invalid_dates(self):

        create(self.path, date='unparsable', title='bla')
        with self.assertRaises(AcrylamidException):
            Entry(self.path, conf).date

    def test_permalink(self):

        create(self.path, title='foo')
        entry = Entry(self.path, conf)

        assert entry.permalink == '/2012/foo/'

        create(self.path, title='foo', permalink='/hello/world/')
        entry = Entry(self.path, conf)

        assert entry.permalink == '/hello/world/'

        create(self.path, title='foo', permalink_format='/:year/:slug/index.html')
        entry = Entry(self.path, conf)

        assert entry.permalink == '/2012/foo/'

    def test_tags(self):

        create(self.path, title='foo', tags='Foo')
        assert Entry(self.path, conf).tags == ['Foo']

        create(self.path, title='foo', tags='[Foo, Bar]')
        assert Entry(self.path, conf).tags == ['Foo', 'Bar']

    def test_deprecated_keys(self):

        create(self.path, title='foo', tag=None, filter=None)
        entry = Entry(self.path, conf)

        assert 'tags' in entry
        assert 'filters' in entry

    def test_custom_values(self):

        create(self.path, title='foo', image='/img/test.png')
        entry = Entry(self.path, conf)

        assert 'image' in entry
        assert entry.image == '/img/test.png'

    def test_fallbacks(self):

        create(self.path, title='Bla')
        entry = Entry(self.path, conf)

        assert entry.draft == False
        assert entry.email == 'info@example.com'
        assert entry.author == 'Anonymous'
        assert entry.extension == 'txt'
        assert entry.year == datetime.now().year
        assert entry.month == datetime.now().month
        assert entry.day == datetime.now().day
