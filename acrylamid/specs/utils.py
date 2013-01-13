# -*- coding: utf-8 -*-

import attest
from acrylamid.utils import Metadata


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
