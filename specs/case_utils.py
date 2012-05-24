# -*- coding: utf-8 -*-

from acrylamid.utils import NestedProperties

describe "Nested Properties":

    it "works as expected":

        dct = NestedProperties()
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
