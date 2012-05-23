# -*- coding: utf-8 -*-

import konira
import tempfile

from datetime import datetime

from acrylamid import log, errors
from acrylamid.helpers import escape
from acrylamid.base import Entry
from acrylamid.defaults import conf
from acrylamid.errors import AcrylamidException

log.init('acrylamid', level=40)

def create(path, **kwargs):

    with open(path, 'w') as fp:
        fp.write('---\n')
        for k, v in kwargs.iteritems():
            if isinstance(v, basestring):
                v = escape(v)
            fp.write('%s: %s\n' % (k, v))
        fp.write('---\n')


describe 'Entry':

    before all:
        fd, path = tempfile.mkstemp(suffix='.txt')
        self.path = path

    it "handles dates":

        create(self.path, date='13.02.2011, 15:36', title='bla')
        date = Entry(self.path, conf).date

        assert date.year == 2011
        assert date.month == 2
        assert date.day == 13
        assert date == datetime(year=2011, month=2, day=13, hour=15, minute=36)

    it "should parse alternate date format strings":

        create(self.path, date='1.2.2034', title='bla')
        date = Entry(self.path, conf).date

        assert date.year == 2034
        assert date.month == 2
        assert date.day == 1
        assert date == datetime(year=2034, month=2, day=1)

    it "raises an exception on invalid date strings":

        create(self.path, date='unparsable', title='bla')
        raises AcrylamidException: Entry(self.path, conf).date

    it "has a permalink property":

        create(self.path, title='foo')
        entry = Entry(self.path, conf)

        assert entry.permalink == '/2012/foo/'

        create(self.path, title='foo', permalink='/hello/world/')
        entry = Entry(self.path, conf)

        assert entry.permalink == '/hello/world/'

        create(self.path, title='foo', permalink_format='/:year/:slug/index.html')
        entry = Entry(self.path, conf)

        assert entry.permalink == '/2012/foo/'

    it "handles tags":

        create(self.path, title='foo', tags='Foo')
        assert Entry(self.path, conf).tags == ['Foo']

        create(self.path, title='foo', tags='[Foo, Bar]')
        assert Entry(self.path, conf).tags == ['Foo', 'Bar']

    it "remaps deprecated keys":

        create(self.path, title='foo', tag=None, filter=None)
        entry = Entry(self.path, conf)

        assert 'tags' in entry
        assert 'filters' in entry

    it "can has also custom key value pairs":

        create(self.path, title='foo', image='/img/test.png')
        entry = Entry(self.path, conf)

        assert 'image' in entry
        assert entry.image == '/img/test.png'

    it "defines fallbacks":

        create(self.path, title='Bla')
        entry = Entry(self.path, conf)

        assert entry.draft == False
        assert entry.email == 'info@example.com'
        assert entry.author == 'Anonymous'
        assert entry.extension == 'txt'
        assert entry.year == datetime.now().year
        assert entry.month == datetime.now().month
        assert entry.day == datetime.now().day
