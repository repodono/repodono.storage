# -*- coding: utf-8 -*-
import unittest
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from repodono.storage.interfaces import IStorageRegistry
from repodono.storage.testing import REPODONO_STORAGE_INTEGRATION_TESTING


class RegistryTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def test_set_registry(self):
        # Basic registry test case, the actual values and uses are
        # rather coupled to the features that these registry entries
        # enable.
        registry = getUtility(IRegistry)
        registry['repodono.storage.backend_root'] = u'/tmp'
        self.assertEqual(
            registry['repodono.storage.backend_root'], u'/tmp')
        proxy = registry.forInterface(
            IStorageRegistry, prefix='repodono.storage')
        self.assertEqual(proxy.backend_root, u'/tmp')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RegistryTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
