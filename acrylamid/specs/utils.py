# -*- coding: utf-8 -*-

from acrylamid.utils import Metadata, groupby, neighborhood

import attest
tt = attest.Tests()


class TestMetadata(attest.TestBase):

    @attest.test
    def works(self):

        dct = Metadata()
        dct['hello.world'] = 1

        assert dct['hello']['world'] == 1
        assert dct.hello.world == 1

        try:
            dct.foo
            dct.foo.bar
        except KeyError:
            assert True
        else:
            assert False

        dct['hello.foreigner'] = 2

        assert dct['hello']['world'] == 1
        assert dct.hello.world == 1

        assert dct.hello.foreigner == 2

    @attest.test
    def redirects(self):

        dct = Metadata()
        alist = [1, 2, 3]

        dct['foo'] = alist
        dct.redirect('foo', 'baz')

        assert 'foo' not in dct
        assert 'baz' in dct
        assert dct['baz'] == alist


    @attest.test
    def update(self):

        dct = Metadata()
        dct.update({'hello.world': 1})

        assert 'hello' in dct
        assert dct.hello.world == 1

    @attest.test
    def init(self):
        assert Metadata({'hello.world': 1}).hello.world == 1


@tt.test
def neighbors():

    assert list(neighborhood([1, 2, 3])) == \
        [(None, 1, 2), (1, 2, 3), (2, 3, None)]
