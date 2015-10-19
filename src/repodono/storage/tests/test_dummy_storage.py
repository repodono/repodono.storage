# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.interface import alsoProvides

from repodono.storage.interfaces import IStorage
from repodono.storage.interfaces import IStorageEnabled
from repodono.storage.interfaces import IStorageFactory
from repodono.storage.interfaces import IStorageBackend
from repodono.storage.interfaces import IStorageInstaller

from repodono.storage.testing import REPODONO_DUMMY_STORAGE_INTEGRATION_TESTING
from repodono.storage.testing.storage import DummyStorage

import unittest


class DummyStorageIntegrationTestCase(unittest.TestCase):

    layer = REPODONO_DUMMY_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_adapt_fail(self):
        self.assertRaises(TypeError, IStorage, self.portal)

    def test_install_not_enabled_fail(self):
        installer = getUtility(IStorageInstaller)
        with self.assertRaises(TypeError):
            installer(self.portal, 'dummy_backend')

    def test_storage_lifecycle(self):
        # have to mark the object manually with IStorageEnabled.
        # Normally dexterity behavior will provide this.
        alsoProvides(self.portal, IStorageEnabled)

        installer = getUtility(IStorageInstaller)
        installer(self.portal, 'dummy_backend')

        sf = IStorageFactory(self.portal)
        self.assertEqual(sf.backend, u'dummy_backend')

        storage_backend = getUtility(IStorageBackend, name=u'dummy_backend')
        storage = storage_backend.acquire(self.portal)
        self.assertTrue(isinstance(storage, DummyStorage))

        storage = IStorage(self.portal)
        self.assertTrue(isinstance(storage, DummyStorage))
