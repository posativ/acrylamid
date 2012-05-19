# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA


from acrylamid.utils import NestedProperties

class TestUtils(unittest.TestCase):

    def test_nestedprops(self):

        dct = NestedProperties()
        dct['hello.world'] = 1

        self.assertEquals(dct['hello']['world'], 1)
        self.assertEquals(dct.hello.world, 1)

        try:
            dct.foo
            dct.foo.bar
        except KeyError:
            assert True
        else:
            assert False

        dct['hello.foreigner'] = 2

        self.assertEquals(dct['hello']['world'], 1)
        self.assertEquals(dct.hello.world, 1)

        self.assertEquals(dct.hello.foreigner, 2)
