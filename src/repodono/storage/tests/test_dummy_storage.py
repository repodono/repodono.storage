# -*- coding: utf-8 -*-
from os.path import join
from os.path import dirname
from zope.component import getUtility
from zope.interface import alsoProvides

from repodono.storage.interfaces import IStorage
from repodono.storage.interfaces import IStorageEnabled
from repodono.storage.interfaces import IStorageFactory
from repodono.storage.interfaces import IStorageBackend
from repodono.storage.interfaces import IStorageInstaller

from repodono.storage.testing import REPODONO_DUMMY_STORAGE_INTEGRATION_TESTING
from repodono.storage.testing import storage
from repodono.storage.testing.storage import DummyStorage
from repodono.storage.testing.storage import DummyStorageBackend

import unittest

path = lambda p: join(dirname(storage.__file__), 'data', p)


class DummyStorageTestCase(unittest.TestCase):

    def setUp(self):
        self.backend = DummyStorageBackend()

    def tearDown(self):
        pass

    def test_loader(self):
        self.backend.load_dir('test', path('testrepo'))
        self.assertEqual(self.backend._data, {'test': [
            {'file1': 'file1-rev0\nThis is a test file.\n',
             'file2': 'file2-rev0\nThis is also a test file.\n'},
            {'file1': 'file1-rev1\nThis test file has changed.\n',
             'file2': 'file2-rev0\nThis is also a test file.\n',
             'file3': 'A new test file.\n'},
            {'dir1/f1': 'File 1 in dir1\n',
             'dir1/f2': 'File 2 in dir1\n',
             'file2': 'file2-rev0\nThis is also a test file.\n',
             'file3': 'This is to note that file1 was removed.\n'},
            {'dir1/dir2/f1': 'first file in dir1\n',
             'dir1/dir2/f2': 'second file in dir2\n',
             'dir1/dir3/dir4/dir5/info': 'This is some quite nested file.\n',
             'dir1/f1': 'File 1 in dir1\n',
             'dir1/f2': 'File 2 in dir1\n',
             'file1': 'file2-rev0\nThis is also a test file.\n',
             'file3': 'This is to note that file1 was removed.\n'}
        ]})


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
