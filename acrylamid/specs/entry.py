# -*- coding: utf-8 -*-

import tempfile
import attest

from datetime import datetime

from acrylamid import log
from acrylamid.errors import AcrylamidException

from acrylamid.readers import Entry
from acrylamid.helpers import safe
from acrylamid.defaults import conf

log.init('acrylamid', level=40)
conf['entry_permalink'] = '/:year/:slug/'

def create(path, **kwargs):

    with open(path, 'w') as fp:
        fp.write('---\n')
        for k, v in kwargs.iteritems():
            fp.write('%s: %s\n' % (k, v))
        fp.write('---\n')


class TestEntry(attest.TestBase):

    def __context__(self):
        fd, self.path = tempfile.mkstemp(suffix='.txt')
        yield

    @attest.test
    def dates(self):

        create(self.path, date='13.02.2011, 15:36', title='bla')
        date = Entry(self.path, conf).date.replace(tzinfo=None)

        assert date.year == 2011
        assert date.month == 2
        assert date.day == 13
        assert date == datetime(year=2011, month=2, day=13, hour=15, minute=36)

    @attest.test
    def alternate_dates(self):

        create(self.path, date='1.2.2034', title='bla')
        date = Entry(self.path, conf).date.replace(tzinfo=None)

        assert date.year == 2034
        assert date.month == 2
        assert date.day == 1
        assert date == datetime(year=2034, month=2, day=1)

    @attest.test
    def invalid_dates(self):

        create(self.path, date='unparsable', title='bla')
        with attest.raises(AcrylamidException):
            Entry(self.path, conf).date

    @attest.test
    def permalink(self):

        create(self.path, title='foo')
        entry = Entry(self.path, conf)

        assert entry.permalink == '/2012/foo/'

        create(self.path, title='foo', permalink='/hello/world/')
        entry = Entry(self.path, conf)

        assert entry.permalink == '/hello/world/'

        create(self.path, title='foo', permalink_format='/:year/:slug/index.html')
        entry = Entry(self.path, conf)

        assert entry.permalink == '/2012/foo/'

    @attest.test
    def tags(self):

        create(self.path, title='foo', tags='Foo')
        assert Entry(self.path, conf).tags == ['Foo']

        create(self.path, title='foo', tags='[Foo, Bar]')
        assert Entry(self.path, conf).tags == ['Foo', 'Bar']

    @attest.test
    def deprecated_keys(self):

        create(self.path, title='foo', tag=None, filter=None)
        entry = Entry(self.path, conf)

        assert 'tags' in entry
        assert 'filters' in entry

    @attest.test
    def custom_values(self):

        create(self.path, title='foo', image='/img/test.png')
        entry = Entry(self.path, conf)

        assert 'image' in entry
        assert entry.image == '/img/test.png'

    @attest.test
    def fallbacks(self):

        create(self.path, title='Bla')
        entry = Entry(self.path, conf)

        assert entry.draft == False
        assert entry.email == 'info@example.com'
        assert entry.author == 'Anonymous'
        assert entry.extension == 'txt'
        assert entry.year == datetime.now().year
        assert entry.imonth == datetime.now().month
        assert entry.iday == datetime.now().day
