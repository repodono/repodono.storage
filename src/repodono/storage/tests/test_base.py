# -*- coding: utf-8 -*-
from zope.interface import alsoProvides
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.annotation.interfaces import IAnnotations
from repodono.storage.interfaces import IStorageBackend
from repodono.storage.interfaces import IStorageEnabled
from repodono.storage.interfaces import IStorageFactory
from repodono.storage.interfaces import IStorageInfo
from repodono.storage.base import BaseStorageBackend
from repodono.storage.base import BaseStorage

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
