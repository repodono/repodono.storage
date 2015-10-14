# -*- coding: utf-8 -*-
from zope.component import getUtility

from repodono.storage.interfaces import IStorage
from repodono.storage.interfaces import IStorageFactory
from repodono.storage.interfaces import IStorageInstaller

from repodono.storage.testing import REPODONO_DUMMY_STORAGE_INTEGRATION_TESTING
# from repodono.storage.testing.storage import DummyStorage

import unittest


class DummyStorageTestCase(unittest.TestCase):

    layer = REPODONO_DUMMY_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_adapt_fail(self):
        self.assertRaises(TypeError, IStorage, self.portal)

    def test_storage_lifecycle(self):
        installer = getUtility(IStorageInstaller)
        installer(self.portal, 'dummy_backend')

        sf = IStorageFactory(self.portal)
        self.assertEqual(sf.backend, u'dummy_backend')

        # acquire storage
        # storage = storage_backend.acquire(self.portal)
        # storage = IStorage(self.portal)
        # self.assertTrue(isinstance(storage, DummyStorage))
