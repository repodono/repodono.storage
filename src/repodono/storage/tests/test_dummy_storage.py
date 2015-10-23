# -*- coding: utf-8 -*-
from os.path import join
from os.path import dirname
from zope.component import getUtility
from zope.interface import alsoProvides

from plone.dexterity.content import Item

from repodono.storage.exceptions import PathNotFoundError
from repodono.storage.exceptions import RevisionNotFoundError
from repodono.storage.exceptions import StorageNotFoundError

from repodono.storage.interfaces import IStorage
from repodono.storage.interfaces import IStorageEnabled
from repodono.storage.interfaces import IStorageFactory
from repodono.storage.interfaces import IStorageBackend
from repodono.storage.interfaces import IStorageInstaller

from repodono.storage.testing import REPODONO_DUMMY_STORAGE_INTEGRATION_TESTING
from repodono.storage.testing import storage
from repodono.storage.testing.storage import DummyStorage
from repodono.storage.testing.storage import DummyStorageBackend
from repodono.storage.testing.storage import DummyStorageData

import unittest

path = lambda p: join(dirname(storage.__file__), 'data', p)


class DummyStorageBackendTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.backend = DummyStorageBackend()

    def tearDown(self):
        DummyStorageData.teardown()

    def test_teardown(self):
        orig = self.backend._data
        self.assertIs(orig, DummyStorageData._data)
        self.backend.install(Item(id='testdummy'))
        self.assertIn('testdummy', DummyStorageData._data)
        DummyStorageData.teardown()
        self.assertIs(orig, DummyStorageData._data)
        self.assertNotIn('testdummy', DummyStorageData._data)

    def test_backend_loader(self):
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


class DummyStorageTestCase(unittest.TestCase):

    def setUp(self):
        self.backend = DummyStorageBackend()
        self.backend.load_dir('dummy_a', path('testrepo'))

    def tearDown(self):
        DummyStorageData.teardown()

    def test_acquire_fail(self):
        item = Item(id='not_installed')
        self.assertRaises(StorageNotFoundError, self.backend.acquire, item)

    def test_acquire_basic(self):
        item = Item(id='dummy_a')
        storage = self.backend.acquire(item)
        self.assertEqual(item, storage.context)
        self.assertEqual(storage.rev, '3')
        self.assertEqual(
            storage.file('file1'), 'file2-rev0\nThis is also a test file.\n')
        self.assertEqual(
            storage.file('dir1/dir2/f2'), 'second file in dir2\n')
        self.assertEqual(storage.files(), [
            'dir1/dir2/f1', 'dir1/dir2/f2', 'dir1/dir3/dir4/dir5/info',
            'dir1/f1', 'dir1/f2', 'file1', 'file3',
        ])

        self.assertEqual(storage.basename('dir1/dir3/dir4/dir5/info'), 'info')
        self.assertEqual(storage.listdir(''), ['dir1', 'file1', 'file3'])
        self.assertEqual(storage.listdir('dir1'), ['dir2', 'dir3', 'f1', 'f2'])
        self.assertEqual(storage.listdir('dir1/dir2'), ['f1', 'f2'])

        with self.assertRaises(PathNotFoundError):
            storage.listdir('dir1/no/such/dir')

        # this implementation will raise an error if trying to access a
        # file as directory.

        with self.assertRaises(PathNotDirError):
            storage.listdir('file1')

        storage.checkout('0')
        self.assertEqual(storage.rev, '0')
        self.assertEqual(
            storage.file('file1'), 'file1-rev0\nThis is a test file.\n')
        self.assertEqual(storage.files(), ['file1', 'file2'])
        self.assertEqual(storage.listdir(''), ['file1', 'file2'])

        with self.assertRaises(PathNotFoundError):
            storage.listdir('dir1')

    def test_bad_revision(self):
        item = Item(id='dummy_a')
        storage = self.backend.acquire(item)
        self.assertRaises(RevisionNotFoundError, storage.checkout, '123')
        self.assertRaises(RevisionNotFoundError, storage.checkout, 'abc')
        self.assertRaises(RevisionNotFoundError, storage.checkout, '4')
        self.assertRaises(RevisionNotFoundError, storage.checkout, 3)

    def test_bad_path(self):
        item = Item(id='dummy_a')
        storage = self.backend.acquire(item)
        with self.assertRaises(PathNotFoundError):
            storage.file('no/such/path')


class DummyStorageIntegrationTestCase(unittest.TestCase):

    layer = REPODONO_DUMMY_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def tearDown(self):
        DummyStorageData.teardown()

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

        self.assertEqual(DummyStorageData._data.keys(), ['plone'])

        sf = IStorageFactory(self.portal)
        self.assertEqual(sf.backend, u'dummy_backend')

        storage_backend = getUtility(IStorageBackend, name=u'dummy_backend')
        storage = storage_backend.acquire(self.portal)
        self.assertTrue(isinstance(storage, DummyStorage))

        storage = IStorage(self.portal)
        self.assertTrue(isinstance(storage, DummyStorage))
