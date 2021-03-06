# -*- coding: utf-8 -*-
import shutil
import tempfile
import os.path

from zope.interface import alsoProvides
from zope.component import getUtility
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.annotation.interfaces import IAnnotations
from plone.registry.interfaces import IRegistry

from repodono.registry.interfaces import IUtilityRegistry
from repodono.storage.interfaces import IStorageBackend
from repodono.storage.interfaces import IStorageEnabled
from repodono.storage.interfaces import IStorageFactory
from repodono.storage.interfaces import IStorageInfo
from repodono.storage.base import BaseStorageBackend
from repodono.storage.base import BaseStorage
from repodono.storage.base import DefaultStorageBackendFSAdapter

from plone.app.contenttypes.tests.robot.variables import TEST_FOLDER_ID

from repodono.storage.testing import REPODONO_STORAGE_INTEGRATION_TESTING
from repodono.storage.testing import storage

import unittest


class BaseDefaultTestCase(unittest.TestCase):

    def test_default_backend_impl(self):
        # default data, no annotation
        backend = BaseStorageBackend()
        self.assertRaises(NotImplementedError, backend.acquire, None)
        self.assertRaises(NotImplementedError, backend.install, None)

    def test_default_storage_impl(self):
        # default data, no real context.
        storage = BaseStorage(None)
        self.assertRaises(NotImplementedError, storage.basename, None)
        self.assertRaises(NotImplementedError, storage.checkout, None)
        self.assertRaises(NotImplementedError, storage.file, None)
        self.assertRaises(NotImplementedError, storage.files)
        self.assertRaises(NotImplementedError, storage.listdir, None)
        self.assertRaises(NotImplementedError, storage.log, None, None)
        self.assertRaises(NotImplementedError, storage.pathinfo, None)

    def test_storage_datefmt(self):
        storage = BaseStorage(None)
        self.assertEqual(storage.datefmt, 'iso8601')
        iso8601 = storage.datefmtstr
        self.assertTrue(iso8601.startswith('%Y'))

        storage.datefmt = 'rfc2822'
        self.assertEqual(storage.datefmt, 'rfc2822')
        self.assertTrue(storage.datefmtstr.startswith('%a'))

        with self.assertRaises(ValueError):
            storage.datefmt = 'invalid'

        self.assertEqual(storage.datefmt, 'rfc2822')

        # Defaults back to default iso8601
        storage._datefmt = 'invalid'
        self.assertEqual(storage.datefmtstr, iso8601)


class StorageFactoryTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal.get(TEST_FOLDER_ID)

    def test_not_enabled_fail(self):
        with self.assertRaises(TypeError):
            IStorageFactory(self.folder)

    def test_default_impl_no_backend(self):
        alsoProvides(self.folder, IStorageEnabled)
        sf = IStorageFactory(self.folder)
        with self.assertRaises(ConstraintNotSatisfied):
            sf.backend = u'test'


class StorageFactoryRegisteredTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        # Register a dummy backend
        self.portal = self.layer['portal']
        self.folder = self.portal.get(TEST_FOLDER_ID)
        self.backend = storage.DummyStorageBackend()
        self.portal.getSiteManager().registerUtility(
            self.backend, provided=IStorageBackend, name=u'dummy_a')
        self.portal.getSiteManager().registerUtility(
            self.backend, provided=IStorageBackend, name=u'dummy_b')

        utilities = getUtility(IUtilityRegistry, 'repodono.storage.backends')
        utilities.enable('dummy_a')
        utilities.enable('dummy_b')

    def tearDown(self):
        self.portal.getSiteManager().unregisterUtility(
            self.backend, provided=IStorageBackend, name=u'dummy_a')
        self.portal.getSiteManager().unregisterUtility(
            self.backend, provided=IStorageBackend, name=u'dummy_b')

    def test_default_impl_readonly(self):
        alsoProvides(self.folder, IStorageEnabled)
        sf = IStorageFactory(self.folder)
        sf.backend = u'dummy_a'
        self.assertEqual(sf.backend, u'dummy_a')

        with self.assertRaises(ValueError) as cm:
            sf.backend = u'dummy_b'

        self.assertEqual(cm.exception.args, ('backend', 'field is readonly'))


class StorageInfoTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal.get(TEST_FOLDER_ID)

    def test_storage_info_annotation_success(self):
        # default data, no annotation
        storage_info = IStorageInfo(self.folder)
        self.assertIsNone(storage_info.path)
        storage_info.path = u'Some Path'

        self.assertIn(
            'repodono.storage.base.StorageInfo',
            IAnnotations(self.folder).keys())


class DefaultStorageBackendFSAdapterTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal.get(TEST_FOLDER_ID)
        self.tempdir = unicode(tempfile.mkdtemp())
        reg = getUtility(IRegistry)
        reg['repodono.storage.backend_root'] = self.tempdir

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_basics(self):
        d = DefaultStorageBackendFSAdapter(None, self.portal)
        self.assertEqual(d.get_root(), self.tempdir)
        self.assertEqual(d._get_path(), os.path.join(self.tempdir, 'plone'))

        target_dir = os.path.join(self.tempdir, 'plone', TEST_FOLDER_ID)
        d = DefaultStorageBackendFSAdapter(None, self.folder)
        self.assertEqual(d._get_path(), target_dir)

    def test_install_default(self):
        target_dir = os.path.join(self.tempdir, 'plone', TEST_FOLDER_ID)
        d = DefaultStorageBackendFSAdapter(None, self.folder)
        d.install()

        self.assertEqual(IStorageInfo(self.folder).path, target_dir)
        self.assertTrue(os.path.exists(target_dir))

    def test_install_multiple_ignored(self):
        target_dir = os.path.join(self.tempdir, 'plone', TEST_FOLDER_ID)
        d = DefaultStorageBackendFSAdapter(None, self.folder)
        d.install()
        d.install()

        self.assertEqual(IStorageInfo(self.folder).path, target_dir)
        self.assertTrue(os.path.exists(target_dir))

    def test_install_exists(self):
        # create blocking dir.
        os.makedirs(os.path.join(self.tempdir, 'plone', TEST_FOLDER_ID))

        target_dir = os.path.join(self.tempdir, 'plone', TEST_FOLDER_ID + '-1')
        d = DefaultStorageBackendFSAdapter(None, self.folder)
        d.install()
        self.assertEqual(IStorageInfo(self.folder).path, target_dir)
        self.assertTrue(os.path.exists(target_dir))

        # doesn't go ahead and create extra directories.
        self.assertFalse(os.path.exists(
            os.path.join(self.tempdir, 'plone', TEST_FOLDER_ID + '-2')))

    def test_acquire_failure(self):
        d = DefaultStorageBackendFSAdapter(None, self.folder)
        with self.assertRaises(ValueError):
            d.acquire()

    def test_acquire_success(self):
        d = DefaultStorageBackendFSAdapter(None, self.folder)
        d.install()

        target_dir = os.path.join(self.tempdir, 'plone', TEST_FOLDER_ID)
        self.assertEqual(IStorageInfo(self.folder).path, target_dir)
        self.assertEqual(d.acquire(), target_dir)

        # remove the target dir.
        shutil.rmtree(target_dir)
        with self.assertRaises(ValueError):
            d.acquire()

    def test__find_next_path(self):
        d = DefaultStorageBackendFSAdapter(None, self.folder)
        names = [
            'a', 'b', 'c', 'c-1', 'c-1-1', 'c-12-1', 'c-1-2', 'c-1-2a', 'c-2',
            'c-1-3', 'c-1-5', 'd-1', 'e', 'cd-11111', 'b-1',
        ]
        self.assertEqual(d._find_next_path(names, 'a'), 'a-1')
        self.assertEqual(d._find_next_path(names, 'b'), 'b-2')
        self.assertEqual(d._find_next_path(names, 'c-1'), 'c-1-6')
        self.assertEqual(d._find_next_path(names, 'c-12'), 'c-12-2')
        self.assertEqual(d._find_next_path(names, 'c-12-1'), 'c-12-1-1')
        self.assertEqual(d._find_next_path(names, 'cd'), 'cd-11112')

    def test__makedirs(self):
        target_dir = os.path.join(self.tempdir, 'dummy')
        d = DefaultStorageBackendFSAdapter(None, self.folder)
        self.assertFalse(os.path.exists(target_dir))
        d._makedirs(target_dir)
        self.assertTrue(os.path.exists(target_dir))

        self.assertFalse(os.path.exists(target_dir + '-1'))
        d._makedirs(target_dir)
        self.assertTrue(os.path.exists(target_dir + '-1'))

        self.assertFalse(os.path.exists(target_dir + '-2'))
        d._makedirs(target_dir)
        self.assertTrue(os.path.exists(target_dir + '-2'))

        self.assertFalse(os.path.exists(target_dir + '-3'))
        d._makedirs(target_dir)
        self.assertTrue(os.path.exists(target_dir + '-3'))

        d.makedir_retry = 0
        with self.assertRaises(ValueError):
            d._makedirs(target_dir)

        self.assertFalse(os.path.exists(target_dir + '-a'))
        d._makedirs(target_dir + '-a')
        self.assertTrue(os.path.exists(target_dir + '-a'))
